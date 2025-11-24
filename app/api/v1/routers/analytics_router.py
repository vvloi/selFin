"""Analytics router."""
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.db.session import get_db
from app.schemas.analytics import (
    CategorySpendingResponse, SpendingTrendResponse, TopCategoryResponse
)
from app.services.analytics_service import analytics_service
from app.api.v1.deps import get_current_user
from app.models.user import User
import csv
import io


router = APIRouter(tags=["Analytics"])


@router.get("/analytics/spending-by-category", response_model=list[CategorySpendingResponse])
def get_spending_by_category(
    date_from: datetime = Query(...),
    date_to: datetime = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spending breakdown by category."""
    spending = analytics_service.get_spending_by_category(db, current_user.id, date_from, date_to)
    return spending


@router.get("/analytics/spending-trend", response_model=list[SpendingTrendResponse])
def get_spending_trend(
    date_from: datetime = Query(...),
    date_to: datetime = Query(...),
    group_by: str = Query("month", regex="^(day|week|month)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spending trend over time."""
    trend = analytics_service.get_spending_trend(db, current_user.id, date_from, date_to, group_by)
    return trend


@router.get("/analytics/top-categories", response_model=list[TopCategoryResponse])
def get_top_categories(
    date_from: datetime = Query(...),
    date_to: datetime = Query(...),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top spending categories."""
    top_categories = analytics_service.get_top_categories(
        db, current_user.id, date_from, date_to, limit
    )
    return top_categories


@router.get("/reports/transactions.csv")
def export_transactions_csv(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export transactions as CSV."""
    from app.services.transaction_service import transaction_service
    
    transactions, _ = transaction_service.get_transactions_with_filters(
        db, current_user.id, date_from, date_to, page=1, size=10000
    )
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "ID", "Date", "Type", "Amount", "Currency", "Category",
        "Wallet", "Description"
    ])
    
    for transaction in transactions:
        writer.writerow([
            transaction.id,
            transaction.date.isoformat(),
            transaction.type,
            float(transaction.amount),
            transaction.currency,
            transaction.category.name if transaction.category else "",
            transaction.wallet.name if transaction.wallet else "",
            transaction.description or ""
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"}
    )


@router.get("/reports/transactions.pdf")
def export_transactions_pdf(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export transactions as PDF."""
    from app.services.transaction_service import transaction_service
    
    transactions, _ = transaction_service.get_transactions_with_filters(
        db, current_user.id, date_from, date_to, page=1, size=10000
    )
    
    # TODO: Implement PDF generation using reportlab or similar library
    # For now, return a simple placeholder response
    content = f"PDF Report for user {current_user.email}\n"
    content += f"Transactions: {len(transactions)}\n"
    content += "PDF generation to be implemented with reportlab\n"
    
    return Response(
        content=content.encode(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=transactions.pdf"}
    )
