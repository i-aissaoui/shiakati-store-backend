from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Use hardcoded connection string with known working credentials
DATABASE_URL = "postgresql://shiakati:shiakati@localhost:5432/shiakati"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 