"""Database base configuration."""
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


# Note: Models are imported in conftest.py and alembic env.py to avoid circular imports
# Do not import models here
