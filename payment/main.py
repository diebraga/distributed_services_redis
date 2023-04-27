from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from dotenv import load_dotenv
import os
from starlette.requests import Request
import httpx
from redis_om.model.model import NotFoundError

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

    class Meta:
        database = redis

@app.get("/orders")
async def get_orders():
    try:
        order_pks = Order.all_pks()
        orders = list(map(formatOrder, order_pks))
        return orders
    except Exception as e:
        print(f"Error retrieving orders from Redis: {e}")
        return {"error": "Unable to retrieve orders"}

def formatOrder(pk: str):
    try:
        order = Order.get(pk)
        formatted_order = {
            "pk": order.pk,
            "product_id": order.product_id,
            "price": order.price,
            "fee": order.fee,
            "total": order.total,
            "quantity": order.quantity
        }
        return formatted_order
    except Exception as e:
        print(f"Error formatting order with pk {pk}: {e}")
        return {"error": f"Unable to format order with pk {pk}"}


@app.post("/orders")
async def create_order(request: Request):
    body = await request.json()
    url = products_url + "/products/" + body["id"]

    product_response = httpx.get(url)

    if product_response.status_code == 200:
        product_data = product_response.json()
        order = Order(
            product_id=body["id"],
            price=product_data["price"],
            fee=0.2 * product_data["price"],
            total=1.2 * product_data["price"],
            quantity=body["quantity"],
        )

        order.save()
        return order
    else:
        # The product was not found
        return "Product not found"

