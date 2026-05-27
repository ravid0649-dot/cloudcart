from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Cart Service")

cart = []

class CartItem(BaseModel):
    product_id: int
    quantity: int

@app.get("/")
def home():
    return {"service": "Cart Service", "status": "running"}

@app.post("/cart")
def add_to_cart(item: CartItem):
    cart.append(item.dict())
    return {"message": "Product added to cart", "cart": cart}

@app.get("/cart")
def get_cart():
    return {"cart": cart}

@app.delete("/cart")
def clear_cart():
    cart.clear()
    return {"message": "Cart cleared successfully"}
