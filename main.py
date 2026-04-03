from typing import Annotated

from fastapi import FastAPI, Request, Form, status, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, computed_field, TypeAdapter

app = FastAPI()


class Coffee(BaseModel):
    name: str
    price: float
    quantity: int = Field(gte=0)
    is_offer: bool | None = None


class PublicCoffee(Coffee):
    quantity: int = Field(gte=0, exclude=True)

    @computed_field
    @property
    def out_of_stock(self) -> bool:
        return self.quantity == 0


coffees: list[Coffee]
coffees = [
    Coffee(name="Espresso", price=1.0, is_offer=True, quantity=2),
    Coffee(name="Latte", price=3.0, is_offer=False, quantity=5),
]


def make_money():
    money: float
    money = 10.0

    def get_money() -> float:
        return money

    def set_money(new_money: float) -> float:
        nonlocal money
        money = new_money

    return (get_money, set_money)


get_money, set_money = make_money()

templates = Jinja2Templates(directory="templates")


@app.get("/")
def show_home(request: Request, purchased_coffee: int = None, admin: int = 0):
    coffee_model = PublicCoffee if not admin else Coffee
    validated_coffees = TypeAdapter(list[coffee_model]).validate_python(
        [coffee.model_dump() for coffee in coffees]
    )

    message = (
        "Have one, not a hundred! 💯"
        if purchased_coffee is None
        else f"Enjoy your {coffees[purchased_coffee].name}! ☺️"
    )

    return templates.TemplateResponse(
        request,
        "index.html",
        context={
            "coffees": validated_coffees,
            "message": message,
            "money": get_money(),
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
    quantity: Annotated[int, Form()],
    admin: int = 0,
):
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not admin action",
        )

    coffee = Coffee(name=name, price=price, is_offer=is_offer, quantity=quantity)

    coffees.append(coffee)

    return RedirectResponse("/?admin=1", status_code=303)


@app.post("/coffees/{id}")
def update_coffee_action(
    id: int,
    name: Annotated[str, Form()],
    price: Annotated[float, Form()],
    is_offer: Annotated[bool, Form()],
    quantity: Annotated[int, Form()],
    admin: int = 0,
):
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not admin action",
        )

    new_coffee = Coffee(name=name, price=price, is_offer=is_offer, quantity=quantity)

    coffees[id] = coffees[id].model_copy(update=new_coffee.model_dump())

    return RedirectResponse("/?admin=1", status_code=303)


@app.post("/coffees/{id}/buy")
def buy_coffee(id: int, admin: int = 0):
    if admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Coffee is free for you!",
        )

    coffee = coffees[id]

    money = get_money()
    new_money = money - coffee.price

    if new_money < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough money for that coffee! We can offer a glass of water instead...",
        )

    new_quantity = coffee.quantity - 1

    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already out of stock, cannot buy that coffee!",
        )

    set_money(new_money)

    new_coffee = coffee.model_copy(update={"quantity": new_quantity})

    coffees[id] = new_coffee

    return RedirectResponse(f"/?purchased_coffee={id}", status_code=303)
