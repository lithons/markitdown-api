# MarkItDown REST API Docker Container

A containerized REST API for Microsoft's MarkItDown library that converts various document formats to Markdown.

## Features

- Convert documents to Markdown via REST API
- Support for PDF, DOCX, PPTX, XLSX, images, HTML, and more
- Docker containerized for easy deployment
- FastAPI with automatic API documentation
- File upload and URL conversion support

## Quick Start

1. **Build and run with the script:**

   ```bash
   chmod +x build_and_run.sh
   ./build_and_run.sh
   ```

2. **Or use Docker Compose:**

   ```bash
   docker-compose up --build
   ```

3. **Or build manually:**
   ```bash
   docker build -t markitdown-api .
   docker run -p 8000:8000 markitdown-api
   ```

## API Endpoints

- `GET /` - Health check
- `POST /convert` - Upload file for conversion
- `POST /convert-url` - Convert document from URL
- `GET /supported-formats` - List supported formats
- `GET /docs` - Interactive API documentation

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

- Port: 8000 (configurable)
- Max file size: 50MB
- Supported formats: PDF, Office docs, images, HTML, and more

## Requirements

- Docker
- 2GB+ RAM recommended for processing large documents

## OpenAPI and Client Generation

This repository uses an OpenAPI schema and Microsoft Kiota to generate API clients that live under `src/clients/`. Changes to the API must be reflected in the generated clients.

### Generate openapi.json
Use the provided tool to regenerate the OpenAPI document from the FastAPI app without running the server:

```bash
# From the repo root
# Writes to src/markitdown-api/openapi.json by default
python -m app.tools.generate_openapi

# Optionally include a server URL in the OpenAPI 'servers' section
PUBLIC_BASE_URL=https://api.example.com python -m app.tools.generate_openapi

# Or write to a specific file (or '-' for stdout)
python -m app.tools.generate_openapi -o src/markitdown-api/openapi.json
```

### Generate clients with Kiota
Prerequisites: Install the Kiota CLI. You can install it locally or rely on the GitHub Action (see below).

Generate both C# and TypeScript clients in one command (also regenerates openapi.json by default):
```bash
# From the repo root
python -m app.tools.generate_clients

# Optionally include a server URL in the OpenAPI 'servers' section
PUBLIC_BASE_URL=https://api.example.com python -m app.tools.generate_clients

# Skip regenerating openapi.json and use an existing file
python -m app.tools.generate_clients --skip-openapi --openapi src/markitdown-api/openapi.json
```

Generate only C# client:
```bash
kiota generate -d src/markitdown-api/openapi.json -l CSharp -c PythonApiClient -n Lithons.PythonApi -o src/clients/csharp
```

Generate only TypeScript client:
```bash
kiota generate -d src/markitdown-api/openapi.json -l TypeScript -c PythonApiClient -n LithonsPythonApi -o src/clients/typescript
```

### CI guardrail for generated clients
A GitHub Action runs on pull requests to main to ensure the generated clients are up to date. If your PR modifies the API or the OpenAPI document but you forgot to regenerate clients, the workflow will fail when it detects diffs under `src/clients/` after running Kiota.

To fix a failing PR:
- Regenerate the OpenAPI document if needed (see above).
- Regenerate the clients with Kiota (C# and/or TypeScript commands above).
- Commit and push the changes.
