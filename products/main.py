from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from redis_om.model.model import NotFoundError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_host = os.environ.get("REDIS_HOST")
redis_port = os.environ.get("REDIS_PORT")
redis_password = os.environ.get("REDIS_PASSWORD")

redis = get_redis_connection(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    decode_responses=True,
)

class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis

@app.get("/products")
async def get_products():
    return list(map(formatProduct, Product.all_pks()))

def formatProduct(pk: str):
    product = Product.get(pk)

    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity
    }


@app.post("/products")
async def create_product(product: Product):
    return product.save()


@app.get("/products/{id}")
async def get_product_by_id(id: str):
    try:
        product = Product.get(id)
    except NotFoundError:
        return JSONResponse(status_code=404, content={"message": "Product not found"})

    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity
    }


@app.delete("/products/{id}")
async def delete_product_by_id(id: str):
    try:
        product = Product.get(id)
    except NotFoundError:
        return JSONResponse(status_code=404, content={"message": "Product not found"})

    product.delete(product.pk)

    return JSONResponse(status_code=200, content={"message": "Product deleted"})
