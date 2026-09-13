from typing import Any

from pydantic import BaseModel


class ApiResponse[T](BaseModel):
    success: bool
    message: str
    data: T | None = None
    detail: Any | None = None
