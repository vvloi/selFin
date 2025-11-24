"""Tests for transaction service."""
import pytest
from datetime import datetime
from decimal import Decimal
from app.services.transaction_service import transaction_service
from app.services.auth_service import auth_service
from app.repositories.wallet_repository import wallet_repository
from app.repositories.category_repository import category_repository
from app.models.transaction import TransactionType
from app.models.category import CategoryType
from fastapi import HTTPException


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    return auth_service.register_user(
        db_session,
        email="test@example.com",
        password="password123",
        full_name="Test User"
    )


@pytest.fixture
def test_wallet(db_session, test_user):
    """Create a test wallet."""
    return wallet_repository.create(
        db_session,
        user_id=test_user.id,
        name="Test Wallet",
        currency="VND",
        initial_balance=10000.0
    )


@pytest.fixture
def test_category(db_session, test_user):
    """Create a test category."""
    return category_repository.create(
        db_session,
        user_id=test_user.id,
        name="Food",
        category_type=CategoryType.EXPENSE
    )


def test_create_expense_transaction(db_session, test_user, test_wallet, test_category):
    """Test creating an expense transaction."""
    initial_balance = test_wallet.balance
    
    transaction = transaction_service.create_transaction(
        db_session,
        user_id=test_user.id,
        transaction_type=TransactionType.EXPENSE,
        amount=100.0,
        currency="VND",
        transaction_date=datetime.now(),
        category_id=test_category.id,
        wallet_id=test_wallet.id,
        description="Test expense"
    )
    
    assert transaction.id is not None
    assert transaction.type == TransactionType.EXPENSE
    assert transaction.amount == Decimal("100.0")
    
    # Check wallet balance decreased
    db_session.refresh(test_wallet)
    assert test_wallet.balance == initial_balance - Decimal("100.0")


def test_create_income_transaction(db_session, test_user, test_wallet, test_category):
    """Test creating an income transaction."""
    initial_balance = test_wallet.balance
    
    transaction = transaction_service.create_transaction(
        db_session,
        user_id=test_user.id,
        transaction_type=TransactionType.INCOME,
        amount=500.0,
        currency="VND",
        transaction_date=datetime.now(),
        category_id=test_category.id,
        wallet_id=test_wallet.id,
        description="Test income"
    )
    
    assert transaction.type == TransactionType.INCOME
    
    # Check wallet balance increased
    db_session.refresh(test_wallet)
    assert test_wallet.balance == initial_balance + Decimal("500.0")


def test_create_transfer_transaction(db_session, test_user):
    """Test creating a transfer transaction."""
    wallet1 = wallet_repository.create(
        db_session, test_user.id, "Wallet 1", "VND", 1000.0
    )
    wallet2 = wallet_repository.create(
        db_session, test_user.id, "Wallet 2", "VND", 500.0
    )
    
    initial_balance1 = wallet1.balance
    initial_balance2 = wallet2.balance
    
    transaction = transaction_service.create_transaction(
        db_session,
        user_id=test_user.id,
        transaction_type=TransactionType.TRANSFER,
        amount=200.0,
        currency="VND",
        transaction_date=datetime.now(),
        wallet_id=wallet1.id,
        to_wallet_id=wallet2.id,
        description="Transfer test"
    )
    
    assert transaction.type == TransactionType.TRANSFER
    
    # Check balances updated correctly
    db_session.refresh(wallet1)
    db_session.refresh(wallet2)
    
    assert wallet1.balance == initial_balance1 - Decimal("200.0")
    assert wallet2.balance == initial_balance2 + Decimal("200.0")


def test_create_transaction_invalid_amount(db_session, test_user, test_wallet):
    """Test creating transaction with invalid amount fails."""
    with pytest.raises(HTTPException) as exc_info:
        transaction_service.create_transaction(
            db_session,
            user_id=test_user.id,
            transaction_type=TransactionType.EXPENSE,
            amount=0.0,
            currency="VND",
            transaction_date=datetime.now(),
            wallet_id=test_wallet.id
        )
    
    assert exc_info.value.status_code == 400


def test_delete_transaction_reverts_balance(db_session, test_user, test_wallet, test_category):
    """Test deleting transaction reverts wallet balance."""
    initial_balance = test_wallet.balance
    
    transaction = transaction_service.create_transaction(
        db_session,
        user_id=test_user.id,
        transaction_type=TransactionType.EXPENSE,
        amount=100.0,
        currency="VND",
        transaction_date=datetime.now(),
        category_id=test_category.id,
        wallet_id=test_wallet.id
    )
    
    # Balance should be decreased
    db_session.refresh(test_wallet)
    assert test_wallet.balance == initial_balance - Decimal("100.0")
    
    # Delete transaction
    transaction_service.delete_transaction(db_session, transaction.id, test_user.id)
    
    # Balance should be restored
    db_session.refresh(test_wallet)
    assert test_wallet.balance == initial_balance


def test_get_transactions_with_filters(db_session, test_user, test_wallet, test_category):
    """Test getting transactions with filters."""
    # Create multiple transactions
    for i in range(5):
        transaction_service.create_transaction(
            db_session,
            user_id=test_user.id,
            transaction_type=TransactionType.EXPENSE,
            amount=100.0 * (i + 1),
            currency="VND",
            transaction_date=datetime.now(),
            category_id=test_category.id,
            wallet_id=test_wallet.id
        )
    
    # Get all transactions
    transactions, total = transaction_service.get_transactions_with_filters(
        db_session,
        user_id=test_user.id,
        page=1,
        size=10
    )
    
    assert total >= 5
    assert len(transactions) >= 5


def test_group_transactions_by_date(db_session, test_user, test_wallet, test_category):
    """Test grouping transactions by date."""
    transaction_service.create_transaction(
        db_session,
        user_id=test_user.id,
        transaction_type=TransactionType.EXPENSE,
        amount=100.0,
        currency="VND",
        transaction_date=datetime.now(),
        category_id=test_category.id,
        wallet_id=test_wallet.id
    )
    
    grouped = transaction_service.get_daily_grouped_transactions(
        db_session,
        user_id=test_user.id
    )
    
    assert len(grouped) > 0
    assert 'date' in grouped[0]
    assert 'total_expense' in grouped[0]
    assert 'transactions' in grouped[0]
