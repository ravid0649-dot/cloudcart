from datetime import datetime

from pydantic import BaseModel, Field


class PlaceOrderRequest(BaseModel):
    shipping_address: str = Field(min_length=10, max_length=500)


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    line_total: float


class OrderResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    shipping_address: str
    created_at: datetime
    items: list[OrderItemResponse]
