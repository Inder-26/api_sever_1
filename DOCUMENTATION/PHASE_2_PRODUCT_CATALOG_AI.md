# Phase 2: Product Catalog AI System

---

## TL;DR (Quick Summary)

### The Issue (Simple)
```
You upload a jhumka photo (front view) → System saves it as Product A
Next month, you upload SAME jhumka (side view) → System saves it as Product B

WRONG! Same product is treated as two different products.
Because different angles look different to the AI.
```

### What We're Building (Simple)
```
A smart system that recognizes "same product, different angle".

It uses:
- CLIP (AI) to understand what the jewelry looks like
- Color matching to confirm it's the same piece
- Product centroids (average of all angles) for better matching

Result: Upload any angle → System knows which product it belongs to.
```

---

## Technology Stack (Final — Locked)

| Component | Technology | Details |
|-----------|------------|---------|
| **Database** | **Supabase (PostgreSQL)** | Cloud-hosted PostgreSQL. Accessible from any machine, even when dev PC is off. Free tier available. Dashboard for viewing data. |
| **Job Queue** | **Redis** | Redis for job queue, idempotency keys, batch tracking, product locks. Cloud-hosted (e.g., Redis Cloud, Upstash, or Railway). |
| **Vector DB** | **Zilliz Cloud (Milvus)** | Existing instance. New `product_centroids` collection alongside existing `image_embeddings_ip`. |
| **Storage** | **AWS S3** | Existing buckets (`alyaimg`, `blyskimg`). Catalog images stored under `catalog/` prefix. |
| **AI Model** | **CLIP (openai/clip-vit-base-patch32)** | Existing model. 512-dimensional embeddings, IP metric. |
| **Server** | **FastAPI + Uvicorn** | Existing server. New endpoints under `/catalog/*` prefix via APIRouter. |

### Why These Choices?
```
Supabase (not SQLite):
  - Accessible from any machine, any time
  - Built-in dashboard to view/edit data
  - Free PostgreSQL with native array types (FLOAT[512])
  - No "machine must be on" requirement

Redis (not in-memory queue):
  - Persists job state across server restarts
  - Built-in TTL for idempotency keys
  - Atomic operations for locks
  - Industry standard for job queues

Zilliz Cloud (same instance):
  - Already connected and working
  - Just add a new collection — no new infrastructure
```

---

## Environment Variables (New for Phase 2)

```env
# ============================================================
# SUPABASE (PostgreSQL)
# Get these from: Supabase Dashboard → Project Settings → Database
# ============================================================
SUPABASE_DB_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres

# ============================================================
# REDIS
# Get from: Redis Cloud / Upstash / Railway
# ============================================================
REDIS_URL=redis://default:[PASSWORD]@[HOST]:[PORT]

# ============================================================
# EXISTING (Already in .env — no changes needed)
# ============================================================
# ZILLIZ_URL=...          (for Milvus — already set)
# ZILLIZ_TOKEN=...        (for Milvus — already set)
# AWS_ACCESS_KEY_ID=...   (for S3 — already set)
# AWS_SECRET_ACCESS_KEY=...(for S3 — already set)
# S3_BUCKET=...           (for S3 — already set)
```

---

## Code File Structure (New Files for Phase 2)

```
api_sever_1/
├── img_to_csv.py              (MODIFY) — Add ~36 lines: imports, init, register router
├── image_search_engine.py     (NO CHANGE) — Reuse embed_image(), load_image_from_s3(), s3 client
├── requirements.txt           (MODIFY) — Add: imagehash, psycopg2-binary, redis
│
├── catalog_db.py              (NEW) — Supabase/PostgreSQL database layer
│   └── CatalogDB class with all CRUD operations
│
├── catalog_pipeline.py        (NEW) — AI processing pipeline
│   ├── pHash duplicate detection (imagehash)
│   ├── Color histogram extraction (PIL, 180-bin HSV)
│   ├── Milvus centroid operations (search, upsert, update)
│   ├── Decision engine (auto_merge / review / new_product)
│   └── process_single_image() orchestrator
│
├── catalog_worker.py          (NEW) — Redis job queue + background worker
│   ├── Job submission (single + batch)
│   ├── Idempotency checking
│   ├── Background worker loop (with retry logic)
│   └── Timeout monitor (reset stuck jobs)
│
├── catalog_routes.py          (NEW) — FastAPI router (/catalog/*)
│   └── 10 endpoints (upload, status, reviews, products, metrics)
│
└── DOCUMENTATION/
    └── PHASE_2_PRODUCT_CATALOG_AI.md  (THIS FILE)
```

### What Gets Reused (NOT Modified)
| Function | File | Purpose |
|----------|------|---------|
| `embed_image()` | `image_search_engine.py` | CLIP embedding (512d, normalized for IP) |
| `load_image_from_s3()` | `image_search_engine.py` | Load PIL image from S3 |
| `s3` client | `image_search_engine.py` | boto3 S3 client |
| `clipmodel, processor, device` | `img_to_csv.py` | Shared CLIP model instance |

---

## How Key Components Work (Simple)

### How Color Matching Works
```
Same jhumka from any angle = Same colors (gold + red stones)
Different jhumka = Different colors (maybe silver + green stones)

AI says "78% similar" (confused by angle)
Color says "95% match" (same gold + red)
→ System confirms: Same product!
```

### How Product Centroids Work
```
Product has 3 photos: front, side, back
Centroid = Average of all 3 embeddings

New upload compares to this "average"
Average has "seen" all angles → matches better than single image
```

### Why We Need Database Tables
| Table | Why |
|-------|-----|
| `products` | Store product IDs (PRD-001, PRD-002...) |
| `product_images` | Track which images belong to which product |
| `review_queue` | Store uncertain cases for human to decide |
| `decision_logs` | Record every decision to find mistakes and improve |

```
Without tables = No memory, no tracking, no improvement
With tables = Know everything, fix mistakes, get smarter
```

---

## Upload Flow: First Time vs Second Time

### First Time Upload (New Product)
```
Upload jhumka front photo
    ↓
Search Milvus → No match found (<70% similar)
    ↓
Create new Product: PRD-001
    ↓
Store:
  - Image in S3
  - Embedding as centroid in Milvus
  - Color histogram
    ↓
Done. PRD-001 has 1 image.
```

### Second Time Upload (Same Product, Different Angle)
```
Upload same jhumka side photo
    ↓
Search Milvus → Found PRD-001 (82% CLIP match)
    ↓
Check color → 94% match (same gold + red)
    ↓
Check gap → top1 is clearly best match
    ↓
Decision: SAME PRODUCT
    ↓
Add image to PRD-001
Update centroid: (old + new) / 2
    ↓
Done. PRD-001 now has 2 images.
```

### What Changes Between First and Second Upload?
| Step | First Upload | Second Upload |
|------|--------------|---------------|
| Milvus Search | No match | Finds PRD-001 |
| Decision | Create new product | Add to existing |
| Centroid | Created fresh | Updated (averaged) |
| Product images | 1 | 2 |

### Visual Summary
```
FIRST UPLOAD:
[Image] → Search → Nothing found → CREATE NEW PRODUCT (PRD-001)

SECOND UPLOAD (same product, different angle):
[Image] → Search → Found PRD-001 → CLIP 82% + Color 94% → ADD TO PRD-001

SECOND UPLOAD (different product):
[Image] → Search → Found PRD-001 → CLIP 75% + Color 55% → CREATE NEW PRODUCT (PRD-002)
```

---

## Glossary (Key Terms)

| Term | What It Means |
|------|---------------|
| **CLIP** | AI model that converts images into numbers (512 numbers per image) |
| **Embedding** | The 512 numbers that represent an image |
| **Centroid** | Average embedding of all images in a product |
| **pHash** | Perceptual hash - fingerprint to detect exact duplicate images |
| **Color Histogram** | Distribution of colors in an image (180 numbers) |
| **Milvus** | Database that stores and searches embeddings fast |
| **IP (Inner Product)** | Math formula to compare two embeddings (higher = more similar) |
| **Gap** | Difference between best match and second-best match |

---

## Overview

This document outlines the architecture for an intelligent product catalog system that can:
- Detect duplicate images (exact matches)
- Recognize the same product from different angles
- Automatically group product images
- Handle uncertain cases via human review

---

## Problem Statement

### Current Issue
```
Day 1:  Upload jhumka front photo  → System creates Image A
Day 30: Upload same jhumka (side)  → System creates Image B (WRONG!)

Current system treats different angles as different products.
```

### Desired Behavior
```
Day 1:  Upload jhumka front photo  → System creates Product PRD-001
Day 30: Upload same jhumka (side)  → System adds to PRD-001 (CORRECT!)

System should recognize same product from any angle.
```

---

## Solution: Product Centroids + Multi-Signal Matching

### Core Concept

Instead of comparing **image to image**, compare **image to product**.

Each product stores a **centroid** (average embedding of all its images).

```
Product PRD-001:
├── Image 1 (front): embedding [0.5, 0.3, 0.2, ...]
├── Image 2 (side):  embedding [0.4, 0.4, 0.2, ...]
├── Image 3 (back):  embedding [0.6, 0.2, 0.2, ...]
└── Centroid:        embedding [0.5, 0.3, 0.2, ...] (average)
```

New uploads compare against **product centroids**, not individual images.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           ADMIN PANEL                               │
│                                                                     │
│   Upload images + idempotency_key                                   │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            API SERVER                               │
│                                                                     │
│   1. Check idempotency_key (prevent duplicate uploads)              │
│   2. Upload ALL images to S3 (permanent storage)                    │
│   3. Create jobs in Redis queue                                     │
│   4. Return batch_id instantly                                      │
│                                                                     │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          REDIS QUEUE                                │
│                                                                     │
│   Jobs with: image_s3_url, status, retries, timestamps              │
│                                                                     │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
┌───────────────────────────┐     ┌───────────────────────────────────┐
│      BACKGROUND WORKER    │     │    TIMEOUT MONITOR (cron 2min)    │
│                           │     │                                   │
│   Pick job → Process      │     │    Find stuck jobs (>5 min)       │
│   Retry on fail (max 3)   │     │    Reset to pending               │
│                           │     │                                   │
└─────────────┬─────────────┘     └───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        PROCESSING PIPELINE                          │
│                                                                     │
│   ┌──────────────┐                                                  │
│   │ pHash Check  │──── MATCH ────► Link to existing (skip process)  │
│   └──────┬───────┘                                                  │
│          │ NO MATCH                                                 │
│          ▼                                                          │
│   ┌──────────────┐                                                  │
│   │ Extract:     │                                                  │
│   │ • CLIP (512d)│                                                  │
│   │ • Color(180d)│                                                  │
│   └──────┬───────┘                                                  │
│          │                                                          │
│          ▼                                                          │
│   ┌──────────────┐                                                  │
│   │ Milvus TOP-3 │                                                  │
│   │ Centroid     │                                                  │
│   │ Search       │                                                  │
│   └──────┬───────┘                                                  │
│          │                                                          │
│          ▼                                                          │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │                    DECISION ENGINE                           │  │
│   │                                                              │  │
│   │   Inputs: clip_sim, color_sim, gap (top1 - top2)             │  │
│   │                                                              │  │
│   │   AUTO MERGE:  clip>85% AND color>85% AND gap>5%             │  │
│   │   NEW PRODUCT: clip<70%                                      │  │
│   │   REVIEW:      everything else                               │  │
│   │                                                              │  │
│   └──────────────────────────┬───────────────────────────────────┘  │
│                              │                                      │
│          ┌───────────────────┼───────────────────┐                  │
│          │                   │                   │                  │
│          ▼                   ▼                   ▼                  │
│   ┌────────────┐      ┌────────────┐      ┌────────────┐            │
│   │ AUTO MERGE │      │  REVIEW    │      │ NEW        │            │
│   │            │      │  QUEUE     │      │ PRODUCT    │            │
│   │ Update     │      │            │      │            │            │
│   │ centroid   │      │ Store for  │      │ Create     │            │
│   │            │      │ human      │      │ centroid   │            │
│   └────────────┘      └────────────┘      └────────────┘            │
│                              │                                      │
│                              ▼                                      │
│                    ┌──────────────────┐                             │
│                    │ LOG DECISION     │                             │
│                    │                  │                             │
│                    │ • timestamps     │                             │
│                    │ • all scores     │                             │
│                    │ • processing_ms  │                             │
│                    │ • top2_clip_sim  │                             │
│                    └──────────────────┘                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Processing Pipeline Detail

```
┌────────────────────────────────────────────────────────────┐
│                    SINGLE IMAGE PROCESSING                 │
└────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  1. pHash Check  │
                    │  (exact match?)  │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
           MATCH                        NO MATCH
              │                             │
              ▼                             ▼
    ┌─────────────────┐          ┌─────────────────────┐
    │ EXACT DUPLICATE │          │ 2. Feature Extract  │
    │                 │          │                     │
    │ Link to exist-  │          │ • CLIP embedding    │
    │ ing image       │          │   (512 dimensions)  │
    │                 │          │                     │
    │ Skip processing │          │ • Color histogram   │
    │                 │          │   (180 dimensions)  │
    └─────────────────┘          └──────────┬──────────┘
                                            │
                                            ▼
                                 ┌─────────────────────┐
                                 │ 3. Milvus Search    │
                                 │                     │
                                 │ Search TOP-3        │
                                 │ product centroids   │
                                 │                     │
                                 │ Returns:            │
                                 │ • top1 (best match) │
                                 │ • top2 (2nd best)   │
                                 │ • top3 (3rd best)   │
                                 └──────────┬──────────┘
                                            │
                                            ▼
                                 ┌─────────────────────┐
                                 │ 4. Compare Colors   │
                                 │                     │
                                 │ Compare uploaded    │
                                 │ color histogram     │
                                 │ with top1 product   │
                                 └──────────┬──────────┘
                                            │
                                            ▼
                                 ┌─────────────────────┐
                                 │ 5. Calculate Gap    │
                                 │                     │
                                 │ gap = top1_sim -    │
                                 │       top2_sim      │
                                 │                     │
                                 │ (Is top1 clearly    │
                                 │  the best match?)   │
                                 └──────────┬──────────┘
                                            │
                                            ▼
                                 ┌─────────────────────┐
                                 │ 6. Decision Engine  │
                                 └──────────┬──────────┘
                                            │
                      ┌─────────────────────┼─────────────────────┐
                      │                     │                     │
                      ▼                     ▼                     ▼
            ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
            │   AUTO MERGE     │  │     REVIEW       │  │   NEW PRODUCT    │
            │                  │  │                  │  │                  │
            │ clip > 85%       │  │ 70% < clip < 85% │  │ clip < 70%       │
            │ AND color > 85%  │  │ OR color < 85%   │  │                  │
            │ AND gap > 5%     │  │ OR gap < 5%      │  │                  │
            │                  │  │                  │  │                  │
            │ → Add image to   │  │ → Add to review  │  │ → Create new     │
            │   matched product│  │   queue for      │  │   product        │
            │ → Update centroid│  │   human decision │  │ → Create centroid│
            └──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## Decision Logic Explained

### Why Three Signals?

| Signal | What It Catches | Limitation |
|--------|-----------------|------------|
| CLIP Similarity | Semantic match (same type of jewelry) | Different angles score lower |
| Color Histogram | Same colors regardless of angle | Different products can have same colors |
| Gap (top1 - top2) | Is the match clearly the best? | - |

### Combining Signals

```
SCENARIO 1: Same product, different angle
┌─────────────────────────────────────────┐
│ CLIP:  78% (angles look different)      │
│ Color: 94% (same gold + red stones)     │
│ Gap:   12% (clear best match)           │
│                                         │
│ Decision: AUTO MERGE (color confirms)   │
└─────────────────────────────────────────┘

SCENARIO 2: Different product, similar style
┌─────────────────────────────────────────┐
│ CLIP:  82% (both are jhumkas)           │
│ Color: 58% (different stone colors)     │
│ Gap:   8%  (clear best match)           │
│                                         │
│ Decision: NEW PRODUCT (color differs)   │
└─────────────────────────────────────────┘

SCENARIO 3: Uncertain case
┌─────────────────────────────────────────┐
│ CLIP:  79%                              │
│ Color: 81%                              │
│ Gap:   3%  (top1 and top2 very close)   │
│                                         │
│ Decision: REVIEW (gap too small)        │
└─────────────────────────────────────────┘
```

---

## Database Schema

### PostgreSQL Tables

```sql
-- ============================================================
-- PRODUCTS TABLE
-- Stores product metadata (centroid stored in Milvus)
-- ============================================================
CREATE TABLE products (
    product_id      VARCHAR(20) PRIMARY KEY,  -- Format: PRD-00001
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    image_count     INT DEFAULT 1,
    is_active       BOOLEAN DEFAULT TRUE      -- Soft delete
);

-- ============================================================
-- PRODUCT IMAGES TABLE
-- All images with their embeddings (for future reprocessing)
-- ============================================================
CREATE TABLE product_images (
    image_id        VARCHAR(50) PRIMARY KEY,
    product_id      VARCHAR(20) REFERENCES products(product_id),
    s3_url          VARCHAR(500) NOT NULL,
    phash           VARCHAR(16),              -- Perceptual hash
    clip_embedding  FLOAT[512],               -- Stored for reprocessing
    color_hist      FLOAT[180],               -- Stored for reprocessing
    created_at      TIMESTAMP DEFAULT NOW(),
    is_active       BOOLEAN DEFAULT TRUE      -- Soft delete
);

-- ============================================================
-- REVIEW QUEUE TABLE
-- Uncertain cases waiting for human decision
-- ============================================================
CREATE TABLE review_queue (
    id                      SERIAL PRIMARY KEY,
    image_s3_url            VARCHAR(500) NOT NULL,
    suggested_product_id    VARCHAR(20),
    clip_sim                FLOAT,
    color_sim               FLOAT,
    gap                     FLOAT,
    top2_product_id         VARCHAR(20),
    top2_clip_sim           FLOAT,
    status                  VARCHAR(20) DEFAULT 'pending',
    final_decision          VARCHAR(20),      -- merged / new_product
    final_product_id        VARCHAR(20),      -- Where it ended up
    reviewed_by             VARCHAR(100),
    reviewed_at             TIMESTAMP,
    created_at              TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- DECISION LOGS TABLE
-- Every decision for analysis and threshold tuning
-- ============================================================
CREATE TABLE decision_logs (
    id                  SERIAL PRIMARY KEY,
    timestamp           TIMESTAMP DEFAULT NOW(),
    job_id              VARCHAR(50),
    image_s3_url        VARCHAR(500),
    top1_product_id     VARCHAR(20),
    top2_product_id     VARCHAR(20),
    clip_sim            FLOAT,
    color_sim           FLOAT,
    gap                 FLOAT,
    top2_clip_sim       FLOAT,
    processing_time_ms  INT,
    decision            VARCHAR(20),          -- auto_merge / review / new_product
    final_outcome       VARCHAR(20),          -- Filled after review
    was_correct         BOOLEAN               -- Filled if mistake found
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX idx_phash ON product_images(phash);
CREATE INDEX idx_product_images_product ON product_images(product_id);
CREATE INDEX idx_review_status ON review_queue(status);
CREATE INDEX idx_logs_decision ON decision_logs(decision);
CREATE INDEX idx_logs_timestamp ON decision_logs(timestamp);
CREATE INDEX idx_products_active ON products(is_active);
```

### Milvus Collection

```
Collection: product_centroids
├── product_id    (VARCHAR, primary key)
├── centroid      (FLOAT_VECTOR, 512 dimensions)
│                 Index: HNSW
│                 Metric: IP (Inner Product)
├── color_hist    (FLOAT_VECTOR, 180 dimensions)
└── image_count   (INT64)
```

### Redis Keys

```
# Idempotency (prevents duplicate uploads)
# TTL: 1 hour
idempotency:{key} → batch_id

# Batch tracking
# TTL: 24 hours
batch:{batch_id} → {
    job_ids: ["job_001", "job_002", ...],
    total: 50,
    created_at: "2026-02-06T10:00:00Z"
}

# Individual job status
# TTL: 24 hours
job:{job_id} → {
    batch_id: "batch_abc123",
    image_s3_url: "https://s3.../image.jpg",
    status: "pending|processing|completed|failed",
    retries: 0,
    result: {
        decision: "auto_merge",
        product_id: "PRD-00123",
        processing_time_ms: 1250
    },
    error: null,
    created_at: "2026-02-06T10:00:00Z",
    updated_at: "2026-02-06T10:00:05Z"
}

# Product-level lock (prevents race conditions)
# TTL: 5 seconds
lock:product:{product_id} → "1"
```

---

## API Endpoints

### Upload Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload single image |
| `/upload-batch` | POST | Upload 1-50 images with idempotency_key |

### Status Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/job/{job_id}` | GET | Get single job status |
| `/batch/{batch_id}` | GET | Get all jobs in batch |

### Review Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reviews` | GET | List pending reviews |
| `/reviews/{id}/merge` | POST | Approve as same product |
| `/reviews/{id}/new` | POST | Create as new product |

### Product Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/products` | GET | List all products |
| `/products/{id}` | GET | Get product with all images |

### Debug Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/system/metrics` | GET | Health dashboard |
| `/debug/job/{job_id}` | GET | Detailed job analysis |

---

## API Request/Response Examples

### Upload Batch

**Request:**
```json
POST /upload-batch
Content-Type: multipart/form-data

{
    "idempotency_key": "uuid-from-frontend-abc123",
    "images": [file1, file2, file3, ...]
}
```

**Response (Instant):**
```json
{
    "batch_id": "batch_abc123",
    "jobs": [
        {"job_id": "job_001", "status": "queued"},
        {"job_id": "job_002", "status": "queued"},
        {"job_id": "job_003", "status": "queued"}
    ],
    "total": 3,
    "message": "3 images queued for processing"
}
```

### Check Batch Status

**Request:**
```
GET /batch/batch_abc123
```

**Response:**
```json
{
    "batch_id": "batch_abc123",
    "total": 3,
    "completed": 2,
    "failed": 0,
    "pending": 1,
    "jobs": [
        {
            "job_id": "job_001",
            "status": "completed",
            "result": {
                "decision": "new_product",
                "product_id": "PRD-00456",
                "processing_time_ms": 1320
            }
        },
        {
            "job_id": "job_002",
            "status": "completed",
            "result": {
                "decision": "review",
                "suggested_product_id": "PRD-00089",
                "clip_sim": 0.78,
                "color_sim": 0.82,
                "gap": 0.04
            }
        },
        {
            "job_id": "job_003",
            "status": "processing"
        }
    ]
}
```

### System Metrics

**Request:**
```
GET /system/metrics
```

**Response:**
```json
{
    "queue_pending": 5,
    "queue_processing": 2,
    "completed_today": 148,
    "failed_today": 1,
    "avg_processing_time_ms": 1150,
    "review_pending": 3,
    "total_products": 1247,
    "total_images": 3891
}
```

---

## Centroid Update Algorithm

### When Image is Added to Product

```python
def update_centroid(product_id: str, new_embedding: np.ndarray):
    """
    Update product centroid using weighted average.
    Uses Redis lock to prevent race conditions.
    """
    lock_key = f"lock:product:{product_id}"

    # Acquire lock
    if not redis.set(lock_key, "1", nx=True, ex=5):
        raise RetryLater("Product locked, retry in 2 seconds")

    try:
        # Get current product
        product = milvus.get(product_id)
        old_centroid = product.centroid
        old_count = product.image_count

        # Calculate new centroid (weighted average)
        new_centroid = (old_centroid * old_count + new_embedding) / (old_count + 1)

        # Normalize for IP similarity
        new_centroid = new_centroid / np.linalg.norm(new_centroid)

        # Update in Milvus
        milvus.upsert(
            product_id=product_id,
            centroid=new_centroid,
            image_count=old_count + 1
        )

    finally:
        redis.delete(lock_key)
```

### When New Product is Created

```python
def create_product(image_embedding: np.ndarray, color_hist: np.ndarray) -> str:
    """
    Create new product with initial centroid.
    """
    # Generate product ID
    product_id = generate_product_id()  # PRD-00001 format

    # Normalize embedding
    centroid = image_embedding / np.linalg.norm(image_embedding)

    # Insert into Milvus
    milvus.insert(
        product_id=product_id,
        centroid=centroid,
        color_hist=color_hist,
        image_count=1
    )

    # Insert into PostgreSQL
    db.execute("""
        INSERT INTO products (product_id, image_count)
        VALUES (%s, 1)
    """, [product_id])

    return product_id
```

---

## Color Histogram Extraction

```python
import cv2
import numpy as np

def extract_color_histogram(image: np.ndarray) -> np.ndarray:
    """
    Extract HSV color histogram from image.
    Returns 180-dimensional vector (Hue channel).

    HSV is better than RGB for jewelry because:
    - Hue captures actual color (gold, red, silver)
    - Saturation/Value handle lighting variations
    """
    # Convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    # Extract Hue histogram (180 bins)
    hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])

    # Normalize to sum to 1
    hist = hist / hist.sum()

    return hist.flatten()


def compare_color_histograms(hist1: np.ndarray, hist2: np.ndarray) -> float:
    """
    Compare two histograms using intersection.
    Returns similarity score 0-1.
    """
    # Histogram intersection
    similarity = np.minimum(hist1, hist2).sum()
    return float(similarity)
```

---

## pHash Duplicate Detection

```python
import imagehash
from PIL import Image

def calculate_phash(image: Image.Image) -> str:
    """
    Calculate perceptual hash of image.
    Returns 16-character hex string.
    """
    return str(imagehash.phash(image))


def check_phash_duplicate(phash: str) -> Optional[str]:
    """
    Check if exact duplicate exists.
    Returns image_id if found, None otherwise.
    """
    result = db.execute("""
        SELECT image_id, product_id
        FROM product_images
        WHERE phash = %s AND is_active = TRUE
        LIMIT 1
    """, [phash])

    if result:
        return result[0]
    return None
```

---

## Retry Logic

```python
MAX_RETRIES = 3
RETRY_DELAYS = [2, 4, 8]  # Exponential backoff

def process_job_with_retry(job_id: str):
    job = redis.get(f"job:{job_id}")

    try:
        job['status'] = 'processing'
        job['updated_at'] = now()
        redis.set(f"job:{job_id}", job)

        result = process_image(job['image_s3_url'])

        job['status'] = 'completed'
        job['result'] = result

    except Exception as e:
        job['retries'] += 1

        if job['retries'] < MAX_RETRIES:
            job['status'] = 'pending'
            delay = RETRY_DELAYS[job['retries'] - 1]
            requeue_with_delay(job_id, delay)
        else:
            job['status'] = 'failed'
            job['error'] = str(e)

    finally:
        job['updated_at'] = now()
        redis.set(f"job:{job_id}", job)
```

---

## Timeout Monitor (Cron Job)

```python
def reset_stuck_jobs():
    """
    Run every 2 minutes.
    Reset jobs stuck in 'processing' for >5 minutes.
    """
    stuck_jobs = find_jobs_where(
        status='processing',
        updated_at__lt=now() - timedelta(minutes=5)
    )

    for job in stuck_jobs:
        job['status'] = 'pending'
        job['retries'] += 1
        job['updated_at'] = now()

        if job['retries'] >= MAX_RETRIES:
            job['status'] = 'failed'
            job['error'] = 'Timeout after multiple retries'
        else:
            requeue(job)
```

---

## Implementation Checklist

### Day 1: Infrastructure
- [ ] Setup Redis
- [ ] Create PostgreSQL tables
- [ ] Create Milvus collection
- [ ] `POST /upload-batch` endpoint (with idempotency)
- [ ] `GET /batch/{id}` endpoint
- [ ] Basic worker (pick jobs from queue)

### Day 2: AI Pipeline
- [ ] pHash extraction + duplicate check
- [ ] CLIP embedding extraction
- [ ] Color histogram extraction
- [ ] Milvus centroid search (top-3)
- [ ] Decision engine logic
- [ ] Decision logging

### Day 3: Product Management
- [ ] Create product + centroid
- [ ] Update centroid on merge (with locking)
- [ ] Review queue endpoints
- [ ] Timeout monitor (cron)
- [ ] Retry logic
- [ ] System metrics endpoint
- [ ] Testing

---

## Expected Performance

| Metric | Expected Value |
|--------|----------------|
| Upload response time | < 500ms (async) |
| Processing time per image | 1-2 seconds |
| Milvus search time | < 50ms |
| Auto-merge accuracy | 95%+ |
| Reviews per day | 0-2 |
| Wrong merges | Near zero |

---

## Threshold Configuration

```python
# Store in config file or environment variables
# Easy to tune based on decision_logs analysis

THRESHOLDS = {
    # Auto merge requirements (all must be true)
    "auto_merge_clip": 0.85,
    "auto_merge_color": 0.85,
    "auto_merge_gap": 0.05,

    # New product threshold
    "new_product_clip": 0.70,

    # Everything else goes to review
}
```

---

## Future Improvements (Add Only If Needed)

| Improvement | When to Add |
|-------------|-------------|
| Image normalization | If matching accuracy drops |
| Model versioning | If changing CLIP model |
| Milvus caching | If search becomes slow |
| Auto threshold tuning | If reviews exceed 10/day |
| Category filtering | If cross-category matches occur |

---

## Real-World Scenarios

### Scenario 1: New Product Upload
```
Input: Jhumka front photo (first time in system)

Step 1: pHash check → No match
Step 2: CLIP embedding → [0.02, -0.08, ...]
Step 3: Milvus search → Best match is 45% (too low)
Step 4: Decision → NEW PRODUCT

Result:
- Created PRD-001
- Stored image in S3
- Created centroid in Milvus
```

### Scenario 2: Same Product, Different Angle
```
Input: Same jhumka from side (PRD-001 exists with front photo)

Step 1: pHash check → No match (different angle)
Step 2: CLIP embedding → [0.03, -0.07, ...]
Step 3: Milvus search → PRD-001 is 82% match
Step 4: Color check → 94% match
Step 5: Gap check → 15% gap (clear winner)
Step 6: Decision → AUTO MERGE

Result:
- Added image to PRD-001
- Updated centroid: (old + new) / 2
- PRD-001 now has 2 images
```

### Scenario 3: Similar But Different Product
```
Input: Different gold jhumka (similar style to PRD-001)

Step 1: pHash check → No match
Step 2: CLIP embedding → [0.04, -0.06, ...]
Step 3: Milvus search → PRD-001 is 78% match
Step 4: Color check → 52% match (different stones!)
Step 5: Decision → NEW PRODUCT

Result:
- Created PRD-002
- Different stone colors saved the day
```

### Scenario 4: Uncertain Case (Human Review)
```
Input: Similar jhumka, similar colors

Step 1: pHash check → No match
Step 2: CLIP embedding → extracted
Step 3: Milvus search → PRD-001 is 79% match, PRD-002 is 76% match
Step 4: Color check → 83% match
Step 5: Gap check → Only 3% gap (too close!)
Step 6: Decision → REVIEW

Result:
- Added to review queue
- Human will decide: merge to PRD-001 or create PRD-003
```

---

## Quick Reference: Decision Rules

```
┌─────────────────────────────────────────────────────────────┐
│                    DECISION CHEAT SHEET                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  AUTO MERGE (add to existing product):                      │
│    ✓ CLIP similarity > 85%                                  │
│    ✓ Color similarity > 85%                                 │
│    ✓ Gap (top1 - top2) > 5%                                │
│    All three must be true!                                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  NEW PRODUCT (create fresh):                                │
│    ✓ CLIP similarity < 70%                                  │
│    Just this one rule.                                      │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  REVIEW (human decides):                                    │
│    Everything else:                                         │
│    - CLIP between 70-85%                                    │
│    - OR Color < 85%                                         │
│    - OR Gap < 5%                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting Guide

### Problem: Wrong products getting merged
```
Symptom: Two different jhumkas ended up in same product

Check:
1. Look at decision_logs for that image
2. Check color_sim - was it high despite different products?
3. Check gap - was there a close second match?

Fix:
- If color is fooling the system → lower color threshold
- If gap was small → increase gap threshold
- Split the product manually and reprocess
```

### Problem: Same product not being recognized
```
Symptom: Same jhumka from different angles creating new products

Check:
1. Look at CLIP similarity - is it below 70%?
2. Check if lighting/background is very different
3. Check color_sim - lighting affecting colors?

Fix:
- If CLIP is 65-70% → lower new_product threshold to 65%
- If color is low due to lighting → consider image normalization
- Manually merge and system will learn from updated centroid
```

### Problem: Too many reviews
```
Symptom: More than 5-10 reviews per day

Check:
1. What's the distribution of CLIP scores in reviews?
2. Are reviews mostly becoming merges or new products?

Fix:
- If most reviews → merge: lower auto_merge_clip threshold
- If most reviews → new: raise new_product_clip threshold
- Analyze decision_logs to find optimal thresholds
```

---

## System Health Checks

### Daily Check (1 minute)
```
GET /system/metrics

Look for:
- review_pending < 5 (normal)
- failed_today < 3 (normal)
- avg_processing_time_ms < 2000 (normal)
```

### Weekly Check (5 minutes)
```sql
-- Check wrong merge rate
SELECT
    COUNT(*) as total_decisions,
    SUM(CASE WHEN was_correct = false THEN 1 ELSE 0 END) as wrong
FROM decision_logs
WHERE timestamp > NOW() - INTERVAL '7 days';

-- Check review outcomes
SELECT
    final_decision,
    COUNT(*) as count
FROM review_queue
WHERE reviewed_at > NOW() - INTERVAL '7 days'
GROUP BY final_decision;
```

### Monthly Check (15 minutes)
```
1. Review decision_logs for patterns
2. Adjust thresholds if needed
3. Check for any corrupted products (wrong images)
4. Backup database
```

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-06 | Initial architecture design |
| 1.1 | 2026-02-06 | Added simple explanations, glossary, scenarios, troubleshooting |
