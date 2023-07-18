from sqlalchemy.orm import Session

from models.restaurant import Restaurant
import schemas


def get_restaurants_by_ids(restaurant_ids: list[int], db: Session) -> list[Restaurant]:
    return db.query(Restaurant).filter(Restaurant.id.in_(restaurant_ids)).all()


def get_restaurant_by_name(restaurant_name: str, db: Session):
    # todo: add tests
    return db.query(Restaurant).filter(Restaurant.name == restaurant_name).first()


def get_restaurants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Restaurant).offset(skip).limit(limit).all()


def create_restaurant(restaurant: schemas.restaurant.RestaurantCreate, db: Session):
    # todo: refactor objects names to be clear what is db object and what is schema
    db_restaurant = Restaurant(**restaurant.dict())
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant


def delete_restaurant(restaurant_id: int, db: Session):
    restaurant = db.get(Restaurant, restaurant_id)
    if not restaurant:
        return None
    db.delete(restaurant)
    db.commit()
    return restaurant


def update_restaurant(restaurant: schemas.restaurant.Restaurant, db: Session):
    db_restaurant = db.get(Restaurant, restaurant.id)
    if not db_restaurant:
        return None

    # coping all the data from the input as source of truth, except id
    db_restaurant.name = restaurant.name
    db_restaurant.address = restaurant.address
    db_restaurant.phone = restaurant.phone
    db_restaurant.website = restaurant.website
    db_restaurant.notes = restaurant.notes

    db.commit()
    return db_restaurant
