from pydantic import BaseModel

class ProductBase(BaseModel):
    brand: str
    name: str
    price: int
