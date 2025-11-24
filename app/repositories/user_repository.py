"""User repository for database operations."""
from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User


class UserRepository:
    """Repository for User entity database operations."""
    
    def create(self, db: Session, email: str, hashed_password: str, full_name: str) -> User:
        """Create a new user."""
        user = User(email=email, hashed_password=hashed_password, full_name=full_name)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    def exists_by_email(self, db: Session, email: str) -> bool:
        """Check if user exists by email."""
        return db.query(User).filter(User.email == email).count() > 0


user_repository = UserRepository()
