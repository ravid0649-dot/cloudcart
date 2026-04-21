from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str = Field(min_length=5)
    category: str = Field(min_length=2, max_length=80)
    price: float = Field(gt=0)
    rating: float = Field(ge=0, le=5, default=0)
    stock: int = Field(ge=0, default=0)
    image_url: Optional[str] = None


class ProductCreateRequest(ProductBase):
    pass


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    description: Optional[str] = Field(default=None, min_length=5)
    category: Optional[str] = Field(default=None, min_length=2, max_length=80)
    price: Optional[float] = Field(default=None, gt=0)
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    stock: Optional[int] = Field(default=None, ge=0)
    image_url: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
