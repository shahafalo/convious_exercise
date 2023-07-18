import datetime

from sqlalchemy import Column, Integer, DateTime, String

from db.base_class import Base


class Voter(Base):
    __tablename__ = "voter"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)

    creation_time = Column(DateTime, default=datetime.datetime.now)
    update_time = Column(DateTime, default=datetime.datetime.now, nullable=True)
