from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Order Service")

orders = []

class Order(BaseModel):
    user_name: str
    product_id: int
    quantity: int
    address: str

@app.get("/")
def home():
    return {"service": "Order Service", "status": "running"}

@app.post("/orders")
def place_order(order: Order):
    new_order = {
        "order_id": len(orders) + 1,
        "user_name": order.user_name,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "address": order.address,
        "status": "Order Placed",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    orders.append(new_order)
    return {"message": "Order placed successfully", "order": new_order}

@app.get("/orders")
def get_orders():
    return {"orders": orders}
