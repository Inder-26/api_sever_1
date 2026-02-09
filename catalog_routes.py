import io
import uuid
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List

logger = logging.getLogger("catalog_routes")

router = APIRouter(prefix="/catalog", tags=["catalog"])

# Injected by init_catalog_routes() from img_to_csv.py
_db = None
_pipeline = None
_worker = None
_s3 = None
_bucket_map = None

CATALOG_PREFIX = "catalog/"


def init_catalog_routes(db, pipeline, worker, s3_client, bucket_map):
    global _db, _pipeline, _worker, _s3, _bucket_map
    _db = db
    _pipeline = pipeline
    _worker = worker
    _s3 = s3_client
    _bucket_map = bucket_map


# ── Upload Endpoints ───────────────────────────────────────────

@router.post("/upload")
async def upload_single(
    file: UploadFile = File(...),
    website: str = Form("alya"),
):
    """Upload a single image for catalog processing."""
    bucket = _bucket_map.get(website.lower())
    if not bucket:
        raise HTTPException(400, f"Invalid website. Use: {list(_bucket_map.keys())}")

    image_bytes = await file.read()
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    s3_key = f"{CATALOG_PREFIX}{timestamp}_{uuid.uuid4().hex[:8]}.{ext}"

    _s3.put_object(
        Bucket=bucket, Key=s3_key, Body=image_bytes,
        ContentType=file.content_type or "image/jpeg",
    )

    s3_url = f"https://{bucket}.s3.amazonaws.com/{s3_key}"
    job = _worker.create_single_job(s3_url)

    return {"job_id": job["job_id"], "status": "queued", "s3_url": s3_url}


@router.post("/upload-batch")
async def upload_batch(
    files: List[UploadFile] = File(...),
    idempotency_key: str = Form(...),
    website: str = Form("alya"),
):
    """Upload 1-50 images with idempotency."""
    if not 1 <= len(files) <= 50:
        raise HTTPException(400, "Batch size must be 1-50 images")

    bucket = _bucket_map.get(website.lower())
    if not bucket:
        raise HTTPException(400, f"Invalid website. Use: {list(_bucket_map.keys())}")

    # Check idempotency
    existing = _worker.check_idempotency(idempotency_key)
    if existing:
        return _worker.get_batch_status(existing)

    # Upload all files to S3 first
    s3_urls = []
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    for i, f in enumerate(files):
        image_bytes = await f.read()
        ext = f.filename.rsplit(".", 1)[-1] if "." in f.filename else "jpg"
        s3_key = f"{CATALOG_PREFIX}{timestamp}_{i:03d}_{uuid.uuid4().hex[:8]}.{ext}"

        _s3.put_object(
            Bucket=bucket, Key=s3_key, Body=image_bytes,
            ContentType=f.content_type or "image/jpeg",
        )
        s3_urls.append(f"https://{bucket}.s3.amazonaws.com/{s3_key}")

    return _worker.create_batch(idempotency_key, s3_urls)


# ── Process Existing S3 Image ──────────────────────────────────

@router.post("/process")
async def process_existing(
    s3_url: str = Form(...),
):
    """Process an image that's already in S3 (e.g. from /generate_caption).
    No re-upload — just runs catalog matching on the existing URL."""
    job = _worker.create_single_job(s3_url)
    return {"job_id": job["job_id"], "status": "queued", "s3_url": s3_url}


@router.post("/process-batch")
async def process_existing_batch(
    s3_urls: str = Form(...),
    idempotency_key: str = Form(...),
):
    """Process multiple existing S3 URLs (comma-separated).
    No re-upload — just runs catalog matching."""
    urls = [u.strip() for u in s3_urls.split(",") if u.strip()]
    if not 1 <= len(urls) <= 50:
        raise HTTPException(400, "Provide 1-50 comma-separated S3 URLs")

    existing = _worker.check_idempotency(idempotency_key)
    if existing:
        return _worker.get_batch_status(existing)

    return _worker.create_batch(idempotency_key, urls)


# ── Status Endpoints ───────────────────────────────────────────

@router.get("/job/{job_id}")
async def get_job_status(job_id: str):
    job = _worker.get_job_status(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@router.get("/batch/{batch_id}")
async def get_batch_status(batch_id: str):
    batch = _worker.get_batch_status(batch_id)
    if not batch:
        raise HTTPException(404, "Batch not found")
    return batch


# ── Review Endpoints ───────────────────────────────────────────

@router.get("/reviews")
async def get_pending_reviews():
    return _db.get_pending_reviews()


@router.post("/reviews/{review_id}/merge")
async def merge_review(review_id: int, reviewed_by: str = Form("admin")):
    try:
        result = _pipeline.resolve_review_as_merge(review_id, reviewed_by)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/reviews/{review_id}/new")
async def new_from_review(review_id: int, reviewed_by: str = Form("admin")):
    try:
        result = _pipeline.resolve_review_as_new(review_id, reviewed_by)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/reviews/bulk-new")
async def bulk_resolve_as_new(reviewed_by: str = Form("backfill_auto")):
    """Resolve ALL pending reviews as new products in one go."""
    reviews = _db.get_pending_reviews(limit=1000)
    if not reviews:
        return {"message": "No pending reviews", "resolved": 0}

    results = []
    failed = 0
    for r in reviews:
        try:
            result = _pipeline.resolve_review_as_new(r["id"], reviewed_by)
            results.append(result)
        except Exception as e:
            failed += 1
            logger.error(f"Bulk resolve failed for review {r['id']}: {e}")

    return {
        "message": f"Resolved {len(results)} reviews as new products",
        "resolved": len(results),
        "failed": failed,
    }


# ── Product Endpoints ──────────────────────────────────────────

@router.get("/products")
async def list_products(limit: int = 50, offset: int = 0):
    return _db.list_products(limit, offset)


@router.get("/products/{product_id}")
async def get_product(product_id: str):
    product = _db.get_product(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    images = _db.get_images_for_product(product_id)
    return {**product, "images": images}


# ── Reset Endpoint ─────────────────────────────────────────────

@router.post("/reset")
async def reset_catalog(confirm: str = Form(...)):
    """Clear all catalog data (products, images, reviews, logs, centroids).
    Pass confirm='YES_DELETE_ALL' to execute."""
    if confirm != "YES_DELETE_ALL":
        raise HTTPException(400, "Pass confirm='YES_DELETE_ALL' to reset")

    from pymilvus import utility
    conn = _db._get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM decision_logs")
            cur.execute("DELETE FROM review_queue")
            cur.execute("DELETE FROM product_images")
            cur.execute("DELETE FROM products")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _db._put_conn(conn)

    # Drop and recreate Milvus collection
    if "product_centroids" in utility.list_collections():
        utility.drop_collection("product_centroids")
    _pipeline.centroid_collection = _pipeline._init_centroid_collection()

    return {"message": "Catalog reset complete. All data cleared."}


# ── Backfill Endpoints ─────────────────────────────────────────

@router.post("/backfill")
async def start_backfill(
    website: str = Form("alya"),
    exclude_catalog: str = Form("yes"),
    workers: int = Form(4),
):
    """Backfill existing S3 images into the catalog.
    Runs in background — check progress via GET /catalog/backfill.
    exclude_catalog: skip images under catalog/ prefix (already processed).
    """
    from image_search_engine import get_image_paths_from_s3

    bucket = _bucket_map.get(website.lower())
    if not bucket:
        raise HTTPException(400, f"Invalid website. Use: {list(_bucket_map.keys())}")

    # Get all image paths from S3
    all_keys = get_image_paths_from_s3(bucket)

    # Optionally exclude catalog/ prefix images
    if exclude_catalog.lower() == "yes":
        all_keys = [k for k in all_keys if not k.startswith("catalog/")]

    if not all_keys:
        return {"message": "No images found in bucket", "total": 0}

    result = _worker.start_backfill(all_keys, bucket, workers=workers)
    return result


@router.post("/backfill/resume")
async def resume_backfill(
    website: str = Form("alya"),
    exclude_catalog: str = Form("yes"),
    workers: int = Form(4),
):
    """Resume a previously interrupted backfill.
    Skips images already indexed in the catalog DB and only processes the rest.
    """
    from image_search_engine import get_image_paths_from_s3

    bucket = _bucket_map.get(website.lower())
    if not bucket:
        raise HTTPException(400, f"Invalid website. Use: {list(_bucket_map.keys())}")

    all_keys = get_image_paths_from_s3(bucket)

    if exclude_catalog.lower() == "yes":
        all_keys = [k for k in all_keys if not k.startswith("catalog/")]

    if not all_keys:
        return {"message": "No images found in bucket", "total": 0}

    result = _worker.start_backfill(all_keys, bucket, workers=workers, resume=True)
    return result


@router.post("/backfill/stop")
async def stop_backfill():
    """Stop a running backfill."""
    status = _worker.get_backfill_status()
    if status.get("status") != "running":
        raise HTTPException(400, "No backfill is currently running")
    _worker._backfill_stop = True
    return {"message": "Backfill stop signal sent. Check GET /catalog/backfill for status."}


@router.get("/backfill")
async def backfill_status():
    """Check backfill progress."""
    return _worker.get_backfill_status()


# ── System Endpoints ───────────────────────────────────────────

@router.get("/system/metrics")
async def system_metrics():
    db_metrics = _db.get_metrics()
    queue_counts = _worker.get_queue_counts()
    return {
        **db_metrics,
        **queue_counts,
        "worker_mode": "in-memory",
    }
