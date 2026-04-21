from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderItemResponse, OrderResponse
from app.schemas.user import UpdateProfileRequest, UserProfileResponse

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserProfileResponse)
def update_profile(
    payload: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/orders", response_model=list[OrderResponse])
def get_order_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    response: list[OrderResponse] = []
    for order in orders:
        response.append(
            OrderResponse(
                id=order.id,
                total_amount=order.total_amount,
                status=order.status.value,
                shipping_address=order.shipping_address,
                created_at=order.created_at,
                items=[
                    OrderItemResponse(
                        product_id=item.product_id,
                        product_name=item.product.name,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        line_total=item.quantity * item.unit_price,
                    )
                    for item in order.items
                ],
            )
        )
    return response
