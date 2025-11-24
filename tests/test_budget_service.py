"""Tests for budget service."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from app.services.budget_service import budget_service
from app.services.auth_service import auth_service
from app.repositories.category_repository import category_repository
from app.models.budget import PeriodType
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
def test_category(db_session, test_user):
    """Create a test category."""
    return category_repository.create(
        db_session,
        user_id=test_user.id,
        name="Food",
        category_type=CategoryType.EXPENSE
    )


def test_create_budget_monthly(db_session, test_user, test_category):
    """Test creating a monthly budget."""
    budget = budget_service.create_budget(
        db_session,
        user_id=test_user.id,
        category_id=test_category.id,
        amount_limit=1000.0,
        period_type=PeriodType.MONTHLY
    )
    
    assert budget.id is not None
    assert budget.amount_limit == Decimal("1000.0")
    assert budget.period_type == PeriodType.MONTHLY
    assert budget.category_id == test_category.id


def test_create_budget_custom_period(db_session, test_user, test_category):
    """Test creating a custom period budget."""
    start = date.today()
    end = start + timedelta(days=30)
    
    budget = budget_service.create_budget(
        db_session,
        user_id=test_user.id,
        category_id=test_category.id,
        amount_limit=500.0,
        period_type=PeriodType.CUSTOM,
        start_date=start,
        end_date=end
    )
    
    assert budget.period_type == PeriodType.CUSTOM
    assert budget.start_date == start
    assert budget.end_date == end


def test_create_budget_invalid_amount(db_session, test_user, test_category):
    """Test creating budget with invalid amount fails."""
    with pytest.raises(HTTPException) as exc_info:
        budget_service.create_budget(
            db_session,
            user_id=test_user.id,
            category_id=test_category.id,
            amount_limit=0.0,
            period_type=PeriodType.MONTHLY
        )
    
    assert exc_info.value.status_code == 400


def test_budget_enrichment_with_usage(db_session, test_user, test_category):
    """Test budget enrichment with usage information."""
    budget = budget_service.create_budget(
        db_session,
        user_id=test_user.id,
        category_id=test_category.id,
        amount_limit=1000.0,
        period_type=PeriodType.MONTHLY
    )
    
    # Budget should be enriched with usage info
    assert hasattr(budget, 'used_amount')
    assert hasattr(budget, 'remaining_amount')
    assert hasattr(budget, 'usage_percentage')
    assert hasattr(budget, 'is_near_limit')
    assert hasattr(budget, 'is_exceeded')
    
    # Initial values
    assert budget.used_amount == 0.0
    assert budget.remaining_amount == 1000.0
    assert budget.usage_percentage == 0.0
    assert budget.is_near_limit is False
    assert budget.is_exceeded is False


def test_get_all_budgets(db_session, test_user, test_category):
    """Test getting all budgets for a user."""
    budget_service.create_budget(
        db_session,
        user_id=test_user.id,
        category_id=test_category.id,
        amount_limit=1000.0,
        period_type=PeriodType.MONTHLY
    )
    
    budgets = budget_service.get_all_budgets(db_session, test_user.id)
    
    assert len(budgets) > 0
    assert all(hasattr(b, 'used_amount') for b in budgets)
