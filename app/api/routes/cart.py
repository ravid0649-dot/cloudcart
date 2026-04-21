from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import AddCartItemRequest, CartItemResponse, CartResponse, UpdateCartItemRequest

router = APIRouter(prefix="/api/cart", tags=["Cart"])


def build_cart_response(items: list[CartItem]) -> CartResponse:
    mapped_items: list[CartItemResponse] = []
    total = 0.0
    for item in items:
        line_total = item.quantity * item.product.price
        total += line_total
        mapped_items.append(
            CartItemResponse(
                id=item.id,
                product_id=item.product.id,
                product_name=item.product.name,
                unit_price=item.product.price,
                quantity=item.quantity,
                line_total=line_total,
                image_url=item.product.image_url,
            )
        )
    return CartResponse(items=mapped_items, cart_total=round(total, 2))


@router.get("", response_model=CartResponse)
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    return build_cart_response(items)


@router.post("", response_model=CartResponse)
def add_to_cart(
    payload: AddCartItemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < payload.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    existing = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id, CartItem.product_id == payload.product_id)
        .first()
    )
    if existing:
        existing.quantity += payload.quantity
    else:
        db.add(CartItem(user_id=current_user.id, product_id=payload.product_id, quantity=payload.quantity))

    db.commit()
    items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    return build_cart_response(items)


@router.put("/{item_id}", response_model=CartResponse)
def update_cart_item(
    item_id: int,
    payload: UpdateCartItemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    if item.product.stock < payload.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    item.quantity = payload.quantity
    db.commit()
    items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    return build_cart_response(items)


@router.delete("/{item_id}", response_model=CartResponse)
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(item)
    db.commit()
    items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    return build_cart_response(items)
