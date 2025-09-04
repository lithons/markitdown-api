from pydantic import BaseModel

class ConvertFileResponse(BaseModel):
    filename: str
    size: int
    markdown: str
    status: str = "success"

class ConvertUrlResponse(BaseModel):
    url: str
    markdown: str
    status: str = "success"

class SupportedFormatsResponse(BaseModel):
    supported_formats: list[str]
    note: str | None = None