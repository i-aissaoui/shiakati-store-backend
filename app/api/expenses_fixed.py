from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import List
from datetime import datetime, date
from ..db.session import get_db
from ..db.models import Expense
from ..schemas.expense import ExpenseCreate, ExpenseUpdate, Expense as ExpenseSchema
from ..api.auth import get_current_admin_user

router = APIRouter()

@router.post("/", response_model=ExpenseSchema)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Create a new expense record."""
    try:
        # Create the expense with all fields
        db_expense = Expense(
            category=expense.category,
            amount=expense.amount,
            description=expense.description,
            expense_date=expense.expense_date,
            payment_method=expense.payment_method if hasattr(expense, 'payment_method') else "Cash"
        )
        
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        return db_expense
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create expense: {str(e)}"
        )

@router.get("/", response_model=List[ExpenseSchema])
def get_expenses(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
    skip: int = 0,
    limit: int = 100
):
    """Get all expenses, optionally paginated."""
    expenses = db.query(Expense).order_by(Expense.expense_date.desc()).offset(skip).limit(limit).all()
    return expenses

@router.get("/date-range", response_model=List[ExpenseSchema])
def get_expenses_by_date_range(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get expenses between two dates."""
    try:
        # Convert string dates to date objects
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        expenses = db.query(Expense).filter(
            Expense.expense_date >= start,
            Expense.expense_date <= end
        ).order_by(Expense.expense_date.desc()).all()
        
        return expenses
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid date format. Use YYYY-MM-DD. Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error filtering expenses: {str(e)}"
        )

@router.get("/{expense_id}", response_model=ExpenseSchema)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get a specific expense by ID."""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@router.put("/{expense_id}", response_model=ExpenseSchema)
def update_expense(
    expense_id: int,
    expense: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Update an expense by ID."""
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Update fields
    for key, value in expense.dict(exclude_unset=True).items():
        setattr(db_expense, key, value)
    
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Delete an expense by ID."""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(expense)
    db.commit()
    return {"success": True, "message": "Expense deleted"}

@router.get("/monthly/{year}/{month}", response_model=List[ExpenseSchema])
def get_monthly_expenses(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get expenses for a specific month and year."""
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    expenses = db.query(Expense).filter(
        extract('year', Expense.expense_date) == year,
        extract('month', Expense.expense_date) == month
    ).order_by(Expense.expense_date.desc()).all()
    
    return expenses

@router.get("/summary/monthly/{year}/{month}")
def get_expense_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get expense summary for a specific month and year."""
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    # Get all expenses for the month
    expenses = db.query(Expense).filter(
        extract('year', Expense.expense_date) == year,
        extract('month', Expense.expense_date) == month
    ).all()
    
    # Calculate totals by category
    categories = {}
    total_amount = 0
    
    for expense in expenses:
        category = expense.category
        if category not in categories:
            categories[category] = 0
        
        categories[category] += expense.amount
        total_amount += expense.amount
    
    return {
        "year": year,
        "month": month,
        "total": total_amount,
        "categories": [{"name": k, "amount": v} for k, v in categories.items()]
    }
