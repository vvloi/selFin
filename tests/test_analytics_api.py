"""API Integration tests for analytics and export endpoints."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from decimal import Decimal
import csv
import io


class TestAnalyticsAPI:
    """Test analytics API endpoints."""
    
    def test_spending_by_category_pie_chart_data(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories, db_session
    ):
        """Test getting spending breakdown by category for pie chart."""
        # Arrange - Create transactions across multiple categories
        from app.models.transaction import Transaction, TransactionType
        
        base_date = datetime(2024, 3, 1)
        transactions = [
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("500000"),  # Food
                currency="VND",
                date=base_date,
                category_id=test_categories[0].id,
                wallet_id=test_wallet.id
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("300000"),  # Food again
                currency="VND",
                date=base_date + timedelta(days=1),
                category_id=test_categories[0].id,
                wallet_id=test_wallet.id
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("200000"),  # Transport
                currency="VND",
                date=base_date + timedelta(days=2),
                category_id=test_categories[1].id,
                wallet_id=test_wallet.id
            ),
        ]
        for txn in transactions:
            db_session.add(txn)
        db_session.commit()
        
        # Act
        response = test_client.get(
            "/api/v1/analytics/spending-by-category",
            params={
                "date_from": base_date.isoformat(),
                "date_to": (base_date + timedelta(days=10)).isoformat()
            },
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        
        # Find Food category (800k total)
        food_data = next((d for d in data if d["category_name"] == "Food"), None)
        assert food_data is not None
        assert float(food_data["total_amount"]) == 800000
        
        # Find Transport category (200k total)
        transport_data = next((d for d in data if d["category_name"] == "Transport"), None)
        assert transport_data is not None
        assert float(transport_data["total_amount"]) == 200000
        
        # Verify percentages sum to ~100%
        total_percentage = sum(float(d["percentage"]) for d in data)
        assert 99.0 <= total_percentage <= 101.0
        
        # Verify Food is 80% and Transport is 20%
        assert food_data["percentage"] == pytest.approx(80.0, rel=0.1)
        assert transport_data["percentage"] == pytest.approx(20.0, rel=0.1)
    
    def test_spending_trend_monthly(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories, db_session
    ):
        """Test getting monthly spending trend."""
        # Arrange - Create transactions across different months
        from app.models.transaction import Transaction, TransactionType
        
        transactions = [
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("500000"),
                currency="VND",
                date=datetime(2024, 1, 15),
                category_id=test_categories[0].id,
                wallet_id=test_wallet.id
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("300000"),
                currency="VND",
                date=datetime(2024, 1, 20),
                category_id=test_categories[0].id,
                wallet_id=test_wallet.id
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("700000"),
                currency="VND",
                date=datetime(2024, 2, 10),
                category_id=test_categories[0].id,
                wallet_id=test_wallet.id
            ),
        ]
        for txn in transactions:
            db_session.add(txn)
        db_session.commit()
        
        # Act
        response = test_client.get(
            "/api/v1/analytics/spending-trend",
            params={
                "date_from": datetime(2024, 1, 1).isoformat(),
                "date_to": datetime(2024, 2, 28).isoformat(),
                "group_by": "month"
            },
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        
        # January: 800k total
        jan_data = next((d for d in data if d["year"] == 2024 and d["month"] == 1), None)
        assert jan_data is not None
        assert float(jan_data["total_expense"]) == 800000
        
        # February: 700k total
        feb_data = next((d for d in data if d["year"] == 2024 and d["month"] == 2), None)
        assert feb_data is not None
        assert float(feb_data["total_expense"]) == 700000
    
    def test_spending_trend_daily_for_cumulative_chart(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories, db_session
    ):
        """Test getting daily spending trend for cumulative chart calculation."""
        # Arrange - Create transactions on consecutive days
        from app.models.transaction import Transaction, TransactionType
        
        base_date = datetime(2024, 3, 1)
        daily_amounts = [100000, 150000, 200000, 80000, 120000]
        
        for i, amount in enumerate(daily_amounts):
            txn = Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal(str(amount)),
                currency="VND",
                date=base_date + timedelta(days=i),
                category_id=test_categories[0].id,
                wallet_id=test_wallet.id
            )
            db_session.add(txn)
        db_session.commit()
        
        # Act
        response = test_client.get(
            "/api/v1/analytics/spending-trend",
            params={
                "date_from": base_date.isoformat(),
                "date_to": (base_date + timedelta(days=10)).isoformat(),
                "group_by": "day"
            },
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 5
        
        # Verify daily amounts are correct for cumulative calculation
        daily_totals = [float(d["total_expense"]) for d in data if d["total_expense"]]
        assert 100000 in daily_totals
        assert 150000 in daily_totals
        assert 200000 in daily_totals
        
        # Frontend can calculate cumulative: [100k, 250k, 450k, 530k, 650k]
    
    def test_top_categories_ranking(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories, db_session
    ):
        """Test getting top spending categories ranked."""
        # Arrange - Create transactions with different category spending
        from app.models.transaction import Transaction, TransactionType
        
        base_date = datetime(2024, 4, 1)
        transactions = [
            # Shopping: 1.5M total
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("1000000"),
                currency="VND",
                date=base_date,
                category_id=test_categories[2].id,
                wallet_id=test_wallet.id
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("500000"),
                currency="VND",
                date=base_date + timedelta(days=1),
                category_id=test_categories[2].id,
                wallet_id=test_wallet.id
            ),
            # Food: 800k total
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("800000"),
                currency="VND",
                date=base_date,
                category_id=test_categories[0].id,
                wallet_id=test_wallet.id
            ),
            # Transport: 300k total
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("300000"),
                currency="VND",
                date=base_date,
                category_id=test_categories[1].id,
                wallet_id=test_wallet.id
            ),
        ]
        for txn in transactions:
            db_session.add(txn)
        db_session.commit()
        
        # Act - Get top 2 categories
        response = test_client.get(
            "/api/v1/analytics/top-categories",
            params={
                "date_from": base_date.isoformat(),
                "date_to": (base_date + timedelta(days=10)).isoformat(),
                "limit": 2
            },
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Verify ranking: Shopping #1, Food #2
        assert data[0]["category_name"] == "Shopping"
        assert float(data[0]["total_amount"]) == 1500000
        assert data[1]["category_name"] == "Food"
        assert float(data[1]["total_amount"]) == 800000
    
    def test_export_transactions_csv(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories, db_session
    ):
        """Test exporting transactions as CSV."""
        # Arrange - Create some transactions
        from app.models.transaction import Transaction, TransactionType
        
        base_date = datetime(2024, 5, 1)
        transactions = [
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("250000"),
                currency="VND",
                date=base_date,
                category_id=test_categories[0].id,
                wallet_id=test_wallet.id,
                description="Grocery"
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.INCOME,
                amount=Decimal("5000000"),
                currency="VND",
                date=base_date,
                category_id=test_categories[3].id,
                wallet_id=test_wallet.id,
                description="Salary"
            ),
        ]
        for txn in transactions:
            db_session.add(txn)
        db_session.commit()
        
        # Act
        response = test_client.get(
            "/api/v1/reports/transactions.csv",
            params={
                "date_from": base_date.isoformat(),
                "date_to": (base_date + timedelta(days=5)).isoformat()
            },
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        
        # Parse CSV content
        csv_content = response.text
        csv_reader = csv.reader(io.StringIO(csv_content))
        rows = list(csv_reader)
        
        assert len(rows) >= 3  # Header + 2 transactions
        header = rows[0]
        assert "ID" in header
        assert "Amount" in header
        assert "Category" in header
        
        # Verify data rows contain our transactions
        amounts = [row[3] for row in rows[1:] if len(row) > 3]  # Amount column
        assert "250000.0" in amounts or "250000" in amounts
        assert "5000000.0" in amounts or "5000000" in amounts
    
    def test_export_transactions_pdf(
        self, test_client: TestClient, auth_headers, test_wallet, db_session
    ):
        """Test exporting transactions as PDF."""
        # Arrange - Create a transaction
        from app.models.transaction import Transaction, TransactionType
        
        txn = Transaction(
            user_id=test_wallet.user_id,
            type=TransactionType.EXPENSE,
            amount=Decimal("100000"),
            currency="VND",
            date=datetime.now(),
            wallet_id=test_wallet.id
        )
        db_session.add(txn)
        db_session.commit()
        
        # Act
        response = test_client.get(
            "/api/v1/reports/transactions.pdf",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        assert "application/pdf" in response.headers["content-type"]
        assert "attachment" in response.headers["content-disposition"]
        assert len(response.content) > 0  # Has content
    
    def test_weekly_grouped_transactions_for_reports(
        self, test_client: TestClient, auth_headers, test_wallet, db_session
    ):
        """Test getting transactions grouped by week for weekly reports."""
        # Arrange - Create transactions across different weeks
        from app.models.transaction import Transaction, TransactionType
        
        # Week 1
        week1_start = datetime(2024, 6, 3)  # Monday
        # Week 2
        week2_start = datetime(2024, 6, 10)  # Next Monday
        
        transactions = [
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("300000"),
                currency="VND",
                date=week1_start,
                wallet_id=test_wallet.id
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("200000"),
                currency="VND",
                date=week1_start + timedelta(days=2),
                wallet_id=test_wallet.id
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("400000"),
                currency="VND",
                date=week2_start,
                wallet_id=test_wallet.id
            ),
        ]
        for txn in transactions:
            db_session.add(txn)
        db_session.commit()
        
        # Act
        response = test_client.get(
            "/api/v1/transactions/weekly",
            params={
                "date_from": week1_start.isoformat(),
                "date_to": (week2_start + timedelta(days=6)).isoformat()
            },
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        
        # Week 1 should have 500k total
        week1_data = next(
            (w for w in data if w["year"] == 2024 and w["week"] == week1_start.isocalendar()[1]),
            None
        )
        if week1_data:
            assert float(week1_data["total_amount"]) == 500000
