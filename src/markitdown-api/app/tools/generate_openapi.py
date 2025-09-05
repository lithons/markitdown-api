# Utility to generate OpenAPI schema to a file (or stdout) without running the server
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi.openapi.utils import get_openapi

# Import the FastAPI app
from app.main import app


def build_schema(server_url: Optional[str] = None) -> Dict[str, Any]:
    # Include title, version, description, and optional servers for better client generation
    # Kiota requires a servers entry; default to localhost if none provided.
    servers: Optional[List[Dict[str, str]]] = None
    base_url = (server_url or "http://localhost:8000").strip()
    if base_url:
        servers = [{"url": base_url.rstrip("/")}]  # avoid trailing slash issues
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=getattr(app, "description", None),
        routes=app.routes,
        servers=servers,
    )
    # Post-process: Kiota doesn't support format: uri, so drop it for UrlPayload.url to reduce warnings.
    try:
        url_schema = schema["components"]["schemas"]["UrlPayload"]["properties"]["url"]
        if isinstance(url_schema, dict):
            url_schema.pop("format", None)
    except Exception:
        # Best effort; if structure changes, ignore silently
        pass
    return schema


essential_default_output = Path(__file__).resolve().parents[2] / "openapi.json"


def write_schema(schema: Dict[str, Any], output: Optional[Path | str]) -> None:
    # If output is '-', write to stdout
    if output is None or str(output) == "-":
        json.dump(schema, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return

    # Ensure parent directory exists and write file
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate OpenAPI schema from FastAPI app.\n\n"
            "Examples:\n"
            "  python -m app.tools.generate_openapi -o openapi.json\n"
            "  python -m app.tools.generate_openapi -o - --server-url https://api.example.com\n"
        )
    )
    parser.add_argument(
        "--output",
        "-o",
        default=str(essential_default_output),
        help="Path to write openapi.json, or '-' for stdout (default: project root openapi.json)",
    )
    parser.add_argument(
        "--server-url",
        dest="server_url",
        default=os.environ.get("PUBLIC_BASE_URL", ""),
        help="Optional server URL to include in the OpenAPI 'servers' section (defaults to env PUBLIC_BASE_URL if set)",
    )
    args = parser.parse_args()

    server_url = args.server_url.strip() or None
    schema = build_schema(server_url=server_url)
    write_schema(schema, args.output)


if __name__ == "__main__":
    main()
