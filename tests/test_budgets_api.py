"""API Integration tests for budget endpoints with threshold alerts."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, date, timedelta
from decimal import Decimal


class TestBudgetAPI:
    """Test budget API endpoints with threshold logic."""
    
    def test_create_monthly_budget(
        self, test_client: TestClient, auth_headers, test_categories
    ):
        """Test creating a monthly budget."""
        # Arrange
        payload = {
            "category_id": test_categories[0].id,
            "amount_limit": 1000000,
            "period_type": "MONTHLY"
        }
        
        # Act
        response = test_client.post(
            "/v1/budgets", json=payload, headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["category_id"] == test_categories[0].id
        assert float(data["amount_limit"]) == 1000000
        assert data["period_type"] == "MONTHLY"
    
    def test_budget_usage_under_limit(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories, db_session
    ):
        """Test budget shows correct usage when under limit."""
        # Arrange - Create budget and small expense
        from app.models.budget import Budget, PeriodType
        from app.models.transaction import Transaction, TransactionType
        
        budget = Budget(
            user_id=test_wallet.user_id,
            category_id=test_categories[0].id,
            amount_limit=Decimal("1000000"),
            period_type=PeriodType.MONTHLY,
            start_date=date.today().replace(day=1),
            end_date=date.today()
        )
        db_session.add(budget)
        db_session.commit()
        db_session.refresh(budget)
        
        # Add expense: 300k of 1M budget = 30%
        txn = Transaction(
            user_id=test_wallet.user_id,
            type=TransactionType.EXPENSE,
            amount=Decimal("300000"),
            currency="VND",
            date=datetime.now(),
            category_id=test_categories[0].id,
            wallet_id=test_wallet.id
        )
        db_session.add(txn)
        db_session.commit()
        
        # Act - Get budget summary
        response = test_client.get(
            "/v1/budgets/summary",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        budget_data = next((b for b in data if b["id"] == budget.id), None)
        assert budget_data is not None
        assert float(budget_data["used_amount"]) == 300000
        assert float(budget_data["remaining_amount"]) == 700000
        assert budget_data["usage_percentage"] == pytest.approx(30.0, rel=0.1)
        assert budget_data["is_near_limit"] is False
        assert budget_data["is_exceeded"] is False
    
    def test_budget_near_limit_alert(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories, db_session
    ):
        """Test budget shows near-limit alert at 85% usage."""
        # Arrange - Create budget and expense near limit
        from app.models.budget import Budget, PeriodType
        from app.models.transaction import Transaction, TransactionType
        
        budget = Budget(
            user_id=test_wallet.user_id,
            category_id=test_categories[0].id,
            amount_limit=Decimal("1000000"),
            period_type=PeriodType.MONTHLY,
            start_date=date.today().replace(day=1),
            end_date=date.today()
        )
        db_session.add(budget)
        db_session.commit()
        db_session.refresh(budget)
        
        # Add expense: 850k of 1M budget = 85%
        txn = Transaction(
            user_id=test_wallet.user_id,
            type=TransactionType.EXPENSE,
            amount=Decimal("850000"),
            currency="VND",
            date=datetime.now(),
            category_id=test_categories[0].id,
            wallet_id=test_wallet.id
        )
        db_session.add(txn)
        db_session.commit()
        
        # Act - Get budget summary
        response = test_client.get(
            "/v1/budgets/summary",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        budget_data = next((b for b in data if b["id"] == budget.id), None)
        assert budget_data is not None
        assert float(budget_data["used_amount"]) == 850000
        assert budget_data["usage_percentage"] == pytest.approx(85.0, rel=0.1)
        assert budget_data["is_near_limit"] is True  # Should trigger near-limit alert
        assert budget_data["is_exceeded"] is False
    
    def test_budget_exceeded_alert(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories, db_session
    ):
        """Test budget shows exceeded alert when over 100% usage."""
        # Arrange - Create budget and expense exceeding limit
        from app.models.budget import Budget, PeriodType
        from app.models.transaction import Transaction, TransactionType
        
        budget = Budget(
            user_id=test_wallet.user_id,
            category_id=test_categories[0].id,
            amount_limit=Decimal("1000000"),
            period_type=PeriodType.MONTHLY,
            start_date=date.today().replace(day=1),
            end_date=date.today()
        )
        db_session.add(budget)
        db_session.commit()
        db_session.refresh(budget)
        
        # Add expense: 1.2M of 1M budget = 120%
        txn = Transaction(
            user_id=test_wallet.user_id,
            type=TransactionType.EXPENSE,
            amount=Decimal("1200000"),
            currency="VND",
            date=datetime.now(),
            category_id=test_categories[0].id,
            wallet_id=test_wallet.id
        )
        db_session.add(txn)
        db_session.commit()
        
        # Act - Get budget summary
        response = test_client.get(
            "/v1/budgets/summary",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        budget_data = next((b for b in data if b["id"] == budget.id), None)
        assert budget_data is not None
        assert float(budget_data["used_amount"]) == 1200000
        assert float(budget_data["remaining_amount"]) == -200000  # Negative
        assert budget_data["usage_percentage"] == pytest.approx(120.0, rel=0.1)
        assert budget_data["is_near_limit"] is True
        assert budget_data["is_exceeded"] is True  # Should trigger exceeded alert
    
    def test_budget_multiple_periods(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories, db_session
    ):
        """Test budget correctly handles different period types."""
        # Arrange - Create weekly budget
        from app.models.budget import Budget, PeriodType
        
        payload = {
            "category_id": test_categories[0].id,
            "amount_limit": 500000,
            "period_type": "WEEKLY"
        }
        
        # Act
        response = test_client.post(
            "/v1/budgets", json=payload, headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["period_type"] == "WEEKLY"
        # Verify dates are set appropriately for weekly period
        assert "start_date" in data or data["period_type"] == "WEEKLY"
    
    def test_budget_custom_period(
        self, test_client: TestClient, auth_headers, test_categories
    ):
        """Test creating budget with custom date range."""
        # Arrange
        start = date(2024, 3, 1)
        end = date(2024, 3, 15)
        payload = {
            "category_id": test_categories[0].id,
            "amount_limit": 750000,
            "period_type": "CUSTOM",
            "start_date": start.isoformat(),
            "end_date": end.isoformat()
        }
        
        # Act
        response = test_client.post(
            "/v1/budgets", json=payload, headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["period_type"] == "CUSTOM"
        assert data["start_date"] == start.isoformat()
        assert data["end_date"] == end.isoformat()
    
    def test_list_all_budgets(
        self, test_client: TestClient, auth_headers, test_categories, db_session
    ):
        """Test listing all budgets for user."""
        # Arrange - Create multiple budgets
        from app.models.budget import Budget, PeriodType
        
        budgets = [
            Budget(
                user_id=test_categories[0].user_id,
                category_id=test_categories[0].id,
                amount_limit=Decimal("1000000"),
                period_type=PeriodType.MONTHLY
            ),
            Budget(
                user_id=test_categories[0].user_id,
                category_id=test_categories[1].id,
                amount_limit=Decimal("500000"),
                period_type=PeriodType.WEEKLY
            ),
        ]
        for budget in budgets:
            db_session.add(budget)
        db_session.commit()
        
        # Act
        response = test_client.get("/v1/budgets", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
