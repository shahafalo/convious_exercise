import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

engine = db.create_engine("sqlite:///dev.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
