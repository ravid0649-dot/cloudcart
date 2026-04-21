from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderItemResponse, OrderResponse, PlaceOrderRequest

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("/checkout", response_model=OrderResponse)
def checkout(
    payload: PlaceOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order_total = 0.0
    for item in cart_items:
        if item.product.stock < item.quantity:
            raise HTTPException(
                status_code=400, detail=f"Product '{item.product.name}' is out of stock"
            )
        order_total += item.quantity * item.product.price

    order = Order(
        user_id=current_user.id,
        total_amount=round(order_total, 2),
        shipping_address=payload.shipping_address,
    )
    db.add(order)
    db.flush()

    for item in cart_items:
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.product.price,
            )
        )
        item.product.stock -= item.quantity
        db.delete(item)

    db.commit()
    db.refresh(order)
    return OrderResponse(
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


@router.get("", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()
    return [
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
        for order in orders
    ]
