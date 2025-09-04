from markitdown import MarkItDown
import tempfile, os
from pathlib import Path
from typing import Annotated

class ConverterService:
    def __init__(self, mkd: MarkItDown | None = None):
        self._mkd = mkd or MarkItDown()

    def convert_path(self, path: str) -> str:
        result = self._mkd.convert(path)
        return result.text_content

    def convert_bytes(self, filename: str, data: bytes) -> str:
        suffix = Path(filename).suffix or ""
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(data)
                temp_path = tmp.name
            return self.convert_path(temp_path)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

    def convert_url(self, url: str) -> str:
        result = self._mkd.convert(url)
        return result.text_content

SUPPORTED_FORMATS: list[str] = [
    ".pdf", ".docx", ".pptx", ".xlsx",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff",
    ".html", ".htm", ".xml", ".csv", ".json",
    ".zip", ".txt", ".md",
]
