import datetime
from typing import Union

from pydantic import BaseModel


class VoterBase(BaseModel):
    email: str
    name: str


class VoterCreate(VoterBase):
    pass


class Voter(VoterBase):
    id: int
    creation_time: datetime.datetime
    update_time: Union[datetime.datetime, None] = None

    class Config:
        orm_mode = True
