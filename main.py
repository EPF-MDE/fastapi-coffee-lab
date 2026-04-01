from typing import Annotated

from fastapi import FastAPI, Request, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()


class Coffee(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None


coffees: list[Coffee]
coffees = [
    {"name": "Espresso", "price": 1, "is_offer": True},
    {"name": "Latte", "price": 3, "is_offer": False},
]

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def show_home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        context={"coffees": coffees, "welcome_message": "Have one, not a hundred!"},
    )


@app.get("/admin", response_class=HTMLResponse)
def show_admin(request: Request):
    return templates.TemplateResponse(
        request,
        "admin.html",
        context={"coffees": coffees},
    )


@app.get("/coffees/{coffee_id}")
def read_coffee(coffee_id: int, quantity: int | None = None):
    return {"coffee_id": coffee_id, "coffee": coffees[coffee_id], "quantity": quantity}


@app.post("/coffees")
def create_coffee(
    name: Annotated[str, Form()],
    price: Annotated[float, Form()],
    is_offer: Annotated[bool, Form()],
    admin: Annotated[bool, Form()] = None,
):
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not admin action",
        )

    coffee = {"name": name, "price": price, "is_offer": is_offer}

    coffees.append(coffee)

    return RedirectResponse("/admin", status_code=303)


@app.put("/coffees/{coffee_id}")
def update_coffee(coffee_id: int, coffee: Coffee):
    # print("coffees", coffees)

    coffees[coffee_id].update(coffee)

    # print("coffees[coffee_id]", coffees[coffee_id])

    response = {"coffee_name": coffees[coffee_id]["name"], "coffee_id": coffee_id}

    # print("response", response)

    return response
