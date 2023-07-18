from typing import Union
from sqlalchemy.orm import Session

from fastapi import APIRouter, HTTPException, Depends

from src.schemas.restaurant import Restaurant, RestaurantCreate
from src.crud import restaurant_crud
from src.db.utils import get_db

router = APIRouter()


@router.get("/", response_model=list[Restaurant])
async def read_restaurants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return restaurant_crud.get_restaurants(db, skip, limit)


@router.get("/{restaurant_id}", response_model=Union[Restaurant, None])
async def read_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    results = restaurant_crud.get_restaurants_by_ids([restaurant_id], db)
    if not results:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return Restaurant.from_orm(results[0])


@router.post("/", response_model=Restaurant)
async def create_restaurant(restaurant_in: RestaurantCreate, db: Session = Depends(get_db)):
    if not restaurant_in.name:
        raise HTTPException(status_code=400, detail="Restaurant name can't be empty")
    other_db_restaurant = restaurant_crud.get_restaurant_by_name(restaurant_in.name, db)
    if other_db_restaurant:
        raise HTTPException(status_code=409, detail=f"Restaurant name already taken."
                                                    f" Restaurant id: {other_db_restaurant.id}")
    db_restaurant = restaurant_crud.create_restaurant(restaurant_in, db)
    return Restaurant.from_orm(db_restaurant)


@router.put("/{restaurant_id}", response_model=Restaurant)
async def update_restaurant(restaurant_id: int, restaurant_in: Restaurant, db: Session = Depends(get_db)):
    if not restaurant_crud.get_restaurants_by_ids([restaurant_id], db):
        raise HTTPException(status_code=404, detail="Restaurant not found")
    db_restaurant = restaurant_crud.update_restaurant(restaurant_in, db)
    return Restaurant.from_orm(db_restaurant)


@router.delete("/{restaurant_id}", response_model=Union[Restaurant, None])
async def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    db_restaurant = restaurant_crud.delete_restaurant(restaurant_id, db)
    if not db_restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return Restaurant.from_orm(db_restaurant)
