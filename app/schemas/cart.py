from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class AddCartItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, le=20, default=1)


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(gt=0, le=20)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    unit_price: float
    quantity: int
    line_total: float
    image_url: Optional[str] = None


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    cart_total: float
