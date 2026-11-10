
from pydantic import BaseModel, ConfigDict


class SupportMessageCreate(BaseModel):
    message_id: str
    customer_id: str
    channel_id: str
    ticket_id: str
    message_text: str


class SupportMessageResponse(SupportMessageCreate):
    model_config = ConfigDict(from_attributes=True)
