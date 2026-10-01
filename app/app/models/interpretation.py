from pydantic import BaseModel, Field
from typing import Optional

class InterpretIn(BaseModel):
    user_id: str
    text: str = Field(min_length=1, max_length=5000)
    execute: bool = False

class ConfirmIn(BaseModel):
    interpretation_id: str
