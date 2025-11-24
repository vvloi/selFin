"""Common schemas."""
from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = 1
    size: int = 50
