"""Transaction repository for database operations."""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, extract, case
from typing import List, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
from app.models.transaction import Transaction, TransactionType


class TransactionRepository:
    """Repository for Transaction entity database operations."""
    
    def create(
        self,
        db: Session,
        user_id: int,
        transaction_type: TransactionType,
        amount: Decimal,
        currency: str,
        transaction_date: datetime,
        category_id: Optional[int] = None,
        wallet_id: Optional[int] = None,
        to_wallet_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> Transaction:
        """Create a new transaction."""
        transaction = Transaction(
            user_id=user_id,
            type=transaction_type,
            amount=amount,
            currency=currency,
            date=transaction_date,
            category_id=category_id,
            wallet_id=wallet_id,
            to_wallet_id=to_wallet_id,
            description=description
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    
    def get_by_id(self, db: Session, transaction_id: int, user_id: int) -> Optional[Transaction]:
        """Get transaction by ID for a specific user."""
        return db.query(Transaction).options(
            joinedload(Transaction.category),
            joinedload(Transaction.wallet),
            joinedload(Transaction.to_wallet)
        ).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        ).first()
    
    def get_with_filters(
        self,
        db: Session,
        user_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        category_id: Optional[int] = None,
        wallet_id: Optional[int] = None,
        transaction_type: Optional[TransactionType] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        page: int = 1,
        size: int = 50
    ) -> Tuple[List[Transaction], int]:
        """Get transactions with filters and pagination."""
        query = db.query(Transaction).options(
            joinedload(Transaction.category),
            joinedload(Transaction.wallet),
            joinedload(Transaction.to_wallet)
        ).filter(Transaction.user_id == user_id)
        
        if date_from:
            query = query.filter(Transaction.date >= date_from)
        if date_to:
            query = query.filter(Transaction.date <= date_to)
        if category_id:
            query = query.filter(Transaction.category_id == category_id)
        if wallet_id:
            query = query.filter(
                or_(Transaction.wallet_id == wallet_id, Transaction.to_wallet_id == wallet_id)
            )
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)
        if min_amount is not None:
            query = query.filter(Transaction.amount >= min_amount)
        if max_amount is not None:
            query = query.filter(Transaction.amount <= max_amount)
        
        total = query.count()
        transactions = query.order_by(Transaction.date.desc()).offset((page - 1) * size).limit(size).all()
        
        return transactions, total
    
    def update(self, db: Session, transaction: Transaction) -> Transaction:
        """Update transaction."""
        db.commit()
        db.refresh(transaction)
        return transaction
    
    def delete(self, db: Session, transaction: Transaction) -> None:
        """Delete transaction."""
        db.delete(transaction)
        db.commit()
    
    def get_total_by_category_and_period(
        self,
        db: Session,
        user_id: int,
        category_id: int,
        start_date: date,
        end_date: date
    ) -> Decimal:
        """Get total amount spent for a category within a period."""
        result = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.category_id == category_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        ).scalar()
        
        return result or Decimal(0)
    
    def get_grouped_by_day(
        self,
        db: Session,
        user_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Transaction]:
        """Get transactions grouped by day."""
        query = db.query(Transaction).options(
            joinedload(Transaction.category),
            joinedload(Transaction.wallet),
            joinedload(Transaction.to_wallet)
        ).filter(Transaction.user_id == user_id)
        
        if date_from:
            query = query.filter(Transaction.date >= date_from)
        if date_to:
            query = query.filter(Transaction.date <= date_to)
        
        return query.order_by(Transaction.date.desc()).all()
    
    def get_spending_by_category(
        self,
        db: Session,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Tuple[int, str, Decimal, int]]:
        """Get spending grouped by category."""
        from app.models.category import Category
        
        result = db.query(
            Category.id,
            Category.name,
            func.sum(Transaction.amount).label("total_amount"),
            func.count(Transaction.id).label("transaction_count")
        ).join(
            Transaction, Transaction.category_id == Category.id
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        ).group_by(Category.id, Category.name).all()
        
        return result
    
    def get_spending_trend(
        self,
        db: Session,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        group_by: str = "month"
    ) -> List[dict]:
        """Get spending trend grouped by period."""
        if group_by == "day":
            result = db.query(
                func.date(Transaction.date).label("day"),
                extract("year", Transaction.date).label("year"),
                extract("month", Transaction.date).label("month"),
                func.sum(
                    case((Transaction.type == TransactionType.EXPENSE, Transaction.amount), else_=0)
                ).label("total_expense"),
                func.sum(
                    case((Transaction.type == TransactionType.INCOME, Transaction.amount), else_=0)
                ).label("total_income")
            ).filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.date >= start_date,
                    Transaction.date <= end_date
                )
            ).group_by(
                func.date(Transaction.date)
            ).order_by(
                func.date(Transaction.date)
            ).all()
            
            return [
                {
                    "day": str(r.day),
                    "year": int(r.year),
                    "month": int(r.month),
                    "total_expense": float(r.total_expense or 0),
                    "total_income": float(r.total_income or 0)
                }
                for r in result
            ]
        elif group_by == "week":
            result = db.query(
                extract("year", Transaction.date).label("year"),
                extract("week", Transaction.date).label("week"),
                func.sum(
                    case((Transaction.type == TransactionType.EXPENSE, Transaction.amount), else_=0)
                ).label("total_expense"),
                func.sum(
                    case((Transaction.type == TransactionType.INCOME, Transaction.amount), else_=0)
                ).label("total_income")
            ).filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.date >= start_date,
                    Transaction.date <= end_date
                )
            ).group_by(
                extract("year", Transaction.date),
                extract("week", Transaction.date)
            ).order_by(
                extract("year", Transaction.date),
                extract("week", Transaction.date)
            ).all()
            
            return [
                {
                    "year": int(r.year),
                    "week": int(r.week),
                    "total_expense": float(r.total_expense or 0),
                    "total_income": float(r.total_income or 0)
                }
                for r in result
            ]
        elif group_by == "month":
            result = db.query(
                extract("year", Transaction.date).label("year"),
                extract("month", Transaction.date).label("month"),
                func.sum(
                    case((Transaction.type == TransactionType.EXPENSE, Transaction.amount), else_=0)
                ).label("total_expense"),
                func.sum(
                    case((Transaction.type == TransactionType.INCOME, Transaction.amount), else_=0)
                ).label("total_income")
            ).filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.date >= start_date,
                    Transaction.date <= end_date
                )
            ).group_by(
                extract("year", Transaction.date),
                extract("month", Transaction.date)
            ).order_by(
                extract("year", Transaction.date),
                extract("month", Transaction.date)
            ).all()
            
            return [
                {
                    "year": int(r.year),
                    "month": int(r.month),
                    "total_expense": float(r.total_expense or 0),
                    "total_income": float(r.total_income or 0)
                }
                for r in result
            ]
        
        return []


transaction_repository = TransactionRepository()
