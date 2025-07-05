# app/schemas/common.py
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

# Define a TypeVar for the data payload
T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """
    Common API response template.
    """
    status_code: int
    message: str
    data: Optional[T] = None
    success: bool = True
    error: Optional[str] = None