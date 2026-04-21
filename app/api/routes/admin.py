import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.core.config import get_settings
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.user import User
from app.schemas.admin import AdminDashboardResponse, OrdersListResponse, UsersListResponse
from app.schemas.order import OrderItemResponse, OrderResponse
from app.schemas.product import ProductCreateRequest, ProductResponse, ProductUpdateRequest
from app.schemas.user import UserProfileResponse

router = APIRouter(prefix="/api/admin", tags=["Admin"])
settings = get_settings()


@router.get("/dashboard", response_model=AdminDashboardResponse)
def dashboard(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    users_count = db.query(User).count()
    products_count = db.query(Product).count()
    orders = db.query(Order).all()
    return AdminDashboardResponse(
        users_count=users_count,
        products_count=products_count,
        orders_count=len(orders),
        revenue=round(sum(order.total_amount for order in orders), 2),
    )


@router.get("/users", response_model=UsersListResponse)
def users(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    all_users = db.query(User).order_by(User.created_at.desc()).all()
    return UsersListResponse(users=[UserProfileResponse.model_validate(user) for user in all_users])


@router.get("/orders", response_model=OrdersListResponse)
def orders(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    all_orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return OrdersListResponse(
        orders=[
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
            for order in all_orders
        ]
    )


@router.put("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status: OrderStatus,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
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


@router.post("/products", response_model=ProductResponse)
def create_product(
    payload: ProductCreateRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.post("/products/upload-image")
async def upload_product_image(
    _: User = Depends(require_admin),
    image: UploadFile = File(...),
):
    extension = image.filename.split(".")[-1].lower()
    if extension not in {"jpg", "jpeg", "png", "webp"}:
        raise HTTPException(status_code=400, detail="Only jpg/jpeg/png/webp files are allowed")

    os.makedirs(settings.uploads_dir, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}.{extension}"
    full_path = os.path.join(settings.uploads_dir, unique_name)

    content = await image.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(status_code=400, detail="Image exceeds upload size limit")
    with open(full_path, "wb") as destination:
        destination.write(content)
    return {"image_url": f"/static/uploads/{unique_name}"}


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductUpdateRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}")
def delete_product(product_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}
