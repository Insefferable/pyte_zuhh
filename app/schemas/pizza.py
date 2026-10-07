from decimal import Decimal
from typing import Annotated
from pydantic import BaseModel, Field
from app.schemas.topping import ToppingResponse

Price = Annotated[Decimal, Field(ge=0, le=10000)]


class PizzaBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: Price


class PizzaCreate(PizzaBase):
    topping_ids: list[int] = Field(default_factory=list)


class PizzaUpdate(PizzaBase):
    pass


class PizzaToppingsUpdate(BaseModel):
    topping_ids: list[int]


class PizzaResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Price
    toppings: list[ToppingResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True