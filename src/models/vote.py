import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.db.base_class import Base


class Vote(Base):
    __tablename__ = "vote"
    id = Column(Integer, primary_key=True, index=True)
    voter_id = Column(Integer, ForeignKey("voter.id"), nullable=False)
    voter = relationship("Voter", backref="votes")
    restaurant_id = Column(Integer, ForeignKey("restaurant.id"), nullable=True)
    restaurant = relationship("Restaurant", backref="votes")
    vote_score = Column(Integer, nullable=False)
    vote_time = Column(DateTime, default=datetime.datetime.now)
    creation_time = Column(DateTime, default=datetime.datetime.now)
    update_time = Column(DateTime, default=datetime.datetime.now, nullable=True)
