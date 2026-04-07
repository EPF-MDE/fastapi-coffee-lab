from typing import Annotated
import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, Form, status, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Field, Session, SQLModel, create_engine, select

load_dotenv()


class CoffeeBase(SQLModel):
    name: str = Field(index=True)
    price: float
    is_offer: bool | None = Field(default=None, index=True)


class Coffee(CoffeeBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    quantity: int = Field(gt=0)


class CoffeeCreate(CoffeeBase):
    quantity: int = Field(gt=0)


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

connect_args = {"check_same_thread": False}
engine = create_engine(os.environ.get("DATABASE_URL"), connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def show_home(
    request: Request,
    session: SessionDep,
    purchased_coffee_id: int = None,
    admin: int = 0,
):
    coffees = session.exec(select(Coffee)).all()

    message = "Have one, not a hundred! 💯"

    if purchased_coffee_id:
        purchased_coffee = session.get(Coffee, purchased_coffee_id)
        message = f"Enjoy your {purchased_coffee.name}! ☺️"

    return templates.TemplateResponse(
        request,
        "index.html",
        context={
            "coffees": coffees,
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
        context={"coffee": {}, "admin": admin},
    )


@app.get("/coffees/{id}")
def update_coffee_page(
    request: Request, session: SessionDep, id: int = None, admin: int = 0
):
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not admin action",
        )

    coffee = session.get(Coffee, id)

    if not coffee:
        raise HTTPException(status_code=404, detail="Coffee not found")

    return templates.TemplateResponse(
        request,
        "admin.html",
        context={"coffee": coffee, "admin": admin},
    )


@app.post("/coffees")
def create_coffee_action(
    session: SessionDep,
    data: Annotated[CoffeeCreate, Form()],
    admin: int = 0,
):
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not admin action",
        )

    coffee = Coffee(**data.model_dump())

    session.add(coffee)
    session.commit()
    session.refresh(coffee)

    return RedirectResponse("/?admin=1", status_code=303)


@app.post("/coffees/{id}")
def update_coffee_action(
    session: SessionDep,
    id: int,
    data: Annotated[Coffee, Form()],
    admin: int = 0,
):
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not admin action",
        )

    coffee_db = session.get(Coffee, id)

    if not coffee_db:
        raise HTTPException(status_code=404, detail="Coffee not found")

    # Convert 1/0 to True/False
    data.is_offer = bool(data.is_offer)

    coffee_data = data.model_dump(exclude_unset=True)
    coffee_db.sqlmodel_update(coffee_data)
    session.add(coffee_db)
    session.commit()
    session.refresh(coffee_db)

    return RedirectResponse("/?admin=1", status_code=303)


@app.post("/coffees/{id}/buy")
def buy_coffee(session: SessionDep, id: int, admin: int = 0):
    if admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Coffee is free for you!",
        )

    coffee_db = session.get(Coffee, id)

    if not coffee_db:
        raise HTTPException(status_code=404, detail="Coffee not found")

    money = get_money()
    new_money = money - coffee_db.price

    if new_money < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough money for that coffee! We can offer a glass of water instead...",
        )

    new_quantity = coffee_db.quantity - 1

    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already out of stock, cannot buy that coffee!",
        )

    set_money(new_money)

    coffee_db.sqlmodel_update({"quantity": new_quantity})
    session.add(coffee_db)
    session.commit()
    session.refresh(coffee_db)

    return RedirectResponse(f"/?purchased_coffee_id={id}", status_code=303)
