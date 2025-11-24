"""Category repository for database operations."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.category import Category, CategoryType


class CategoryRepository:
    """Repository for Category entity database operations."""
    
    def create(
        self,
        db: Session,
        user_id: int,
        name: str,
        category_type: CategoryType,
        icon: Optional[str] = None,
        color: Optional[str] = None
    ) -> Category:
        """Create a new category."""
        category = Category(
            user_id=user_id,
            name=name,
            type=category_type,
            icon=icon,
            color=color
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    
    def get_by_id(self, db: Session, category_id: int, user_id: int) -> Optional[Category]:
        """Get category by ID for a specific user."""
        return db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == user_id
        ).first()
    
    def get_all_by_user(self, db: Session, user_id: int) -> List[Category]:
        """Get all categories for a user."""
        return db.query(Category).filter(Category.user_id == user_id).all()


category_repository = CategoryRepository()
