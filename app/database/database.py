from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database URL using pymssql
# SQLALCHEMY_DATABASE_URL = f"mssql+pymssql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_SERVER}/{settings.DB_NAME}"
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_SERVER}/{settings.DB_NAME}?driver=SQL+Server"

# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()