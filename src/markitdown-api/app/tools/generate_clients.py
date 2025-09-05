# Generate OpenAPI and both C# and TypeScript clients with one command
from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Reuse existing OpenAPI generator
from . import generate_openapi as go

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OPENAPI_PATH = REPO_ROOT / "openapi.json"
DEFAULT_CSHARP_OUT = REPO_ROOT.parent / "clients" / "csharp"
DEFAULT_TS_OUT = REPO_ROOT.parent / "clients" / "TypeScript"


def which(cmd: str) -> str | None:
    return shutil.which(cmd)


def run(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        raise
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed with exit code {e.returncode}: {' '.join(cmd)}") from e


def ensure_kiota_available(kiota_cmd: str) -> None:
    if which(kiota_cmd) is None:
        raise RuntimeError(
            "Kiota CLI not found. Please install it and ensure it is on PATH. See https://github.com/microsoft/kiota.\n"
            "Example: dotnet tool install --global Microsoft.OpenApi.Kiota"
        )


def generate_openapi(output: Path, server_url: str | None) -> None:
    schema = go.build_schema(server_url=server_url)
    go.write_schema(schema, str(output))


def generate_clients(openapi_path: Path, kiota_cmd: str, csharp_out: Path, ts_out: Path) -> None:
    # C#
    csharp_out.mkdir(parents=True, exist_ok=True)
    run([
        kiota_cmd,
        "generate",
        "-d", str(openapi_path),
        "-l", "CSharp",
        "-c", "MarkItDownApiClient",
        "-n", "Lithons.MarkItDown",
        "-o", str(csharp_out),
    ])
    # TypeScript
    ts_out.mkdir(parents=True, exist_ok=True)
    run([
        kiota_cmd,
        "generate",
        "-d", str(openapi_path),
        "-l", "TypeScript",
        "-c", "MarkItDownApiClient",
        "-n", "Lithons",
        "-o", str(ts_out),
    ])


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate OpenAPI and both C# and TypeScript clients.\n\n"
            "Examples:\n"
            "  python -m app.tools.generate_clients\n"
            "  PUBLIC_BASE_URL=https://api.example.com python -m app.tools.generate_clients\n"
            "  python -m app.tools.generate_clients --skip-openapi --openapi src/markitdown-api/openapi.json\n"
        )
    )
    parser.add_argument("--openapi", "-d", default=str(DEFAULT_OPENAPI_PATH), help="Path to openapi.json to write/read")
    parser.add_argument("--skip-openapi", action="store_true", help="Skip regenerating the OpenAPI document")
    parser.add_argument("--server-url", default=os.environ.get("PUBLIC_BASE_URL", ""), help="Server URL to include in OpenAPI (or env PUBLIC_BASE_URL)")
    parser.add_argument("--kiota", default="kiota", help="Kiota CLI command name or path (default: kiota)")
    parser.add_argument("--csharp-out", default=str(DEFAULT_CSHARP_OUT), help="Output directory for C# client")
    parser.add_argument("--ts-out", default=str(DEFAULT_TS_OUT), help="Output directory for TypeScript client")

    args = parser.parse_args()

    openapi_path = Path(args.openapi).resolve()
    csharp_out = Path(args.csharp_out).resolve()
    ts_out = Path(args.ts_out).resolve()

    # Ensure Kiota is available before long operations
    ensure_kiota_available(args.kiota)

    # Generate OpenAPI unless skipped
    if not args.skip_openapi:
        server_url = args.server_url.strip() or None
        generate_openapi(openapi_path, server_url)
        print(f"Wrote OpenAPI to {openapi_path}")
    else:
        if not openapi_path.exists():
            print(f"--skip-openapi set but OpenAPI file does not exist: {openapi_path}", file=sys.stderr)
            sys.exit(2)

    # Generate both clients
    print("Generating C# and TypeScript clients with Kiota...")
    generate_clients(openapi_path, args.kiota, csharp_out, ts_out)
    print("Client generation complete:")
    print(f"  C#:        {csharp_out}")
    print(f"  TypeScript:{ts_out}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
