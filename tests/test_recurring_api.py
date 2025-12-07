"""API Integration tests for recurring transaction endpoints."""
import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal


class TestRecurringTransactionAPI:
    """Test recurring transaction API endpoints."""
    
    def test_create_daily_recurring_transaction(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories
    ):
        """Test creating a daily recurring transaction."""
        # Arrange
        start_date = date.today()
        payload = {
            "type": "EXPENSE",
            "amount": 50000,
            "currency": "VND",
            "frequency": "DAILY",
            "start_date": start_date.isoformat(),
            "category_id": test_categories[0].id,
            "wallet_id": test_wallet.id,
            "description": "Daily expense",
            "is_active": True
        }
        
        # Act
        response = test_client.post(
            "/v1/recurring-transactions", json=payload, headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["frequency"] == "DAILY"
        assert data["start_date"] == start_date.isoformat()
        # Next run should be tomorrow
        expected_next = (start_date + timedelta(days=1)).isoformat()
        assert data["next_run_date"] == expected_next
        assert data["is_active"] is True
    
    def test_create_weekly_recurring_transaction(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories
    ):
        """Test creating a weekly recurring transaction."""
        # Arrange
        start_date = date(2024, 1, 1)  # Monday
        payload = {
            "type": "EXPENSE",
            "amount": 100000,
            "currency": "VND",
            "frequency": "WEEKLY",
            "start_date": start_date.isoformat(),
            "category_id": test_categories[0].id,
            "wallet_id": test_wallet.id,
            "description": "Weekly subscription"
        }
        
        # Act
        response = test_client.post(
            "/v1/recurring-transactions", json=payload, headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["frequency"] == "WEEKLY"
        # Next run should be one week later
        expected_next = (start_date + timedelta(weeks=1)).isoformat()
        assert data["next_run_date"] == expected_next
    
    def test_create_monthly_recurring_transaction(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories
    ):
        """Test creating a monthly recurring transaction."""
        # Arrange
        start_date = date(2024, 1, 15)
        payload = {
            "type": "EXPENSE",
            "amount": 500000,
            "currency": "VND",
            "frequency": "MONTHLY",
            "start_date": start_date.isoformat(),
            "category_id": test_categories[0].id,
            "wallet_id": test_wallet.id,
            "description": "Monthly rent"
        }
        
        # Act
        response = test_client.post(
            "/v1/recurring-transactions", json=payload, headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["frequency"] == "MONTHLY"
        # Next run should be one month later
        expected_next = (start_date + relativedelta(months=1)).isoformat()
        assert data["next_run_date"] == expected_next
    
    def test_create_yearly_recurring_transaction(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories
    ):
        """Test creating a yearly recurring transaction."""
        # Arrange
        start_date = date(2024, 3, 15)
        payload = {
            "type": "EXPENSE",
            "amount": 2000000,
            "currency": "VND",
            "frequency": "YEARLY",
            "start_date": start_date.isoformat(),
            "category_id": test_categories[0].id,
            "wallet_id": test_wallet.id,
            "description": "Annual insurance"
        }
        
        # Act
        response = test_client.post(
            "/v1/recurring-transactions", json=payload, headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["frequency"] == "YEARLY"
        # Next run should be one year later
        expected_next = (start_date + relativedelta(years=1)).isoformat()
        assert data["next_run_date"] == expected_next
    
    def test_execute_recurring_transaction_manually(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories, db_session
    ):
        """Test manually executing a recurring transaction."""
        # Arrange - Create recurring transaction
        from app.models.recurring_transaction import RecurringTransaction, Frequency
        
        recurring = RecurringTransaction(
            user_id=test_wallet.user_id,
            type="EXPENSE",
            amount=Decimal("200000"),
            currency="VND",
            frequency=Frequency.MONTHLY,
            start_date=date.today() - timedelta(days=5),
            next_run_date=date.today() - timedelta(days=1),  # Due yesterday
            category_id=test_categories[0].id,
            wallet_id=test_wallet.id,
            is_active=True
        )
        db_session.add(recurring)
        db_session.commit()
        db_session.refresh(recurring)
        
        initial_balance = test_wallet.balance
        
        # Act - Execute the recurring transaction
        response = test_client.post(
            f"/v1/recurring-transactions/{recurring.id}/execute",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "transaction_id" in data
        
        # Verify transaction was created
        from app.models.transaction import Transaction
        created_txn = db_session.query(Transaction).filter_by(
            id=data["transaction_id"]
        ).first()
        assert created_txn is not None
        assert created_txn.amount == Decimal("200000")
        
        # Verify wallet balance was updated
        db_session.refresh(test_wallet)
        assert test_wallet.balance == initial_balance - Decimal("200000")
        
        # Verify next_run_date was updated
        db_session.refresh(recurring)
        assert recurring.next_run_date > date.today() - timedelta(days=1)
    
    def test_deactivate_recurring_transaction(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories, db_session
    ):
        """Test deactivating a recurring transaction."""
        # Arrange - Create active recurring transaction
        from app.models.recurring_transaction import RecurringTransaction, Frequency
        
        recurring = RecurringTransaction(
            user_id=test_wallet.user_id,
            type="EXPENSE",
            amount=Decimal("100000"),
            currency="VND",
            frequency=Frequency.MONTHLY,
            start_date=date.today(),
            next_run_date=date.today() + timedelta(days=30),
            wallet_id=test_wallet.id,
            is_active=True
        )
        db_session.add(recurring)
        db_session.commit()
        db_session.refresh(recurring)
        
        # Act - Deactivate it
        response = test_client.patch(
            f"/v1/recurring-transactions/{recurring.id}",
            json={"is_active": False},
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
    
    def test_list_recurring_transactions(
        self, test_client: TestClient, auth_headers, test_wallet, db_session
    ):
        """Test listing all recurring transactions."""
        # Arrange - Create multiple recurring transactions
        from app.models.recurring_transaction import RecurringTransaction, Frequency
        
        recurrings = [
            RecurringTransaction(
                user_id=test_wallet.user_id,
                type="EXPENSE",
                amount=Decimal("50000"),
                currency="VND",
                frequency=Frequency.DAILY,
                start_date=date.today(),
                next_run_date=date.today() + timedelta(days=1),
                wallet_id=test_wallet.id,
                is_active=True,
                description="Daily coffee"
            ),
            RecurringTransaction(
                user_id=test_wallet.user_id,
                type="EXPENSE",
                amount=Decimal("500000"),
                currency="VND",
                frequency=Frequency.MONTHLY,
                start_date=date.today(),
                next_run_date=date.today() + timedelta(days=30),
                wallet_id=test_wallet.id,
                is_active=True,
                description="Monthly rent"
            ),
        ]
        for rec in recurrings:
            db_session.add(rec)
        db_session.commit()
        
        # Act
        response = test_client.get(
            "/v1/recurring-transactions", headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert any(r["description"] == "Daily coffee" for r in data)
        assert any(r["description"] == "Monthly rent" for r in data)
    
    def test_recurring_transaction_edge_case_month_end(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories
    ):
        """Test monthly recurring handles month-end dates correctly."""
        # Arrange - Start on Jan 31
        start_date = date(2024, 1, 31)
        payload = {
            "type": "EXPENSE",
            "amount": 300000,
            "currency": "VND",
            "frequency": "MONTHLY",
            "start_date": start_date.isoformat(),
            "category_id": test_categories[0].id,
            "wallet_id": test_wallet.id,
            "description": "Month-end test"
        }
        
        # Act
        response = test_client.post(
            "/v1/recurring-transactions", json=payload, headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        # Next run should handle Feb having fewer days
        next_run = date.fromisoformat(data["next_run_date"])
        assert next_run.month == 2  # February
        # Should be last day of February (28 or 29)
        assert next_run.day <= 29
