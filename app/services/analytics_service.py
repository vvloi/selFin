"""Analytics service for business logic."""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.repositories.transaction_repository import transaction_repository


class AnalyticsService:
    """Service for analytics and reporting business logic."""
    
    def get_spending_by_category(
        self,
        db: Session,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[dict]:
        """Get spending breakdown by category."""
        results = transaction_repository.get_spending_by_category(
            db, user_id, start_date, end_date
        )
        
        total_amount = sum(float(r[2]) for r in results)
        
        return [
            {
                "category_id": r[0],
                "category_name": r[1],
                "total_amount": float(r[2]),
                "percentage": (float(r[2]) / total_amount * 100) if total_amount > 0 else 0,
                "transaction_count": r[3]
            }
            for r in results
        ]
    
    def get_spending_trend(
        self,
        db: Session,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        group_by: str = "month"
    ) -> List[dict]:
        """Get spending trend over time."""
        trend_data = transaction_repository.get_spending_trend(
            db, user_id, start_date, end_date, group_by
        )
        
        return [
            {
                "period": self._format_period(item, group_by),
                "year": item["year"],
                "month": item.get("month"),
                "total_expense": item["total_expense"],
                "total_income": item["total_income"]
            }
            for item in trend_data
        ]
    
    def get_top_categories(
        self,
        db: Session,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10
    ) -> List[dict]:
        """Get top spending categories."""
        results = transaction_repository.get_spending_by_category(
            db, user_id, start_date, end_date
        )
        
        sorted_results = sorted(results, key=lambda r: r[2], reverse=True)[:limit]
        
        return [
            {
                "category_id": r[0],
                "category_name": r[1],
                "total_amount": float(r[2]),
                "transaction_count": r[3]
            }
            for r in sorted_results
        ]
    
    def _format_period(self, item: dict, group_by: str) -> str:
        """Format period string for trend data."""
        if group_by == "month":
            return f"{item['year']}-{item['month']:02d}"
        elif group_by == "week":
            return f"{item['year']}-W{item.get('week', 1):02d}"
        elif group_by == "day":
            return item.get("day", "")
        
        return str(item["year"])


analytics_service = AnalyticsService()
