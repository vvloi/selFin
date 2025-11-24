"""Tests for recurring transaction service."""
import pytest
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.recurring_service import recurring_service
from app.models.recurring_transaction import Frequency
from app.models.transaction import TransactionType
from app.models.user import User
from app.models.wallet import Wallet
from app.models.category import Category, CategoryType


@pytest.fixture
def test_user(db_session):
    """Create test user."""
    user = User(email="recurring@test.com", hashed_password="hashed", full_name="Recurring Test")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_wallet(db_session, test_user):
    """Create test wallet."""
    wallet = Wallet(
        user_id=test_user.id,
        name="Test Wallet",
        currency="VND",
        balance=Decimal("10000000")
    )
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    return wallet


@pytest.fixture
def test_category(db_session, test_user):
    """Create test category."""
    category = Category(user_id=test_user.id, name="Subscription", type=CategoryType.EXPENSE)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


def test_create_recurring_transaction_daily(db_session, test_user, test_wallet, test_category):
    """Test creating a daily recurring transaction."""
    start_date = date.today()
    
    recurring = recurring_service.create_recurring_transaction(
        db_session,
        test_user.id,
        TransactionType.EXPENSE,
        50000.0,
        "VND",
        Frequency.DAILY,
        start_date,
        test_category.id,
        test_wallet.id
    )
    
    assert recurring is not None
    assert recurring.user_id == test_user.id
    assert recurring.amount == Decimal("50000")
    assert recurring.frequency == Frequency.DAILY
    assert recurring.start_date == start_date
    assert recurring.next_run_date == start_date + timedelta(days=1)
    assert recurring.is_active is True


def test_create_recurring_transaction_monthly(db_session, test_user, test_wallet, test_category):
    """Test creating a monthly recurring transaction."""
    start_date = date(2024, 1, 15)
    
    recurring = recurring_service.create_recurring_transaction(
        db_session,
        test_user.id,
        TransactionType.EXPENSE,
        500000.0,
        "VND",
        Frequency.MONTHLY,
        start_date,
        test_category.id,
        test_wallet.id,
        description="Monthly subscription"
    )
    
    assert recurring is not None
    assert recurring.frequency == Frequency.MONTHLY
    assert recurring.start_date == start_date
    # Next run should be one month later
    expected_next = start_date + relativedelta(months=1)
    assert recurring.next_run_date == expected_next
    assert recurring.description == "Monthly subscription"


def test_create_recurring_transaction_invalid_amount(db_session, test_user, test_wallet):
    """Test creating recurring transaction with invalid amount."""
    with pytest.raises(HTTPException) as exc_info:
        recurring_service.create_recurring_transaction(
            db_session,
            test_user.id,
            TransactionType.EXPENSE,
            -100.0,  # Invalid negative amount
            "VND",
            Frequency.MONTHLY,
            date.today(),
            wallet_id=test_wallet.id
        )
    
    assert exc_info.value.status_code == 400
    assert "greater than zero" in exc_info.value.detail.lower()


def test_calculate_next_run_date_weekly(db_session, test_user, test_wallet, test_category):
    """Test next run date calculation for weekly frequency."""
    start_date = date(2024, 1, 1)  # Monday
    
    recurring = recurring_service.create_recurring_transaction(
        db_session,
        test_user.id,
        TransactionType.EXPENSE,
        100000.0,
        "VND",
        Frequency.WEEKLY,
        start_date,
        test_category.id,
        test_wallet.id
    )
    
    expected_next = start_date + timedelta(weeks=1)
    assert recurring.next_run_date == expected_next


def test_calculate_next_run_date_yearly(db_session, test_user, test_wallet, test_category):
    """Test next run date calculation for yearly frequency."""
    start_date = date(2024, 3, 15)
    
    recurring = recurring_service.create_recurring_transaction(
        db_session,
        test_user.id,
        TransactionType.EXPENSE,
        1000000.0,
        "VND",
        Frequency.YEARLY,
        start_date,
        test_category.id,
        test_wallet.id,
        description="Annual subscription"
    )
    
    expected_next = start_date + relativedelta(years=1)
    assert recurring.next_run_date == expected_next


def test_process_due_recurring_transactions(db_session, test_user, test_wallet, test_category):
    """Test processing due recurring transactions."""
    # Create a recurring transaction that's due (next_run_date is in the past)
    past_date = date.today() - timedelta(days=5)
    
    recurring = recurring_service.create_recurring_transaction(
        db_session,
        test_user.id,
        TransactionType.EXPENSE,
        200000.0,
        "VND",
        Frequency.DAILY,
        past_date,
        test_category.id,
        test_wallet.id,
        description="Past due transaction"
    )
    
    # Manually set next_run_date to yesterday to make it due
    recurring.next_run_date = date.today() - timedelta(days=1)
    db_session.commit()
    
    initial_balance = test_wallet.balance
    
    # Process due transactions
    processed = recurring_service.process_due_recurring_transactions(db_session)
    
    assert len(processed) > 0
    
    # Verify wallet balance was updated
    db_session.refresh(test_wallet)
    assert test_wallet.balance == initial_balance - Decimal("200000")
    
    # Verify next_run_date was updated
    db_session.refresh(recurring)
    assert recurring.next_run_date > date.today() - timedelta(days=1)
    assert recurring.last_run_date is not None


def test_deactivate_recurring_transaction(db_session, test_user, test_wallet, test_category):
    """Test deactivating a recurring transaction."""
    recurring = recurring_service.create_recurring_transaction(
        db_session,
        test_user.id,
        TransactionType.EXPENSE,
        100000.0,
        "VND",
        Frequency.MONTHLY,
        date.today(),
        test_category.id,
        test_wallet.id
    )
    
    assert recurring.is_active is True
    
    # Update to deactivate
    updated = recurring_service.update_recurring_transaction(
        db_session,
        recurring.id,
        test_user.id,
        is_active=False
    )
    
    assert updated.is_active is False


def test_get_all_recurring_transactions(db_session, test_user, test_wallet, test_category):
    """Test getting all recurring transactions for a user."""
    # Create multiple recurring transactions
    recurring_service.create_recurring_transaction(
        db_session, test_user.id, TransactionType.EXPENSE,
        50000.0, "VND", Frequency.DAILY, date.today(),
        test_category.id, test_wallet.id
    )
    
    recurring_service.create_recurring_transaction(
        db_session, test_user.id, TransactionType.EXPENSE,
        500000.0, "VND", Frequency.MONTHLY, date.today(),
        test_category.id, test_wallet.id
    )
    
    all_recurring = recurring_service.get_all_recurring(db_session, test_user.id)
    
    assert len(all_recurring) >= 2
    assert all(r.user_id == test_user.id for r in all_recurring)
