import os
import logging
from typing import Optional
from datetime import datetime, timezone
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

logger = logging.getLogger("catalog_db")


class CatalogDB:
    def __init__(self, db_url: str = None):
        if db_url is None:
            db_url = os.getenv("SUPABASE_DB_URL")
        if not db_url:
            raise ValueError("SUPABASE_DB_URL not set")

        self.pool = pool.ThreadedConnectionPool(
            minconn=2, maxconn=10, dsn=db_url
        )
        logger.info("CatalogDB connection pool created")

    def _get_conn(self):
        return self.pool.getconn()

    def _put_conn(self, conn):
        self.pool.putconn(conn)

    def close(self):
        self.pool.closeall()
        logger.info("CatalogDB connection pool closed")

    # ── Product ID Generation ──────────────────────────────────

    def generate_product_id(self) -> str:
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT product_id FROM products ORDER BY product_id DESC LIMIT 1"
                )
                row = cur.fetchone()
                if row:
                    num = int(row[0].split("-")[1]) + 1
                else:
                    num = 1
                return f"PRD-{num:05d}"
        finally:
            self._put_conn(conn)

    # ── Products CRUD ──────────────────────────────────────────

    def create_product(self, product_id: str) -> dict:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO products (product_id, image_count) VALUES (%s, 1) RETURNING *",
                    (product_id,),
                )
                row = dict(cur.fetchone())
            conn.commit()
            return row
        except Exception:
            conn.rollback()
            raise
        finally:
            self._put_conn(conn)

    def get_product(self, product_id: str) -> Optional[dict]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM products WHERE product_id = %s AND is_active = TRUE",
                    (product_id,),
                )
                row = cur.fetchone()
                return dict(row) if row else None
        finally:
            self._put_conn(conn)

    def list_products(self, limit: int = 50, offset: int = 0) -> list:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM products WHERE is_active = TRUE "
                    "ORDER BY created_at DESC LIMIT %s OFFSET %s",
                    (limit, offset),
                )
                return [dict(r) for r in cur.fetchall()]
        finally:
            self._put_conn(conn)

    def increment_image_count(self, product_id: str) -> None:
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE products SET image_count = image_count + 1, "
                    "updated_at = NOW() WHERE product_id = %s",
                    (product_id,),
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._put_conn(conn)

    # ── Product Images CRUD ────────────────────────────────────

    def add_product_image(
        self,
        image_id: str,
        product_id: str,
        s3_url: str,
        phash: str,
        clip_embedding: list,
        color_hist: list,
    ) -> dict:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO product_images "
                    "(image_id, product_id, s3_url, phash, clip_embedding, color_hist) "
                    "VALUES (%s, %s, %s, %s, %s, %s) RETURNING *",
                    (image_id, product_id, s3_url, phash, clip_embedding, color_hist),
                )
                row = dict(cur.fetchone())
            conn.commit()
            return row
        except Exception:
            conn.rollback()
            raise
        finally:
            self._put_conn(conn)

    def get_images_for_product(self, product_id: str) -> list:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM product_images "
                    "WHERE product_id = %s AND is_active = TRUE "
                    "ORDER BY created_at ASC",
                    (product_id,),
                )
                return [dict(r) for r in cur.fetchall()]
        finally:
            self._put_conn(conn)

    def find_by_s3_url(self, s3_url: str) -> Optional[dict]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT image_id, product_id, s3_url FROM product_images "
                    "WHERE s3_url = %s AND is_active = TRUE LIMIT 1",
                    (s3_url,),
                )
                row = cur.fetchone()
                return dict(row) if row else None
        finally:
            self._put_conn(conn)

    def find_by_phash(self, phash: str) -> Optional[dict]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT image_id, product_id, s3_url FROM product_images "
                    "WHERE phash = %s AND is_active = TRUE LIMIT 1",
                    (phash,),
                )
                row = cur.fetchone()
                return dict(row) if row else None
        finally:
            self._put_conn(conn)

    # ── Review Queue ───────────────────────────────────────────

    def add_to_review(
        self,
        image_s3_url: str,
        suggested_product_id: str,
        clip_sim: float,
        color_sim: float,
        gap: float,
        top2_product_id: str = None,
        top2_clip_sim: float = None,
    ) -> int:
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO review_queue "
                    "(image_s3_url, suggested_product_id, clip_sim, color_sim, "
                    "gap, top2_product_id, top2_clip_sim) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (
                        image_s3_url, suggested_product_id, clip_sim,
                        color_sim, gap, top2_product_id, top2_clip_sim,
                    ),
                )
                review_id = cur.fetchone()[0]
            conn.commit()
            return review_id
        except Exception:
            conn.rollback()
            raise
        finally:
            self._put_conn(conn)

    def get_pending_reviews(self, limit: int = 20) -> list:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM review_queue WHERE status = 'pending' "
                    "ORDER BY created_at ASC LIMIT %s",
                    (limit,),
                )
                return [dict(r) for r in cur.fetchall()]
        finally:
            self._put_conn(conn)

    def get_review(self, review_id: int) -> Optional[dict]:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM review_queue WHERE id = %s",
                    (review_id,),
                )
                row = cur.fetchone()
                return dict(row) if row else None
        finally:
            self._put_conn(conn)

    def resolve_review(
        self,
        review_id: int,
        decision: str,
        final_product_id: str,
        reviewed_by: str = "admin",
    ) -> dict:
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "UPDATE review_queue SET status = 'resolved', "
                    "final_decision = %s, final_product_id = %s, "
                    "reviewed_by = %s, reviewed_at = NOW() "
                    "WHERE id = %s RETURNING *",
                    (decision, final_product_id, reviewed_by, review_id),
                )
                row = dict(cur.fetchone())
            conn.commit()
            return row
        except Exception:
            conn.rollback()
            raise
        finally:
            self._put_conn(conn)

    # ── Decision Logs ──────────────────────────────────────────

    def log_decision(
        self,
        job_id: str,
        image_s3_url: str,
        top1_product_id: str,
        top2_product_id: str,
        clip_sim: float,
        color_sim: float,
        gap: float,
        top2_clip_sim: float,
        processing_time_ms: int,
        decision: str,
    ) -> int:
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO decision_logs "
                    "(job_id, image_s3_url, top1_product_id, top2_product_id, "
                    "clip_sim, color_sim, gap, top2_clip_sim, "
                    "processing_time_ms, decision) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (
                        job_id, image_s3_url, top1_product_id, top2_product_id,
                        clip_sim, color_sim, gap, top2_clip_sim,
                        processing_time_ms, decision,
                    ),
                )
                log_id = cur.fetchone()[0]
            conn.commit()
            return log_id
        except Exception:
            conn.rollback()
            raise
        finally:
            self._put_conn(conn)

    # ── Metrics ────────────────────────────────────────────────

    def get_metrics(self) -> dict:
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM products WHERE is_active = TRUE"
                )
                total_products = cur.fetchone()[0]

                cur.execute(
                    "SELECT COUNT(*) FROM product_images WHERE is_active = TRUE"
                )
                total_images = cur.fetchone()[0]

                cur.execute(
                    "SELECT COUNT(*) FROM review_queue WHERE status = 'pending'"
                )
                review_pending = cur.fetchone()[0]

                cur.execute(
                    "SELECT COUNT(*) FROM decision_logs "
                    "WHERE timestamp >= CURRENT_DATE"
                )
                decisions_today = cur.fetchone()[0]

                cur.execute(
                    "SELECT COALESCE(AVG(processing_time_ms), 0) FROM decision_logs "
                    "WHERE timestamp >= CURRENT_DATE"
                )
                avg_processing_ms = int(cur.fetchone()[0])

                return {
                    "total_products": total_products,
                    "total_images": total_images,
                    "review_pending": review_pending,
                    "decisions_today": decisions_today,
                    "avg_processing_time_ms": avg_processing_ms,
                }
        finally:
            self._put_conn(conn)
