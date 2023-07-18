from typing import Union

from pydantic import BaseModel, HttpUrl


class RestaurantBase(BaseModel):
    name: str
    address: Union[str, None] = None
    phone: Union[str, None] = None
    website: Union[HttpUrl, None] = None
    notes: Union[str, None] = None


class RestaurantCreate(RestaurantBase):
    pass


class Restaurant(RestaurantBase):
    id: int

    class Config:
        from_attributes = True
        orm_mode = True
