"""Tests for analytics service."""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.services.analytics_service import analytics_service
from app.models.user import User
from app.models.wallet import Wallet
from app.models.category import Category, CategoryType
from app.models.transaction import Transaction, TransactionType


@pytest.fixture
def test_user(db_session):
    """Create test user."""
    user = User(email="analytics@test.com", hashed_password="hashed", full_name="Analytics Test")
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
def test_categories(db_session, test_user):
    """Create test categories."""
    categories = [
        Category(user_id=test_user.id, name="Food", type=CategoryType.EXPENSE),
        Category(user_id=test_user.id, name="Transport", type=CategoryType.EXPENSE),
        Category(user_id=test_user.id, name="Shopping", type=CategoryType.EXPENSE),
    ]
    for cat in categories:
        db_session.add(cat)
    db_session.commit()
    for cat in categories:
        db_session.refresh(cat)
    return categories


@pytest.fixture
def test_transactions(db_session, test_user, test_wallet, test_categories):
    """Create test transactions."""
    base_date = datetime(2024, 1, 15, 12, 0, 0)
    
    transactions = [
        Transaction(
            user_id=test_user.id,
            type=TransactionType.EXPENSE,
            amount=Decimal("500000"),
            currency="VND",
            date=base_date,
            category_id=test_categories[0].id,  # Food
            wallet_id=test_wallet.id,
            description="Grocery shopping"
        ),
        Transaction(
            user_id=test_user.id,
            type=TransactionType.EXPENSE,
            amount=Decimal("200000"),
            currency="VND",
            date=base_date + timedelta(days=1),
            category_id=test_categories[1].id,  # Transport
            wallet_id=test_wallet.id,
            description="Taxi"
        ),
        Transaction(
            user_id=test_user.id,
            type=TransactionType.EXPENSE,
            amount=Decimal("300000"),
            currency="VND",
            date=base_date + timedelta(days=2),
            category_id=test_categories[0].id,  # Food
            wallet_id=test_wallet.id,
            description="Restaurant"
        ),
        Transaction(
            user_id=test_user.id,
            type=TransactionType.EXPENSE,
            amount=Decimal("1000000"),
            currency="VND",
            date=base_date + timedelta(days=5),
            category_id=test_categories[2].id,  # Shopping
            wallet_id=test_wallet.id,
            description="Clothes"
        ),
    ]
    
    for txn in transactions:
        db_session.add(txn)
    db_session.commit()
    for txn in transactions:
        db_session.refresh(txn)
    return transactions


def test_get_spending_by_category(db_session, test_user, test_wallet, test_categories, test_transactions):
    """Test getting spending breakdown by category."""
    date_from = datetime(2024, 1, 1)
    date_to = datetime(2024, 1, 31)
    
    spending = analytics_service.get_spending_by_category(
        db_session, test_user.id, date_from, date_to
    )
    
    assert len(spending) == 3  # Three categories with transactions
    
    # Find Food category (should have 500000 + 300000 = 800000)
    food_spending = next((s for s in spending if s["category_name"] == "Food"), None)
    assert food_spending is not None
    assert food_spending["total_amount"] == Decimal("800000")
    
    # Find Shopping category (should have 1000000)
    shopping_spending = next((s for s in spending if s["category_name"] == "Shopping"), None)
    assert shopping_spending is not None
    assert shopping_spending["total_amount"] == Decimal("1000000")
    
    # Verify percentages sum to 100 (or close to it)
    total_percentage = sum(s["percentage"] for s in spending)
    assert 99.9 <= total_percentage <= 100.1


def test_get_spending_trend_by_month(db_session, test_user, test_wallet, test_categories, test_transactions):
    """Test getting spending trend grouped by month."""
    date_from = datetime(2024, 1, 1)
    date_to = datetime(2024, 12, 31)
    
    trend = analytics_service.get_spending_trend(
        db_session, test_user.id, date_from, date_to, group_by="month"
    )
    
    assert len(trend) > 0
    
    # January 2024 should have total of all test transactions
    jan_trend = next((t for t in trend if t["year"] == 2024 and t["month"] == 1), None)
    assert jan_trend is not None
    # Total: 500000 + 200000 + 300000 + 1000000 = 2000000
    assert jan_trend["total_expense"] == Decimal("2000000")


def test_get_spending_trend_by_day(db_session, test_user, test_wallet, test_categories, test_transactions):
    """Test getting spending trend grouped by day."""
    date_from = datetime(2024, 1, 1)
    date_to = datetime(2024, 1, 31)
    
    trend = analytics_service.get_spending_trend(
        db_session, test_user.id, date_from, date_to, group_by="day"
    )
    
    assert len(trend) > 0
    
    # Should have entries for days with transactions
    assert any(t["total_expense"] == Decimal("500000") for t in trend)  # First day
    assert any(t["total_expense"] == Decimal("200000") for t in trend)  # Second day
    assert any(t["total_expense"] == Decimal("300000") for t in trend)  # Third day


def test_get_top_categories(db_session, test_user, test_wallet, test_categories, test_transactions):
    """Test getting top spending categories."""
    date_from = datetime(2024, 1, 1)
    date_to = datetime(2024, 1, 31)
    
    top_categories = analytics_service.get_top_categories(
        db_session, test_user.id, date_from, date_to, limit=2
    )
    
    assert len(top_categories) == 2
    
    # Shopping should be #1 (1000000)
    assert top_categories[0]["category_name"] == "Shopping"
    assert top_categories[0]["total_amount"] == Decimal("1000000")
    
    # Food should be #2 (800000)
    assert top_categories[1]["category_name"] == "Food"
    assert top_categories[1]["total_amount"] == Decimal("800000")


def test_get_top_categories_with_limit(db_session, test_user, test_wallet, test_categories, test_transactions):
    """Test getting top categories respects limit parameter."""
    date_from = datetime(2024, 1, 1)
    date_to = datetime(2024, 1, 31)
    
    top_categories = analytics_service.get_top_categories(
        db_session, test_user.id, date_from, date_to, limit=1
    )
    
    assert len(top_categories) == 1
    assert top_categories[0]["category_name"] == "Shopping"


def test_spending_by_category_empty_period(db_session, test_user):
    """Test spending by category with no transactions in period."""
    date_from = datetime(2025, 1, 1)  # Future date
    date_to = datetime(2025, 1, 31)
    
    spending = analytics_service.get_spending_by_category(
        db_session, test_user.id, date_from, date_to
    )
    
    assert len(spending) == 0


def test_spending_trend_empty_period(db_session, test_user):
    """Test spending trend with no transactions in period."""
    date_from = datetime(2025, 1, 1)  # Future date
    date_to = datetime(2025, 1, 31)
    
    trend = analytics_service.get_spending_trend(
        db_session, test_user.id, date_from, date_to, group_by="month"
    )
    
    assert len(trend) == 0
