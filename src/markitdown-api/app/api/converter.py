from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import Annotated
import logging

from app.models.converter import (
    ConvertFileResponse, ConvertUrlResponse, SupportedFormatsResponse
)
from app.services.converter_service import ConverterService, SUPPORTED_FORMATS

logger = logging.getLogger(__name__)
router = APIRouter(tags=["convert"])

# Simple “DI” provider (could later swap for a real container)
def get_converter_service() -> ConverterService:
    return ConverterService()

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@router.post(
    "/convert",
    response_model=ConvertFileResponse,
    status_code=status.HTTP_200_OK,
)
async def convert_document(
    file: UploadFile = File(...),
    svc: ConverterService = Depends(get_converter_service),
):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Note: UploadFile.size may be None depending on client; guard when present
    if getattr(file, "size", None) and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB")

    try:
        content = await file.read()
        markdown = svc.convert_bytes(file.filename, content)
        return ConvertFileResponse(filename=file.filename, size=len(content), markdown=markdown)
    except Exception as e:
        logger.exception("Error processing file %s", getattr(file, "filename", "<unknown>"))
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}") from e

class UrlPayload(BaseModel):
    url: HttpUrl

@router.post(
    "/convert-url",
    response_model=ConvertUrlResponse,
    status_code=status.HTTP_200_OK,
)
async def convert_from_url(
    payload: UrlPayload,
    svc: ConverterService = Depends(get_converter_service),
):
    if not payload.url:
        raise HTTPException(status_code=400, detail="No URL provided")
    try:
        markdown = svc.convert_url(str(payload.url))
        return ConvertUrlResponse(url=str(payload.url), markdown=markdown)
    except Exception as e:
        logger.exception("Error processing URL %s", payload.url)
        raise HTTPException(status_code=500, detail=f"Error processing URL: {e}") from e

@router.get(
    "/supported-formats",
    response_model=SupportedFormatsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_supported_formats():
    return SupportedFormatsResponse(
        supported_formats=SUPPORTED_FORMATS,
        note="This list may not be exhaustive. MarkItDown supports many formats.",
    )
