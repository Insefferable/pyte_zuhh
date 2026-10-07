from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.database import get_db
from app.models.pizza import Pizza
from app.models.topping import Topping
from app.models.pizza_topping import PizzaTopping
from app.schemas.pizza import PizzaCreate, PizzaUpdate, PizzaToppingsUpdate, PizzaResponse
from app.schemas.topping import ToppingResponse

router = APIRouter(prefix="/api/pizzas", tags=["pizzas"])


def to_response(pizza: Pizza) -> PizzaResponse:
    return PizzaResponse(
        id=pizza.id,
        name=pizza.name,
        description=pizza.description,
        price=pizza.price,
        toppings=[
            ToppingResponse(id=pt.topping.id, name=pt.topping.name)
            for pt in pizza.pizza_toppings
        ],
    )


def get_pizza_with_toppings(pizza_id: int, db: Session) -> Pizza | None:
    return (
        db.query(Pizza)
        .options(joinedload(Pizza.pizza_toppings).joinedload(PizzaTopping.topping))
        .filter(Pizza.id == pizza_id)
        .first()
    )


@router.get("", response_model=list[PizzaResponse])
def get_pizzas(db: Session = Depends(get_db)):
    pizzas = (
        db.query(Pizza)
        .options(joinedload(Pizza.pizza_toppings).joinedload(PizzaTopping.topping))
        .all()
    )
    return [to_response(p) for p in pizzas]


@router.get("/{pizza_id}", response_model=PizzaResponse)
def get_pizza(pizza_id: int, db: Session = Depends(get_db)):
    pizza = get_pizza_with_toppings(pizza_id, db)
    if not pizza:
        raise HTTPException(status_code=404, detail=f"Pizza with id {pizza_id} not found.")
    return to_response(pizza)


@router.post("", response_model=PizzaResponse, status_code=status.HTTP_201_CREATED)
def create_pizza(dto: PizzaCreate, db: Session = Depends(get_db)):
    name = dto.name.strip()

    duplicate = db.query(Pizza).filter(func.lower(Pizza.name) == name.lower()).first()
    if duplicate:
        raise HTTPException(status_code=409, detail=f"A pizza named '{name}' already exists.")

    topping_ids = list(set(dto.topping_ids))
    existing_toppings = db.query(Topping).filter(Topping.id.in_(topping_ids)).all()

    if len(existing_toppings) != len(topping_ids):
        found_ids = {t.id for t in existing_toppings}
        missing = [i for i in topping_ids if i not in found_ids]
        raise HTTPException(status_code=400, detail=f"Invalid topping id(s): {missing}")

    pizza = Pizza(name=name, description=dto.description, price=dto.price)
    pizza.pizza_toppings = [PizzaTopping(topping_id=t.id) for t in existing_toppings]

    db.add(pizza)
    db.commit()
    db.refresh(pizza)

    pizza = get_pizza_with_toppings(pizza.id, db)
    return to_response(pizza)


@router.put("/{pizza_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_pizza(pizza_id: int, dto: PizzaUpdate, db: Session = Depends(get_db)):
    pizza = db.query(Pizza).filter(Pizza.id == pizza_id).first()
    if not pizza:
        raise HTTPException(status_code=404, detail=f"Pizza with id {pizza_id} not found.")

    name = dto.name.strip()

    duplicate = db.query(Pizza).filter(
        Pizza.id != pizza_id, func.lower(Pizza.name) == name.lower()
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail=f"A pizza named '{name}' already exists.")

    pizza.name = name
    pizza.description = dto.description
    pizza.price = dto.price

    db.commit()
    return None


@router.put("/{pizza_id}/toppings", status_code=status.HTTP_204_NO_CONTENT)
def update_pizza_toppings(pizza_id: int, dto: PizzaToppingsUpdate, db: Session = Depends(get_db)):
    pizza = get_pizza_with_toppings(pizza_id, db)
    if not pizza:
        raise HTTPException(status_code=404, detail=f"Pizza with id {pizza_id} not found.")

    topping_ids = list(set(dto.topping_ids))
    existing_toppings = db.query(Topping).filter(Topping.id.in_(topping_ids)).all()

    if len(existing_toppings) != len(topping_ids):
        found_ids = {t.id for t in existing_toppings}
        missing = [i for i in topping_ids if i not in found_ids]
        raise HTTPException(status_code=400, detail=f"Invalid topping id(s): {missing}")

    pizza.pizza_toppings = [PizzaTopping(pizza_id=pizza_id, topping_id=t.id) for t in existing_toppings]

    db.commit()
    return None


@router.delete("/{pizza_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pizza(pizza_id: int, db: Session = Depends(get_db)):
    pizza = db.query(Pizza).filter(Pizza.id == pizza_id).first()
    if not pizza:
        raise HTTPException(status_code=404, detail=f"Pizza with id {pizza_id} not found.")

    db.delete(pizza)
    db.commit()
    return None