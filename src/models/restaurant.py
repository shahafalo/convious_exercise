import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy_utils import URLType

from db.base_class import Base


class Restaurant(Base):
    __tablename__ = "restaurant"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    phone = Column(String)
    website = Column(URLType)
    notes = Column(String)

    creation_time = Column(DateTime, default=datetime.datetime.now)
    update_time = Column(DateTime, default=datetime.datetime.now, nullable=True)
