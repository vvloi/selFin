"""Recurring transaction router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.recurring import (
    RecurringTransactionCreateRequest, RecurringTransactionUpdateRequest,
    RecurringTransactionResponse, Frequency
)
from app.schemas.transaction import TransactionResponse, TransactionType
from app.services.recurring_service import recurring_service
from app.api.v1.deps import get_current_user
from app.models.user import User


router = APIRouter(prefix="/recurring-transactions", tags=["RecurringTransactions"])


@router.get("", response_model=list[RecurringTransactionResponse])
def get_recurring_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all recurring transactions."""
    recurring_transactions = recurring_service.get_all_recurring(db, current_user.id)
    return recurring_transactions


@router.post("", response_model=RecurringTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_recurring_transaction(
    request: RecurringTransactionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new recurring transaction."""
    from app.models.transaction import TransactionType as ModelTransactionType
    from app.models.recurring_transaction import Frequency as ModelFrequency
    
    recurring = recurring_service.create_recurring_transaction(
        db, current_user.id, ModelTransactionType(request.type.value),
        request.amount, request.currency, ModelFrequency(request.frequency.value),
        request.start_date, request.category_id, request.wallet_id,
        request.to_wallet_id, request.description, request.is_active
    )
    return recurring


@router.get("/{recurring_id}", response_model=RecurringTransactionResponse)
def get_recurring_transaction(
    recurring_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recurring transaction by ID."""
    recurring = recurring_service.get_recurring_by_id(db, recurring_id, current_user.id)
    return recurring


@router.patch("/{recurring_id}", response_model=RecurringTransactionResponse)
def update_recurring_transaction(
    recurring_id: int,
    request: RecurringTransactionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update recurring transaction."""
    from app.models.transaction import TransactionType as ModelTransactionType
    from app.models.recurring_transaction import Frequency as ModelFrequency
    
    model_type = ModelTransactionType(request.type.value) if request.type else None
    model_frequency = ModelFrequency(request.frequency.value) if request.frequency else None
    
    recurring = recurring_service.update_recurring_transaction(
        db, recurring_id, current_user.id, model_type, request.amount,
        request.currency, model_frequency, request.start_date, request.category_id,
        request.wallet_id, request.to_wallet_id, request.description, request.is_active
    )
    return recurring


@router.delete("/{recurring_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring_transaction(
    recurring_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete recurring transaction."""
    recurring_service.delete_recurring_transaction(db, recurring_id, current_user.id)
    return None


@router.post("/{recurring_id}/execute", status_code=status.HTTP_200_OK)
def execute_recurring_transaction(
    recurring_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually execute a recurring transaction."""
    transaction = recurring_service.execute_recurring_transaction(db, recurring_id, current_user.id)
    return {"transaction_id": transaction.id, "amount": float(transaction.amount)}
