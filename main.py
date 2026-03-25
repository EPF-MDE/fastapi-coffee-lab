from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Coffee(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None


@app.get("/")
def read_home():
    return {"Hello": "World"}


@app.get("/coffees/{coffee_id}")
def read_coffee(coffee_id: int, q: str | None = None):
    return {"coffee_id": coffee_id, "q": q}


@app.put("/coffees/{coffee_id}")
def update_coffee(coffee_id: int, coffee: Coffee):
    return {"coffee_name": coffee.name, "coffee_id": coffee_id}
