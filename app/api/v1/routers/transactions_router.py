"""Transaction router."""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.db.session import get_db
from app.schemas.transaction import (
    TransactionCreateRequest, TransactionUpdateRequest, TransactionResponse,
    TransactionListResponse, TransactionType, CategoryCreateRequest, CategoryResponse,
    DailyTransactionGroup, WeeklyTransactionGroup, MonthlyTransactionGroup
)
from app.services.transaction_service import transaction_service
from app.repositories.category_repository import category_repository
from app.api.v1.deps import get_current_user
from app.models.user import User
import math


router = APIRouter(prefix="/transactions", tags=["Transactions"])
category_router = APIRouter(prefix="/categories", tags=["Transactions"])


@category_router.get("", response_model=list[CategoryResponse])
def get_categories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all categories."""
    categories = category_repository.get_all_by_user(db, current_user.id)
    return categories


@category_router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    request: CategoryCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new category."""
    from app.models.category import CategoryType as ModelCategoryType
    category = category_repository.create(
        db, current_user.id, request.name, ModelCategoryType(request.type.value),
        request.icon, request.color
    )
    return category


@router.get("", response_model=TransactionListResponse)
def get_transactions(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    category_id: Optional[int] = Query(None),
    wallet_id: Optional[int] = Query(None),
    transaction_type: Optional[TransactionType] = Query(None),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transactions with filters."""
    from app.models.transaction import TransactionType as ModelTransactionType
    
    model_type = ModelTransactionType(transaction_type.value) if transaction_type else None
    
    transactions, total = transaction_service.get_transactions_with_filters(
        db, current_user.id, date_from, date_to, category_id, wallet_id, model_type,
        min_amount, max_amount, page, size
    )
    
    pages = math.ceil(total / size) if total > 0 else 0
    
    return TransactionListResponse(
        items=transactions,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    request: TransactionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction."""
    from app.models.transaction import TransactionType as ModelTransactionType
    
    transaction = transaction_service.create_transaction(
        db, current_user.id, ModelTransactionType(request.type.value),
        request.amount, request.currency, request.date, request.category_id,
        request.wallet_id, request.to_wallet_id, request.description
    )
    return transaction


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transaction by ID."""
    from app.repositories.transaction_repository import transaction_repository
    transaction = transaction_repository.get_by_id(db, transaction_id, current_user.id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    request: TransactionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update transaction."""
    from app.models.transaction import TransactionType as ModelTransactionType
    
    model_type = ModelTransactionType(request.type.value) if request.type else None
    
    transaction = transaction_service.update_transaction(
        db, transaction_id, current_user.id, model_type, request.amount,
        request.currency, request.date, request.category_id, request.wallet_id,
        request.to_wallet_id, request.description
    )
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete transaction."""
    transaction_service.delete_transaction(db, transaction_id, current_user.id)
    return None


@router.get("/daily", response_model=list[DailyTransactionGroup])
def get_daily_transactions(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transactions grouped by day."""
    return transaction_service.get_daily_grouped_transactions(db, current_user.id, date_from, date_to)


@router.get("/weekly", response_model=list[WeeklyTransactionGroup])
def get_weekly_transactions(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transactions grouped by week."""
    return transaction_service.get_weekly_grouped_transactions(db, current_user.id, date_from, date_to)


@router.get("/monthly", response_model=list[MonthlyTransactionGroup])
def get_monthly_transactions(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transactions grouped by month."""
    return transaction_service.get_monthly_grouped_transactions(db, current_user.id, date_from, date_to)
