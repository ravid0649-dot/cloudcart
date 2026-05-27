from fastapi import FastAPI

app = FastAPI(title="Product Service")

products = [
    {"id": 1, "name": "Laptop", "price": 55000, "category": "Electronics"},
    {"id": 2, "name": "Smartphone", "price": 25000, "category": "Electronics"},
    {"id": 3, "name": "Headphones", "price": 2500, "category": "Accessories"},
    {"id": 4, "name": "Shoes", "price": 3000, "category": "Fashion"}
]

@app.get("/")
def home():
    return {"service": "Product Service", "status": "running"}

@app.get("/products")
def get_products():
    return products

@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return {"error": "Product not found"}
