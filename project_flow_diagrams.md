# Project Flow Diagrams

This document visualizes the different workflows within the AI Jewelry Assistant project.

## 1. High-Level Architecture

This diagram shows the main components of the system and how they interact.

```mermaid
graph TD
    User([User])
    Frontend["Streamlit Frontend <br/> jwellery_front.py"]
    Backend["FastAPI Backend <br/> img_to_csv.py"]

    subgraph AI_Services [AI Service Integration]
        Gemini["Google Gemini <br/> Text/Vision"]
        DallE["OpenAI DALL-E 3 <br/> Image Gen"]
        CLIP["CLIP Model <br/> Image Embeddings"]
    end

    subgraph Data [Data & Storage]
        S3["AWS S3"]
        Chroma["ChromaDB <br/> Vector Store"]
        Milvus["Milvus <br/> Vector Store"]
        Excel["Excel Files <br/> Output"]
    end

    subgraph Adapter [Scraping Adapters]
        Scrapers["Scrapers <br/> scraper.py / flp_scraper.py / myn_scraper.py"]
    end

    User -->|Interacts| Frontend
    Frontend -->|HTTP Requests| Backend

    Backend -->|API Calls| Gemini
    Backend -->|API Calls| DallE
    Backend -->|Computes| CLIP

    Backend -->|Reads/Writes| S3
    Backend -->|Queries| Chroma
    Backend -->|Queries| Milvus
    Backend -->|Generates| Excel

    Backend -->|Invokes| Scrapers
    Scrapers -->|Visits| ExternalSites["Amazon / Flipkart / Myntra / Meesho"]
```

## 2. Image Generation Workflow

This flow details how an uploaded product image is transformed into a marketing asset.

```mermaid
sequenceDiagram
    participant User
    participant Backend as FastAPI (img_to_csv.py)
    participant Utils as Utils (utils2.py)
    participant Prompts as Prompts (prompts2.py)
    participant OpenAI as OpenAI DALL-E 3
    participant S3 as AWS S3

    User->>Backend: Upload Original Image (Earrings/Necklace)
    Backend->>Backend: Identify Product Type (Ear/Neck/Bra)
    Backend->>Prompts: Select Prompt Template (e.g. White Bg, Natural Shadow)
    Backend->>Utils: generate_images_from_gpt(image, prompts)
    Utils->>OpenAI: API Call (base64 image + prompt + style="natural")
    OpenAI-->>Utils: Generated Image (b64_json)
    Utils->>Backend: Return Generated Images
    Backend->>S3: Upload Images & Create ZIP
    Backend-->>User: Return Image URLs + ZIP Link
```

## 3. Catalog Automation Workflow

This flow shows how images are converted into e-commerce catalog spreadsheets.

```mermaid
graph LR
    Input([User Uploads URLs + SKUs]) --> Validator{Check Marketplace}

    Validator -->|Amazon| AMZ_Flow[Amazon Pipeline]
    Validator -->|Flipkart| FLP_Flow[Flipkart Pipeline]
    Validator -->|Meesho| MEE_Flow[Meesho Pipeline]

    subgraph Analysis [AI Analysis]
        Gemini1[Gemini 2.0 Flash]
        Prompts[Catalog Prompts]
        Gemini1 -->|Extract Attributes| Attributes[JSON Data]
    end

    AMZ_Flow --> Gemini1
    FLP_Flow --> Gemini1
    MEE_Flow --> Gemini1

    Attributes --> Formatter[Excel Formatter]
    Formatter --> Excel[Output Excel File]
    Excel --> Upload[Upload to S3]
    Upload --> Final([Return Excel Link])
```

## 4. Scraping Workflow

This flow illustrates how the system gathers data from external e-commerce sites.

```mermaid
sequenceDiagram
    participant API as FastAPI
    participant Scraper as Scrapers (scraper.py, flp_scraper.py, myn_scraper.py)
    participant Browser as Playwright Browser
    participant Site as E-commerce Site

    API->>Scraper: Request Product Data (Search Query / ASIN list)
    Scraper->>Browser: Launch Browser (Headless)

    loop For Each Page/Product
        Browser->>Site: Navigate to URL
        Site-->>Browser: Return HTML
        Browser->>Scraper: Parse DOM (CSS Selectors)
        Scraper->>Scraper: Extract Price, Rating, Image, Description
        Scraper->>Scraper: Random Sleep (Anti-bot)
    end

    Scraper->>API: Return List[ProductDict]
    API->>API: Process/Store Data
```
