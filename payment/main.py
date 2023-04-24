from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from dotenv import load_dotenv
import os
from starlette.requests import Request
import httpx

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

products_url = os.environ.get("PRODUCTS_SERVICE_URL")

redis = get_redis_connection(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    decode_responses=True,
)

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str # pendind | completed ? refunded

    class Meta:
        database = redis


@app.post("/orders")
async def create_order(request: Request):
    body = await request.json()
    url = products_url + "/products/" + body["id"]

    print(url)
    response = httpx.get(url)

    if response.status_code == 200:
        # The product was found
        product_data = response.json()
        return (product_data)
    else:
    # The product was not found
      print("Product not found")
