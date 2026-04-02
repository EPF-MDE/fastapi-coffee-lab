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
def show_home(request: Request, admin: int = 0):
    return templates.TemplateResponse(
        request,
        "index.html",
        context={
            "coffees": coffees,
            "welcome_message": "Have one, not a hundred!",
            "admin": admin,
        },
    )


@app.get("/coffees")
def create_coffee_page(request: Request, admin: int = 0):
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not admin action",
        )

    return templates.TemplateResponse(
        request,
        "admin.html",
        context={"coffee": {}},
    )


@app.get("/coffees/{id}")
def update_coffee_page(request: Request, id: int = None, admin: int = 0):
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not admin action",
        )

    return templates.TemplateResponse(
        request,
        "admin.html",
        context={"coffee": coffees[id], "id": id},
    )


@app.post("/coffees")
def create_coffee_action(
    name: Annotated[str, Form()],
    price: Annotated[float, Form()],
    is_offer: Annotated[bool, Form()],
    admin: int = 0,
):
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not admin action",
        )

    coffee = {"name": name, "price": price, "is_offer": is_offer}

    coffees.append(coffee)

    return RedirectResponse("/?admin=1", status_code=303)


@app.post("/coffees/{id}")
def update_coffee_action(
    id: int,
    name: Annotated[str, Form()],
    price: Annotated[float, Form()],
    is_offer: Annotated[bool, Form()],
    admin: int = 0,
):
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not admin action",
        )

    new_coffee = {
        "name": name,
        "price": price,
        "is_offer": is_offer,
    }

    coffees[id].update(new_coffee)

    return RedirectResponse("/?admin=1", status_code=303)
