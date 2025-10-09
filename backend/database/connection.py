from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./opportunities.db")

try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    print(f"Error creating engine with DATABASE_URL: {e}. Falling back to SQLite.")
    DATABASE_URL = "sqlite:///./opportunities.db"
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()