from pydantic import BaseModel, Field, validator
from typing import Optional, Union
from datetime import datetime, date

class ExpenseBase(BaseModel):
    category: str
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    expense_date: Union[datetime, date, str]
    payment_method: Optional[str] = "Cash"
    
    # Convert string dates to datetime objects
    @validator('expense_date', pre=True)
    def parse_expense_date(cls, value):
        if isinstance(value, str):
            try:
                # Try parsing as date string (YYYY-MM-DD)
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                try:
                    # Try parsing as datetime string
                    return datetime.fromisoformat(value)
                except ValueError:
                    raise ValueError(f"Invalid date format: {value}. Use YYYY-MM-DD format.")
        return value

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    expense_date: Optional[datetime] = None

class ExpenseInDB(ExpenseBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class Expense(ExpenseInDB):
    pass
