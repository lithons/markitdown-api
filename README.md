# MarkItDown REST API Docker Container

A containerized REST API for Microsoft's MarkItDown library that converts various document formats to Markdown..

## Features

- Convert documents to Markdown via REST API
- Support for PDF, DOCX, PPTX, XLSX, images, HTML, and more
- Docker containerized for easy deployment
- FastAPI with automatic API documentation
- File upload and URL conversion support

## Quick Start

You can run the API locally with Python or via Docker.

1. Run locally with Python (recommended for development):
   - Ensure you have Python 3.10+ installed.
   - From the repo root, create and activate a virtual environment, then install deps:
     - Windows (PowerShell):
       - python -m venv .venv
       - .\.venv\Scripts\Activate.ps1
       - pip install -r src/markitdown-api/requirements.txt
     - macOS/Linux:
       - python3 -m venv .venv
       - source .venv/bin/activate
       - pip install -r src/markitdown-api/requirements.txt
   - Start the FastAPI app with Uvicorn (auto-reload):
     - uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir src/markitdown-api
   - Open http://localhost:8000/scalar for interactive docs.

2. Or use Docker Compose:
   - docker compose -f src/markitdown-api/docker-compose.yml up --build

3. Or build and run the Docker image manually:
   - docker build -t markitdown-api src/markitdown-api
   - docker run -p 8000:8000 markitdown-api

## API Endpoints

- GET / - Health check
- GET /health - Detailed health endpoint
- POST /convert - Upload file for conversion (multipart/form-data)
- POST /convert-url - Convert document from URL (application/json)
- GET /supported-formats - List supported formats
- GET /scalar - Interactive API documentation (Scalar UI)

## Usage Examples

**Upload file conversion:**

```bash
curl -X POST "http://localhost:8000/convert" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@example.pdf"
```

**URL conversion:**

```bash
curl -X POST "http://localhost:8000/convert-url" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com/document.pdf"}'
```

## Configuration

- Port: 8000 (configurable via PORT env var; HOST via HOST env var)
- Max file size: 50MB
- Supported formats: PDF, Office docs, images, HTML, and more
- ENV: development|staging|production (affects CORS and trusted hosts)
- PUBLIC_BASE_URL: optional public URL (e.g., https://api.example.com) used for docs server URL and TrustedHost in production
- CORS_ORIGINS: comma-separated list of origins allowed for CORS

## Requirements

- Python 3.10+ and pip (for local development)
- Docker (optional, for containerized deployment)
- 2GB+ RAM recommended for processing large documents

## OpenAPI and Client Generation

This repository uses an OpenAPI schema and Microsoft Kiota to generate API clients that live under `src/clients/`. Changes to the API must be reflected in the generated clients.

### Generate openapi.json
Use the provided tool to regenerate the OpenAPI document from the FastAPI app without running the server:

```bash
# Run from the app directory so that "app" is on PYTHONPATH
cd src/markitdown-api

# Writes to ../openapi.json by default (project root openapi.json)
python -m app.tools.generate_openapi

# Optionally include a server URL in the OpenAPI 'servers' section
PUBLIC_BASE_URL=https://api.example.com python -m app.tools.generate_openapi

# Or write to a specific file (or '-' for stdout)
python -m app.tools.generate_openapi -o openapi.json
# The above writes to src/markitdown-api/openapi.json because we are in that directory
```

### Generate clients with Kiota
Prerequisites: Install the Kiota CLI. You can install it locally or rely on the GitHub Action (see below).

Generate both C# and TypeScript clients in one command (also regenerates openapi.json by default):
```bash
# Run from the app directory ./src/markitdown-api
cd src/markitdown-api
python -m app.tools.generate_clients

# Optionally include a server URL in the OpenAPI 'servers' section
PUBLIC_BASE_URL=https://api.example.com python -m app.tools.generate_clients

# Skip regenerating openapi.json and use an existing file
python -m app.tools.generate_clients --skip-openapi --openapi ../openapi.json
```

Generate only C# client:
```bash
kiota generate -d src/markitdown-api/openapi.json -l CSharp -c MarkItDownApiClient -n Lithons.MarkItDown -o src/clients/csharp/Generated
```

Generate only TypeScript client:
```bash
kiota generate -d src/markitdown-api/openapi.json -l TypeScript -c MarkItDownApiClient -n Lithons -o src/clients/TypeScript
```

### CI guardrail for generated clients
A GitHub Action runs on pull requests to main to ensure the generated clients are up to date. If your PR modifies the API or the OpenAPI document but you forgot to regenerate clients, the workflow will fail when it detects diffs under `src/clients/` after running Kiota.

To fix a failing PR:
- Regenerate the OpenAPI document if needed (see above).
- Regenerate the clients with Kiota (C# and/or TypeScript commands above).
- Commit and push the changes.
