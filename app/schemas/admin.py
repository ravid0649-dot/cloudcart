from pydantic import BaseModel

from app.schemas.order import OrderResponse
from app.schemas.user import UserProfileResponse


class AdminDashboardResponse(BaseModel):
    users_count: int
    products_count: int
    orders_count: int
    revenue: float


class UsersListResponse(BaseModel):
    users: list[UserProfileResponse]


class OrdersListResponse(BaseModel):
    orders: list[OrderResponse]
