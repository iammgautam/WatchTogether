from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Replace with your actual POSTGRESQL credentials
# Format: postgresql://<username>:<password>@<host>:<port>/<database_name>

SQLALCHEMY_DATABASE_URL = "postgresql://mithilesh:kela@localhost:5432/watchtogether"

# The engine is responsible for establishing the core connection to the database
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal class will be used to create actual database sessions for our requests
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base class that our database models will inherit from
Base = declarative_base()
# Dependency to get the DB session in our FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()