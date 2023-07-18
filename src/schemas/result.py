from typing import Union
from pydantic import BaseModel


class Result(BaseModel):
    restaurant_id: int
    score: Union[float, None] = None


class Winner(BaseModel):
    restaurant_id: int
