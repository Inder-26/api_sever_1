import uuid
import time
import logging
import threading
from typing import Optional, Tuple, List
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

logger = logging.getLogger("catalog_worker")

MAX_RETRIES = 3
RETRY_DELAYS = [2, 4, 8]
STUCK_JOB_TIMEOUT = 300  # 5 minutes


class CatalogWorker:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self._jobs = {}
        self._batches = {}
        self._idempotency = {}
        self._lock = threading.Lock()
        self._backfill = {"status": "idle"}
        self._backfill_stop = False
        logger.info("CatalogWorker initialized (in-memory mode)")

    # ── Idempotency ────────────────────────────────────────────

    def check_idempotency(self, key: str) -> Optional[str]:
        return self._idempotency.get(key)

    # ── Job/Batch Creation ─────────────────────────────────────

    def create_batch(self, idempotency_key: str, s3_urls: list) -> dict:
        existing = self.check_idempotency(idempotency_key)
        if existing:
            return self.get_batch_status(existing)

        batch_id = f"batch_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()
        jobs = []

        with self._lock:
            for s3_url in s3_urls:
                job_id = f"job_{uuid.uuid4().hex[:12]}"
                self._jobs[job_id] = {
                    "job_id": job_id,
                    "batch_id": batch_id,
                    "image_s3_url": s3_url,
                    "status": "pending",
                    "retries": 0,
                    "result": None,
                    "error": None,
                    "created_at": now,
                    "updated_at": now,
                }
                jobs.append({"job_id": job_id, "status": "queued"})

            self._batches[batch_id] = {
                "batch_id": batch_id,
                "job_ids": [j["job_id"] for j in jobs],
                "total": len(jobs),
                "created_at": now,
            }
            self._idempotency[idempotency_key] = batch_id

        return {
            "batch_id": batch_id,
            "jobs": jobs,
            "total": len(jobs),
            "message": f"{len(jobs)} images queued for processing",
        }

    def create_single_job(self, s3_url: str) -> dict:
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "batch_id": None,
                "image_s3_url": s3_url,
                "status": "pending",
                "retries": 0,
                "result": None,
                "error": None,
                "created_at": now,
                "updated_at": now,
            }

        return {"job_id": job_id, "status": "queued"}

    # ── Status Queries ─────────────────────────────────────────

    def get_job_status(self, job_id: str) -> Optional[dict]:
        return self._jobs.get(job_id)

    def get_batch_status(self, batch_id: str) -> Optional[dict]:
        batch = self._batches.get(batch_id)
        if not batch:
            return None

        jobs = []
        counts = {"completed": 0, "failed": 0, "pending": 0, "processing": 0}
        for jid in batch["job_ids"]:
            job = self._jobs.get(jid, {})
            status = job.get("status", "unknown")
            if status in ("pending", "queued"):
                counts["pending"] += 1
            elif status in counts:
                counts[status] += 1
            jobs.append(job)

        return {
            "batch_id": batch_id,
            "total": batch["total"],
            **counts,
            "jobs": jobs,
        }

    def get_queue_counts(self) -> dict:
        pending = sum(1 for j in self._jobs.values() if j["status"] == "pending")
        processing = sum(1 for j in self._jobs.values() if j["status"] == "processing")
        return {"queue_pending": pending, "queue_processing": processing}

    # ── Worker Loop ────────────────────────────────────────────

    def process_next_job(self) -> bool:
        """Pick and process the next pending job. Returns True if a job was processed."""
        job_id = None
        with self._lock:
            for jid, job in self._jobs.items():
                if job["status"] == "pending":
                    job_id = jid
                    job["status"] = "processing"
                    job["updated_at"] = datetime.now(timezone.utc).isoformat()
                    break

        if not job_id:
            return False

        job = self._jobs[job_id]
        s3_url = job["image_s3_url"]

        try:
            bucket, key = parse_s3_url(s3_url)
            result = self.pipeline.process_single_image(s3_url, bucket, key, job_id)

            with self._lock:
                job["status"] = "completed"
                job["result"] = result
                job["updated_at"] = datetime.now(timezone.utc).isoformat()

            logger.info(f"Job {job_id} completed: {result.get('decision')}")

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            with self._lock:
                job["retries"] += 1
                if job["retries"] < MAX_RETRIES:
                    job["status"] = "pending"
                    delay = RETRY_DELAYS[job["retries"] - 1]
                    logger.info(f"Job {job_id} will retry in {delay}s (attempt {job['retries']})")
                    time.sleep(delay)
                else:
                    job["status"] = "failed"
                    job["error"] = str(e)
                job["updated_at"] = datetime.now(timezone.utc).isoformat()

        return True

    def start_worker_loop(self, poll_interval: float = 2.0) -> None:
        def loop():
            logger.info(f"Worker loop started (poll every {poll_interval}s)")
            while True:
                try:
                    processed = self.process_next_job()
                    if not processed:
                        time.sleep(poll_interval)
                except Exception as e:
                    logger.error(f"Worker loop error: {e}")
                    time.sleep(poll_interval)

        t = threading.Thread(target=loop, daemon=True)
        t.start()

    def start_timeout_monitor(self, check_interval: float = 120.0) -> None:
        def monitor():
            logger.info(f"Timeout monitor started (check every {check_interval}s)")
            while True:
                time.sleep(check_interval)
                try:
                    now = datetime.now(timezone.utc)
                    with self._lock:
                        for job in self._jobs.values():
                            if job["status"] != "processing":
                                continue
                            updated = datetime.fromisoformat(job["updated_at"])
                            if (now - updated).total_seconds() > STUCK_JOB_TIMEOUT:
                                job["retries"] += 1
                                if job["retries"] >= MAX_RETRIES:
                                    job["status"] = "failed"
                                    job["error"] = "Timeout after multiple retries"
                                else:
                                    job["status"] = "pending"
                                job["updated_at"] = now.isoformat()
                                logger.warning(
                                    f"Reset stuck job {job['job_id']} "
                                    f"(retries: {job['retries']})"
                                )
                except Exception as e:
                    logger.error(f"Timeout monitor error: {e}")

        t = threading.Thread(target=monitor, daemon=True)
        t.start()


    # ── Backfill ────────────────────────────────────────────────

    def start_backfill(
        self, s3_keys: list, bucket: str, workers: int = 4, resume: bool = False
    ) -> dict:
        """Start backfill of existing S3 images into the catalog.
        Runs in background thread with parallel workers.
        If resume=True, pre-filters already-indexed images so only unprocessed ones run.
        """
        if self._backfill["status"] == "running":
            return {"error": "Backfill already running", **self._backfill}

        # Pre-filter: remove images already in the catalog
        skipped = 0
        if resume:
            logger.info("Resume mode: fetching already-indexed URLs from DB...")
            indexed_urls = self.pipeline.db.get_all_indexed_s3_urls()
            original_count = len(s3_keys)
            s3_keys = [
                k for k in s3_keys
                if f"https://{bucket}.s3.amazonaws.com/{k}" not in indexed_urls
            ]
            skipped = original_count - len(s3_keys)
            logger.info(
                f"Resume: {skipped} already indexed, {len(s3_keys)} remaining to process"
            )

        self._backfill = {
            "status": "running",
            "total": len(s3_keys),
            "skipped_already_indexed": skipped,
            "processed": 0,
            "new_products": 0,
            "merged": 0,
            "duplicates": 0,
            "reviews": 0,
            "failed": 0,
            "errors": [],
            "workers": workers,
            "resumed": resume,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "finished_at": None,
        }

        if not s3_keys:
            self._backfill["status"] = "completed"
            self._backfill["finished_at"] = datetime.now(timezone.utc).isoformat()
            return self._backfill

        self._backfill_stop = False
        bf_lock = threading.Lock()

        def process_one(i, key):
            """Process a single image. Returns decision string."""
            if self._backfill_stop:
                return "stopped"
            try:
                s3_url = f"https://{bucket}.s3.amazonaws.com/{key}"

                # Safety net: skip if somehow already indexed (e.g. race condition)
                existing = self.pipeline.db.find_by_s3_url(s3_url)
                if existing:
                    return "duplicate_skip"

                result = self.pipeline.process_single_image(
                    s3_url, bucket, key, job_id=f"backfill_{i}"
                )
                return result.get("decision", "unknown")

            except Exception as e:
                if len(self._backfill["errors"]) < 20:
                    self._backfill["errors"].append(f"{key}: {str(e)}")
                logger.error(f"Backfill failed for {key}: {e}")
                return "failed"

        def run():
            bf = self._backfill
            pbar = tqdm(total=len(s3_keys), desc="Backfill", unit="img")

            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = {}
                for i, key in enumerate(s3_keys):
                    if self._backfill_stop:
                        break
                    fut = pool.submit(process_one, i, key)
                    futures[fut] = (i, key)

                for fut in as_completed(futures):
                    decision = fut.result()

                    with bf_lock:
                        if decision == "new_product":
                            bf["new_products"] += 1
                        elif decision == "auto_merge":
                            bf["merged"] += 1
                        elif decision in ("phash_duplicate", "duplicate_skip"):
                            bf["duplicates"] += 1
                        elif decision == "review":
                            bf["reviews"] += 1
                        elif decision == "failed":
                            bf["failed"] += 1

                        bf["processed"] += 1
                        pbar.update(1)
                        pbar.set_description(
                            f"Backfill | new={bf['new_products']} merged={bf['merged']} "
                            f"dup={bf['duplicates']} review={bf['reviews']} fail={bf['failed']}"
                        )

            pbar.close()
            if self._backfill_stop:
                bf["status"] = "stopped"
            else:
                bf["status"] = "completed"
            bf["finished_at"] = datetime.now(timezone.utc).isoformat()
            logger.info(f"Backfill completed: {bf}")

        t = threading.Thread(target=run, daemon=True)
        t.start()

        return self._backfill

    def get_backfill_status(self) -> dict:
        return self._backfill


# ── Utility ────────────────────────────────────────────────────

def parse_s3_url(s3_url: str) -> tuple:
    """Parse S3 URL into (bucket, key).
    Handles: https://bucket.s3.amazonaws.com/path/to/file.jpg
    """
    parsed = urlparse(s3_url)
    bucket = parsed.hostname.split(".")[0]
    key = unquote(parsed.path.lstrip("/"))
    return bucket, key
