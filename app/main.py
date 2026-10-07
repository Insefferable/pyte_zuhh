from fastapi import FastAPI

from app.database import Base, engine
from app.routers import toppings, pizzas
import app.models

app = FastAPI(title="Pizza Store API")

Base.metadata.create_all(bind=engine)

app.include_router(toppings.router)
app.include_router(pizzas.router)


@app.get("/")
def root():
    return {"message": "Pizza Store API is running"}