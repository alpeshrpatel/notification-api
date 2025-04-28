# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from app.config import settings

# # Create database URL using pymssql
# # SQLALCHEMY_DATABASE_URL = f"mssql+pymssql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_SERVER}/{settings.DB_NAME}"
# SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_SERVER}/{settings.DB_NAME}?driver=SQL+Server"

# # Create SQLAlchemy engine
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL
# )

# # Create SessionLocal class
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Create Base class
# Base = declarative_base()

# # Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from app.config import settings
# import urllib.parse


# # Using MySQL Connector
# encoded_password = urllib.parse.quote_plus(settings.DB_PASSWORD)
# SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{settings.DB_USERNAME}:{encoded_password}@{settings.DB_SERVER}:{settings.DB_PORT}/{settings.DB_NAME}"

# # Alternatively using PyMySQL
# # SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# # Dependency to get DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()






from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from fastapi import Depends  # Import Depends from FastAPI
from app.config import settings
import urllib.parse
import mysql.connector

from contextlib import asynccontextmanager
import aiomysql

encoded_password = urllib.parse.quote_plus(settings.DB_PASSWORD)
# SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{settings.DB_USERNAME}:{encoded_password}@{settings.DB_SERVER}/{settings.DB_NAME}"


# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL
# )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Improved dependency to get DB session with retry logic
# async def get_db():
#     async with aiomysql.connect(
#         host=settings.DB_SERVER,
#         port=3000,
#         user=settings.DB_USERNAME,
#         password=encoded_password,
#         db=settings.DB_NAME,
#     ) as connection:
#         async with connection.cursor() as cursor:
#             try:
#                 yield cursor
#             except mysql.connector.Error as e:
#                 # Log error here if you have a logger configured
#                 print(f"Database connection error: {e}")
#                 raise
#             finally:
#                 await connection.close()
    # db = None
    # try:
    #     print(f"trying Database connection ")
    #     db = SessionLocal()
    #     yield db
    #     print(f"hello Database connection ")
    # except mysql.connector.Error as e:
    #     # Log error here if you have a logger configured
    #     print(f"Database connection error: {e}")
    #     if db:
    #         db.rollback()
    #     raise
    # finally:
    #     if db: 
    #         db.close()
    #         print(f"closing Database connection ")




async def get_db():
    conn = await aiomysql.connect(
        host=settings.DB_SERVER,
        port=3306,
        user=settings.DB_USERNAME,
        password=settings.DB_PASSWORD,
        db=settings.DB_NAME,
    )
    try:
        yield conn
    finally:
        conn.close()



# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import NullPool
# from app.config import settings
# import urllib.parse

# # Use PyMySQL instead
# encoded_password = urllib.parse.quote_plus(settings.DB_PASSWORD)
# SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.DB_USERNAME}:{encoded_password}@{settings.DB_SERVER}:{settings.DB_PORT}/{settings.DB_NAME}"

# # Configure engine with more conservative settings
# # engine = create_engine(
# #     SQLALCHEMY_DATABASE_URL,
# #     pool_size=5,
# #     max_overflow=10,
# #     pool_timeout=30,
# #     pool_recycle=1800,  # Recycle connections after 30 minutes
# #     pool_pre_ping=True,
# #     echo=True  # Enable SQL logging for debugging
# # )
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     poolclass=NullPool,  # Disable connection pooling
#     connect_args={
#         "connect_timeout": 60,
#     }
# )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()