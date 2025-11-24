"""API Integration tests for transaction endpoints with multi-condition filtering."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from decimal import Decimal


class TestTransactionAPI:
    """Test transaction API endpoints."""
    
    def test_create_expense_transaction(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories
    ):
        """Test creating an expense transaction."""
        # Arrange
        payload = {
            "type": "EXPENSE",
            "amount": 150000,
            "currency": "VND",
            "date": datetime.now().isoformat(),
            "category_id": test_categories[0].id,
            "wallet_id": test_wallet.id,
            "description": "Grocery shopping"
        }
        
        # Act
        response = test_client.post(
            "/api/v1/transactions", json=payload, headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "EXPENSE"
        assert float(data["amount"]) == 150000
        assert data["description"] == "Grocery shopping"
    
    def test_filter_transactions_by_date_range(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories, db_session
    ):
        """Test filtering transactions by date range."""
        # Arrange - Create transactions on different dates
        from app.models.transaction import Transaction, TransactionType
        
        base_date = datetime(2024, 1, 15)
        transactions = [
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("100000"),
                currency="VND",
                date=base_date,
                wallet_id=test_wallet.id
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("200000"),
                currency="VND",
                date=base_date + timedelta(days=10),
                wallet_id=test_wallet.id
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("300000"),
                currency="VND",
                date=base_date + timedelta(days=20),
                wallet_id=test_wallet.id
            ),
        ]
        for txn in transactions:
            db_session.add(txn)
        db_session.commit()
        
        # Act - Filter for middle period
        response = test_client.get(
            "/api/v1/transactions",
            params={
                "date_from": (base_date + timedelta(days=5)).isoformat(),
                "date_to": (base_date + timedelta(days=15)).isoformat()
            },
            headers=auth_headers
        )
        
        # Assert - Should only get the middle transaction
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert float(data["items"][0]["amount"]) == 200000
    
    def test_filter_transactions_by_category(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories, db_session
    ):
        """Test filtering transactions by category."""
        # Arrange - Create transactions with different categories
        from app.models.transaction import Transaction, TransactionType
        
        transactions = [
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("100000"),
                currency="VND",
                date=datetime.now(),
                category_id=test_categories[0].id,  # Food
                wallet_id=test_wallet.id
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("200000"),
                currency="VND",
                date=datetime.now(),
                category_id=test_categories[1].id,  # Transport
                wallet_id=test_wallet.id
            ),
        ]
        for txn in transactions:
            db_session.add(txn)
        db_session.commit()
        
        # Act - Filter by Food category
        response = test_client.get(
            "/api/v1/transactions",
            params={"category_id": test_categories[0].id},
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["category"]["name"] == "Food"
    
    def test_filter_transactions_by_amount_range(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories, db_session
    ):
        """Test filtering transactions by min_amount and max_amount."""
        # Arrange - Create transactions with different amounts
        from app.models.transaction import Transaction, TransactionType
        
        transactions = [
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("50000"),
                currency="VND",
                date=datetime.now(),
                wallet_id=test_wallet.id
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("150000"),
                currency="VND",
                date=datetime.now(),
                wallet_id=test_wallet.id
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("500000"),
                currency="VND",
                date=datetime.now(),
                wallet_id=test_wallet.id
            ),
        ]
        for txn in transactions:
            db_session.add(txn)
        db_session.commit()
        
        # Act - Filter for amounts between 100k and 300k
        response = test_client.get(
            "/api/v1/transactions",
            params={"min_amount": 100000, "max_amount": 300000},
            headers=auth_headers
        )
        
        # Assert - Should only get the 150k transaction
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert float(data["items"][0]["amount"]) == 150000
    
    def test_filter_transactions_multi_condition(
        self, test_client: TestClient, auth_headers, test_wallet, test_categories, db_session
    ):
        """Test filtering transactions with multiple conditions simultaneously."""
        # Arrange - Create diverse transactions
        from app.models.transaction import Transaction, TransactionType
        
        base_date = datetime(2024, 2, 1)
        transactions = [
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("200000"),
                currency="VND",
                date=base_date,
                category_id=test_categories[0].id,  # Food
                wallet_id=test_wallet.id,
                description="Target transaction"
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("100000"),  # Too small
                currency="VND",
                date=base_date,
                category_id=test_categories[0].id,
                wallet_id=test_wallet.id
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("200000"),
                currency="VND",
                date=base_date + timedelta(days=40),  # Outside date range
                category_id=test_categories[0].id,
                wallet_id=test_wallet.id
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("200000"),
                currency="VND",
                date=base_date,
                category_id=test_categories[1].id,  # Wrong category
                wallet_id=test_wallet.id
            ),
        ]
        for txn in transactions:
            db_session.add(txn)
        db_session.commit()
        
        # Act - Apply all filters at once
        response = test_client.get(
            "/api/v1/transactions",
            params={
                "date_from": base_date.isoformat(),
                "date_to": (base_date + timedelta(days=30)).isoformat(),
                "category_id": test_categories[0].id,
                "min_amount": 150000,
                "wallet_id": test_wallet.id,
                "type": "EXPENSE"
            },
            headers=auth_headers
        )
        
        # Assert - Should only match the target transaction
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["description"] == "Target transaction"
    
    def test_get_daily_grouped_transactions(
        self, test_client: TestClient, auth_headers, test_wallet, db_session
    ):
        """Test getting transactions grouped by day."""
        # Arrange - Create transactions on same day
        from app.models.transaction import Transaction, TransactionType
        
        target_date = datetime(2024, 3, 15, 10, 0)
        transactions = [
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("100000"),
                currency="VND",
                date=target_date,
                wallet_id=test_wallet.id
            ),
            Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal("150000"),
                currency="VND",
                date=target_date.replace(hour=15),
                wallet_id=test_wallet.id
            ),
        ]
        for txn in transactions:
            db_session.add(txn)
        db_session.commit()
        
        # Act
        response = test_client.get(
            "/api/v1/transactions/daily",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        # Find the target date group
        target_group = next((g for g in data if g["date"] == "2024-03-15"), None)
        assert target_group is not None
        assert float(target_group["total_amount"]) == 250000
        assert target_group["transaction_count"] == 2
    
    def test_pagination(
        self, test_client: TestClient, auth_headers, test_wallet, db_session
    ):
        """Test transaction list pagination."""
        # Arrange - Create many transactions
        from app.models.transaction import Transaction, TransactionType
        
        for i in range(15):
            txn = Transaction(
                user_id=test_wallet.user_id,
                type=TransactionType.EXPENSE,
                amount=Decimal(str((i + 1) * 10000)),
                currency="VND",
                date=datetime.now(),
                wallet_id=test_wallet.id
            )
            db_session.add(txn)
        db_session.commit()
        
        # Act - Get first page with size 10
        response = test_client.get(
            "/api/v1/transactions",
            params={"page": 1, "size": 10},
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["pages"] == 2
