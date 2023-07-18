from typing import Union
from pydantic import BaseModel


class Result(BaseModel):
    restaurant_id: Union[int, None] = None
    score: Union[float, None] = None


class Winner(BaseModel):
    restaurant_id: int
