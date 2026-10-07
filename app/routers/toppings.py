from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.topping import Topping
from app.schemas.topping import ToppingCreate, ToppingUpdate, ToppingResponse

router = APIRouter(prefix="/api/toppings", tags=["toppings"])


@router.get("", response_model=list[ToppingResponse])
def get_toppings(db: Session = Depends(get_db)):
    return db.query(Topping).all()


@router.get("/{topping_id}", response_model=ToppingResponse)
def get_topping(topping_id: int, db: Session = Depends(get_db)):
    topping = db.query(Topping).filter(Topping.id == topping_id).first()
    if not topping:
        raise HTTPException(status_code=404, detail=f"Topping with id {topping_id} not found.")
    return topping


@router.post("", response_model=ToppingResponse, status_code=status.HTTP_201_CREATED)
def create_topping(dto: ToppingCreate, db: Session = Depends(get_db)):
    name = dto.name.strip()

    duplicate = db.query(Topping).filter(func.lower(Topping.name) == name.lower()).first()
    if duplicate:
        raise HTTPException(status_code=409, detail=f"A topping named '{name}' already exists.")

    topping = Topping(name=name)
    db.add(topping)
    db.commit()
    db.refresh(topping)
    return topping


@router.put("/{topping_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_topping(topping_id: int, dto: ToppingUpdate, db: Session = Depends(get_db)):
    topping = db.query(Topping).filter(Topping.id == topping_id).first()
    if not topping:
        raise HTTPException(status_code=404, detail=f"Topping with id {topping_id} not found.")

    name = dto.name.strip()

    duplicate = db.query(Topping).filter(
        Topping.id != topping_id, func.lower(Topping.name) == name.lower()
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail=f"A topping named '{name}' already exists.")

    topping.name = name
    db.commit()
    return None


@router.delete("/{topping_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topping(topping_id: int, db: Session = Depends(get_db)):
    topping = db.query(Topping).filter(Topping.id == topping_id).first()
    if not topping:
        raise HTTPException(status_code=404, detail=f"Topping with id {topping_id} not found.")

    db.delete(topping)
    db.commit()
    return None