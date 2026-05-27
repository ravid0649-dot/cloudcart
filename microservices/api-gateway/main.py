from fastapi import FastAPI
import httpx

app = FastAPI(title="CloudCart API Gateway")

PRODUCT_SERVICE = "http://product-service:8001"
CART_SERVICE = "http://cart-service:8002"
ORDER_SERVICE = "http://order-service:8003"

@app.get("/")
def home():
    return {
        "project": "CloudCart Microservice Based Web Service",
        "status": "API Gateway running",
        "services": ["Product Service", "Cart Service", "Order Service"]
    }

@app.get("/products")
async def get_products():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PRODUCT_SERVICE}/products")
        return response.json()

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PRODUCT_SERVICE}/products/{product_id}")
        return response.json()

@app.get("/cart")
async def get_cart():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CART_SERVICE}/cart")
        return response.json()

@app.post("/cart")
async def add_to_cart(item: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{CART_SERVICE}/cart", json=item)
        return response.json()

@app.delete("/cart")
async def clear_cart():
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{CART_SERVICE}/cart")
        return response.json()

@app.get("/orders")
async def get_orders():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ORDER_SERVICE}/orders")
        return response.json()

@app.post("/orders")
async def place_order(order: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{ORDER_SERVICE}/orders", json=order)
        return response.json()
