
from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProductCreate(BaseModel):
    product_id: str
    product_name: str
    category: str
    description: Optional[str] = None


class ProductResponse(ProductCreate):
    model_config = ConfigDict(from_attributes=True)
