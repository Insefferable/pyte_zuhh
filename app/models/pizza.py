from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship

from app.database import Base


class Pizza(Base):
    __tablename__ = "pizzas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(500), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)

    pizza_toppings = relationship(
        "PizzaTopping", back_populates="pizza", cascade="all, delete-orphan"
    )