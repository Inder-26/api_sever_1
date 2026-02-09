import os
import time
import uuid
import logging
import threading
from typing import Optional, Tuple
import numpy as np
import cv2
import imagehash
from PIL import Image
from pymilvus import (
    Collection, FieldSchema, CollectionSchema, DataType, utility
)

from catalog_db import CatalogDB
from image_search_engine import embed_image, load_image_from_s3

logger = logging.getLogger("catalog_pipeline")

# ── Decision Thresholds ────────────────────────────────────────
THRESHOLDS = {
    "auto_merge_clip": 0.90,
    "auto_merge_color": 0.60,
    "auto_merge_gap": 0.01,
    "new_product_clip": 0.90,
}

CENTROID_COLLECTION = "product_centroids"


class CatalogPipeline:
    def __init__(self, db: CatalogDB, clip_model, processor, device, s3_client):
        self.db = db
        self.clip_model = clip_model
        self.processor = processor
        self.device = device
        self.s3 = s3_client
        self._product_lock = threading.Lock()
        self.centroid_collection = self._init_centroid_collection()

    # ── Milvus Collection Setup ────────────────────────────────

    def _init_centroid_collection(self) -> Collection:
        """Create or load the product_centroids Milvus collection.
        Reuses the existing 'default' connection alias — does NOT reconnect.
        """
        if CENTROID_COLLECTION in utility.list_collections():
            col = Collection(name=CENTROID_COLLECTION)
            col.load()
            logger.info(f"Loaded existing Milvus collection: {CENTROID_COLLECTION}")
            return col

        fields = [
            FieldSchema(
                name="product_id", dtype=DataType.VARCHAR,
                is_primary=True, max_length=20
            ),
            FieldSchema(
                name="centroid", dtype=DataType.FLOAT_VECTOR, dim=512
            ),
            FieldSchema(
                name="color_hist", dtype=DataType.FLOAT_VECTOR, dim=180
            ),
            FieldSchema(
                name="image_count", dtype=DataType.INT64
            ),
        ]
        schema = CollectionSchema(fields, description="Product centroid embeddings")
        col = Collection(name=CENTROID_COLLECTION, schema=schema)

        col.create_index(
            field_name="centroid",
            index_params={
                "index_type": "HNSW",
                "params": {"M": 48, "efConstruction": 200},
                "metric_type": "IP",
            },
        )
        col.create_index(
            field_name="color_hist",
            index_params={
                "index_type": "HNSW",
                "params": {"M": 16, "efConstruction": 100},
                "metric_type": "IP",
            },
        )
        col.load()
        logger.info(f"Created Milvus collection: {CENTROID_COLLECTION}")
        return col

    # ── pHash Operations ───────────────────────────────────────

    def calculate_phash(self, pil_image: Image.Image) -> str:
        return str(imagehash.phash(pil_image))

    def check_phash_duplicate(self, phash: str) -> Optional[dict]:
        return self.db.find_by_phash(phash)

    # ── Feature Extraction ─────────────────────────────────────

    def extract_clip_embedding(self, pil_image: Image.Image) -> np.ndarray:
        return embed_image(pil_image, self.clip_model, self.processor, self.device)

    def extract_color_histogram(self, pil_image: Image.Image) -> np.ndarray:
        rgb = np.array(pil_image.convert("RGB"))
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        hist = hist / (hist.sum() + 1e-10)
        return hist.flatten().astype(np.float32)

    def compare_color_histograms(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        return float(np.minimum(hist1, hist2).sum())

    # ── Milvus Centroid Operations ─────────────────────────────

    def search_centroids(self, embedding: np.ndarray, top_k: int = 3) -> list:
        """Search for most similar product centroids.
        Returns list of dicts with product_id, clip_sim, color_hist, image_count.
        IP metric: higher score = more similar (max 1.0 for normalized vectors).
        """
        col = self.centroid_collection
        if col.num_entities == 0:
            return []

        results = col.search(
            data=[embedding.tolist()],
            anns_field="centroid",
            param={"metric_type": "IP", "params": {"ef": 64}},
            limit=top_k,
            output_fields=["product_id", "color_hist", "image_count"],
        )

        matches = []
        for hit in results[0]:
            matches.append({
                "product_id": hit.entity.get("product_id"),
                "clip_sim": float(hit.distance),
                "color_hist": hit.entity.get("color_hist"),
                "image_count": hit.entity.get("image_count"),
            })
        return matches

    def create_centroid(
        self, product_id: str, embedding: np.ndarray, color_hist: np.ndarray
    ) -> None:
        self.centroid_collection.insert([
            [product_id],
            [embedding.tolist()],
            [color_hist.tolist()],
            [1],
        ])
        self.centroid_collection.flush()

    def update_centroid(
        self, product_id: str, new_embedding: np.ndarray, new_color_hist: np.ndarray
    ) -> None:
        """Update centroid with weighted average of existing + new embedding."""
        # Get current centroid
        results = self.centroid_collection.query(
            expr=f'product_id == "{product_id}"',
            output_fields=["centroid", "color_hist", "image_count"],
        )
        if not results:
            logger.error(f"Centroid not found for {product_id}, creating fresh")
            self.create_centroid(product_id, new_embedding, new_color_hist)
            return

        old = results[0]
        old_centroid = np.array(old["centroid"], dtype=np.float32)
        old_color = np.array(old["color_hist"], dtype=np.float32)
        old_count = old["image_count"]

        # Weighted average
        new_centroid = (old_centroid * old_count + new_embedding) / (old_count + 1)
        new_centroid = new_centroid / (np.linalg.norm(new_centroid) + 1e-10)

        new_color = (old_color * old_count + new_color_hist) / (old_count + 1)
        new_color = new_color / (new_color.sum() + 1e-10)

        new_count = old_count + 1

        # Delete old and insert new (pymilvus upsert via delete+insert)
        self.centroid_collection.delete(expr=f'product_id == "{product_id}"')
        self.centroid_collection.insert([
            [product_id],
            [new_centroid.tolist()],
            [new_color.tolist()],
            [new_count],
        ])
        self.centroid_collection.flush()

    # ── Decision Engine ────────────────────────────────────────

    def decide(self, clip_sim: float, color_sim: float, gap: float) -> str:
        if clip_sim < THRESHOLDS["new_product_clip"]:
            return "new_product"
        if (
            clip_sim >= THRESHOLDS["auto_merge_clip"]
            and color_sim >= THRESHOLDS["auto_merge_color"]
            and gap >= THRESHOLDS["auto_merge_gap"]
        ):
            return "auto_merge"
        return "review"

    # ── Main Orchestrator ──────────────────────────────────────

    def process_single_image(
        self, s3_url: str, bucket: str, s3_key: str, job_id: str = None
    ) -> dict:
        start = time.time()

        # 1. Load image
        pil_image = load_image_from_s3(bucket, s3_key)

        # 2. pHash duplicate check
        phash = self.calculate_phash(pil_image)
        dup = self.check_phash_duplicate(phash)
        if dup:
            ms = int((time.time() - start) * 1000)
            self.db.log_decision(
                job_id, s3_url, dup["product_id"], None,
                1.0, 1.0, 1.0, None, ms, "phash_duplicate",
            )
            return {
                "decision": "phash_duplicate",
                "product_id": dup["product_id"],
                "existing_image_id": dup["image_id"],
                "processing_time_ms": ms,
            }

        # 3. Extract features
        clip_emb = self.extract_clip_embedding(pil_image)
        color_hist = self.extract_color_histogram(pil_image)

        # 4. Search centroids
        matches = self.search_centroids(clip_emb, top_k=3)

        # 5. Empty catalog → new product
        if not matches:
            product_id = self._create_new_product(
                s3_url, clip_emb, color_hist, phash, job_id
            )
            ms = int((time.time() - start) * 1000)
            self.db.log_decision(
                job_id, s3_url, None, None, 0, 0, 0, None, ms, "new_product",
            )
            return {
                "decision": "new_product",
                "product_id": product_id,
                "clip_sim": 0,
                "color_sim": 0,
                "gap": 0,
                "processing_time_ms": ms,
            }

        # 6. Calculate signals
        top1 = matches[0]
        clip_sim = top1["clip_sim"]
        color_sim = self.compare_color_histograms(
            color_hist, np.array(top1["color_hist"], dtype=np.float32)
        )
        top2_clip_sim = matches[1]["clip_sim"] if len(matches) > 1 else 0
        gap = clip_sim - top2_clip_sim
        top2_product_id = matches[1]["product_id"] if len(matches) > 1 else None

        # 7. Decide
        decision = self.decide(clip_sim, color_sim, gap)

        # 8. Execute
        product_id = None
        if decision == "auto_merge":
            self._merge_to_product(
                top1["product_id"], s3_url, clip_emb, color_hist, phash, job_id
            )
            product_id = top1["product_id"]
        elif decision == "new_product":
            product_id = self._create_new_product(
                s3_url, clip_emb, color_hist, phash, job_id
            )
        elif decision == "review":
            self.db.add_to_review(
                s3_url, top1["product_id"], clip_sim, color_sim,
                gap, top2_product_id, top2_clip_sim,
            )

        # 9. Log
        ms = int((time.time() - start) * 1000)
        self.db.log_decision(
            job_id, s3_url, top1["product_id"], top2_product_id,
            clip_sim, color_sim, gap, top2_clip_sim, ms, decision,
        )

        return {
            "decision": decision,
            "product_id": product_id,
            "clip_sim": round(clip_sim, 4),
            "color_sim": round(color_sim, 4),
            "gap": round(gap, 4),
            "top1_product_id": top1["product_id"],
            "top2_product_id": top2_product_id,
            "processing_time_ms": ms,
        }

    # ── Helpers ────────────────────────────────────────────────

    def _create_new_product(
        self, s3_url, clip_emb, color_hist, phash, job_id
    ) -> str:
        with self._product_lock:
            product_id = self.db.generate_product_id()
            self.db.create_product(product_id)
            self.create_centroid(product_id, clip_emb, color_hist)
            image_id = str(uuid.uuid4())
            self.db.add_product_image(
                image_id, product_id, s3_url, phash,
                clip_emb.tolist(), color_hist.tolist(),
            )
        return product_id

    def _merge_to_product(
        self, product_id, s3_url, clip_emb, color_hist, phash, job_id
    ) -> None:
        with self._product_lock:
            image_id = str(uuid.uuid4())
            self.db.add_product_image(
                image_id, product_id, s3_url, phash,
                clip_emb.tolist(), color_hist.tolist(),
            )
            self.db.increment_image_count(product_id)
            self.update_centroid(product_id, clip_emb, color_hist)

    # ── Review Resolution ──────────────────────────────────────

    def resolve_review_as_merge(
        self, review_id: int, reviewed_by: str = "admin"
    ) -> dict:
        review = self.db.get_review(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")
        if review["status"] != "pending":
            raise ValueError(f"Review {review_id} already resolved")

        s3_url = review["image_s3_url"]
        product_id = review["suggested_product_id"]

        # Re-extract features from image
        bucket, key = _parse_s3_url(s3_url)
        pil_image = load_image_from_s3(bucket, key)
        clip_emb = self.extract_clip_embedding(pil_image)
        color_hist = self.extract_color_histogram(pil_image)
        phash = self.calculate_phash(pil_image)

        self._merge_to_product(product_id, s3_url, clip_emb, color_hist, phash, None)
        self.db.resolve_review(review_id, "merged", product_id, reviewed_by)

        return {"review_id": review_id, "decision": "merged", "product_id": product_id}

    def resolve_review_as_new(
        self, review_id: int, reviewed_by: str = "admin"
    ) -> dict:
        review = self.db.get_review(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")
        if review["status"] != "pending":
            raise ValueError(f"Review {review_id} already resolved")

        s3_url = review["image_s3_url"]

        bucket, key = _parse_s3_url(s3_url)
        pil_image = load_image_from_s3(bucket, key)
        clip_emb = self.extract_clip_embedding(pil_image)
        color_hist = self.extract_color_histogram(pil_image)
        phash = self.calculate_phash(pil_image)

        product_id = self._create_new_product(s3_url, clip_emb, color_hist, phash, None)
        self.db.resolve_review(review_id, "new_product", product_id, reviewed_by)

        return {"review_id": review_id, "decision": "new_product", "product_id": product_id}


# ── Utility ────────────────────────────────────────────────────

def _parse_s3_url(s3_url: str) -> Tuple[str, str]:
    """Parse S3 URL into (bucket, key).
    Handles: https://bucket.s3.amazonaws.com/key
    """
    from urllib.parse import urlparse, unquote
    parsed = urlparse(s3_url)
    bucket = parsed.hostname.split(".")[0]
    key = unquote(parsed.path.lstrip("/"))
    return bucket, key
