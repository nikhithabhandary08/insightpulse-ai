
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


class CustomerCreate(BaseModel):
    customer_id: str
    customer_name: str
    email: Optional[EmailStr] = None
    country: Optional[str] = None


class CustomerResponse(CustomerCreate):
    model_config = ConfigDict(from_attributes=True)
