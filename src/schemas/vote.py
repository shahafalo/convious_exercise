import datetime
from typing import Union

from pydantic import BaseModel


class VoteBase(BaseModel):
    voter_id: int
    restaurant_id: Union[int, None] = None


class VoteCreate(VoteBase):
    pass


class VoteUpdate(VoteBase):
    id: int

    class Config:
        from_attributes = True
        orm_mode = True


class Vote(VoteBase):
    id: int
    vote_score: float
    vote_time: datetime.datetime
    creation_time: datetime.datetime
    update_time: Union[datetime.datetime, None] = None

    class Config:
        from_attributes = True
        orm_mode = True
