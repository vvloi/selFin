"""Test configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from typing import Generator
from app.db.base import Base
from app.models.user import User
from app.models.wallet import Wallet
from app.models.category import Category, CategoryType
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.recurring_transaction import RecurringTransaction
from app.core.security import get_password_hash
from decimal import Decimal


# Create test engine once at module level
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a test database session.
    
    Each test gets a session connected to the test database.
    Uses a single connection to ensure tables persist.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    # Create tables for this test
    Base.metadata.create_all(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function", autouse=False)
def setup_test_database():
    """DEPRECATED - keeping for reference but not used."""
    pass


@pytest.fixture(scope="function")
def test_client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with overridden database dependency."""
    from app.main import app
    from app.db.session import get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_client: TestClient, db_session: Session) -> User:
    """Create a test user.
    
    Note: Depends on test_client to ensure DB override is set before user is created.
    """
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user: User) -> str:
    """Get authentication token for test user.
    
    Creates token directly instead of going through login endpoint.
    """
    from app.core.security import create_access_token
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def auth_headers(test_user_token: str) -> dict:
    """Get authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def test_wallet(db_session: Session, test_user: User) -> Wallet:
    """Create a test wallet."""
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
def test_categories(db_session: Session, test_user: User) -> list[Category]:
    """Create test categories."""
    categories = [
        Category(user_id=test_user.id, name="Food", type=CategoryType.EXPENSE),
        Category(user_id=test_user.id, name="Transport", type=CategoryType.EXPENSE),
        Category(user_id=test_user.id, name="Shopping", type=CategoryType.EXPENSE),
        Category(user_id=test_user.id, name="Salary", type=CategoryType.INCOME),
    ]
    for cat in categories:
        db_session.add(cat)
    db_session.commit()
    for cat in categories:
        db_session.refresh(cat)
    return categories
