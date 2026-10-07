from fastapi import FastAPI

from app.database import Base, engine
import app.models

app = FastAPI(title="Pizza Store API")

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Pizza Store API is running"}