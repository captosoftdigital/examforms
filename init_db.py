import os
import sys
from sqlalchemy import create_engine
from src.database.models import Base

# Setup paths
sys.path.append(os.path.join(os.getcwd(), 'src'))

DB_URL = 'sqlite:///db.sqlite3'

def init_db():
    print(f"Initializing database at {DB_URL}...")
    engine = create_engine(DB_URL)
    
    # Create all tables defined in models.py
    Base.metadata.create_all(engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()
