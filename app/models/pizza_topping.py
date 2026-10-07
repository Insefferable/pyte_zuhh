from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class PizzaTopping(Base):
    __tablename__ = "pizza_toppings"

    pizza_id = Column(Integer, ForeignKey("pizzas.id"), primary_key=True)
    topping_id = Column(Integer, ForeignKey("toppings.id"), primary_key=True)

    pizza = relationship("Pizza", back_populates="pizza_toppings")
    topping = relationship("Topping", back_populates="pizza_toppings")