from pydantic import BaseModel, Field


class ToppingBase(BaseModel):
    name: str = Field(..., max_length=100)


class ToppingCreate(ToppingBase):
    pass


class ToppingUpdate(ToppingBase):
    pass


class ToppingResponse(ToppingBase):
    id: int

    class Config:
        from_attributes = True