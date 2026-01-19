# Project Overview: AI Jewelry Assistant

## Executive Summary

This project is a multi-functional AI platform designed for the jewelry e-commerce sector. It automates various tasks such as catalog creation, image generation, semantic search, and data validation using a combination of Large Language Models (Gemini, DALL-E 3), Computer Vision (CLIP), and Web Scraping.

## Core Architecture

- **Backend API**: FastAPI (`img_to_csv.py`) - Acts as the central brain orchestrating all services.
- **Frontend**: Streamlit (`jwellery_front.py`) - Provides a user interface for uploading images and viewing results.
- **Database / Vector Store**:
  - **ChromaDB & Milvus**: Used for storing image and text embeddings for semantic and visual search.
  - **JSON/CSV**: Local storage for temporary data processing.
- **AI Services**:
  - **Google Gemini (Flash 2.0/Pro)**: Text generation, image analysis (multimodal), and data structure extraction (PDFs).
  - **OpenAI DALL-E 3**: Photorealistic product image generation (`utils2.py`).
  - **CLIP**: Image embeddings for similarity search.
- **Infrastructure**: AWS S3 for storage.

## Key Functional Modules

### 1. Image Generation & Manipulation

**Files**: `img_to_csv.py`, `utils2.py`, `prompts2.py`

- **Purpose**: Generates high-quality marketing images for jewelry.
- **Endpoints**:
  - `/generate-images`: Takes an original product image, extracts its design, and places it in new contexts (white background, on a model, with props).
  - `/regenerate-image`: Refines specific generated images.
- **Logic**: Uses `prompts2.py` to define strict style guides (e.g., "natural shadow," "soft lighting") passed to DALL-E 3.

### 2. E-commerce Catalog Automation

**Files**: `img_to_csv.py`, `prompts.py`, `excel_fields.py`

- **Purpose**: Automates the creation of catalog files for marketplaces like Amazon, Flipkart, and Meesho.
- **Endpoints**: `/catalog-ai`, `/catalog_ai_variations`
- **Logic**: Analyzes product images to extract technical attributes (type, material, design) and fills marketplace-specific Excel templates. Supports variations (size, color).

### 3. Semantic Search & Recommendations

**Files**: `img_to_csv.py`, `image_search_engine.py`

- **Purpose**: Helps users find jewelry based on abstract descriptions (e.g., "elegant evening wear").
- **Endpoints**:
  - `/semantic_filter_jewelry/`: Matches user intent with product attributes using vector search (ChromaDB).
  - `/image_similarity_search`: Finds products visually similar to an uploaded image using CLIP embeddings.

### 4. Image Analysis & Captioning

**Files**: `img_to_csv.py`

- **Endpoints**: `/generate_caption`, `/process-image-and-prompt/`
- **Logic**: Uses Gemini to generate SEO-friendly titles, descriptions, and attribute lists (color, quality grade) for uploaded images.

### 5. Data Scraping

**Files**: `scraper.py`, `flp_scraper.py`, `myn_scraper.py`

- **Purpose**: Gathers market data from major e-commerce platforms (Amazon, etc.).
- **Logic**: Uses extensive Playwright automation to scrape product details, rankings, and "A+ content".

### 6. Order Processing

**Files**: `img_to_csv.py`

- **Endpoints**: `/create_order`
- **Logic**: Parses PDF invoices/orders using Gemini to extract structured transaction data (SKUs, quantities, prices).

## Key Files Map

| File                | Responsibility                                                                     |
| ------------------- | ---------------------------------------------------------------------------------- |
| `img_to_csv.py`     | **Main Server**. Defines all API routes and business logic.                        |
| `scraper.py`        | **Amazon Scraper**. Playwright scripts for extracting product data.                |
| `utils2.py`         | **AI Utilities**. Wrapper functions for DALL-E 3 image generation.                 |
| `prompts.py`        | **Catalog Prompts**. Huge collection of prompts for extracting product attributes. |
| `prompts2.py`       | **Image Gen Prompts**. Refined prompts for DALL-E 3 (focus of recent work).        |
| `jwellery_front.py` | **UI**. Streamlit interface for end-users.                                         |
