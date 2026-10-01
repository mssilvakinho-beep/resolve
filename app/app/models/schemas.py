from pydantic import BaseModel, Field
from typing import Optional, Literal

class UserIn(BaseModel):
    name: str = Field(min_length=1)

class ContactIn(BaseModel):
    user_id: str
    name: str = Field(min_length=1)
    kind: str = "contact"

class CaseIn(BaseModel):
    user_id: str
    title: str = Field(min_length=1)
    description: str = ""
    status: str = "ABERTO"
    contact_id: Optional[str] = None

class CaseStatusIn(BaseModel):
    status: str

class TransactionIn(BaseModel):
    user_id: str
    kind: Literal['RECEITA','DESPESA']
    category: str = Field(min_length=1)
    description: str = Field(min_length=1)
    amount: float = Field(gt=0)
    case_id: Optional[str] = None
    contact_id: Optional[str] = None
    due_date: Optional[str] = None
    paid: bool = True

class EventIn(BaseModel):
    user_id: str
    description: str
    type: str = "NOTA"
    case_id: Optional[str] = None
    contact_id: Optional[str] = None
    amount: Optional[float] = None

class DocumentIn(BaseModel):
    user_id: str
    filename: str = Field(min_length=1)
    document_type: str = "outro"
    case_id: Optional[str] = None
    contact_id: Optional[str] = None
    storage_ref: Optional[str] = None

class ReportRequest(BaseModel):
    user_id: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
