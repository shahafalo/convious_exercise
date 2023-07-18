from src.schemas import restaurant
from src.crud import restaurant_crud
from src.schemas.restaurant import RestaurantCreate


def test_get_restaurant(db, db_restaurant):
    results = restaurant_crud.get_restaurants_by_ids([db_restaurant.id], db)
    assert results
    res = results[0]
    assert res.name == db_restaurant.name
    assert res.address == db_restaurant.address
    assert res.phone == db_restaurant.phone
    assert res.website == db_restaurant.website
    assert res.notes == db_restaurant.notes


def test_get_restaurants(db, db_restaurant):
    res = restaurant_crud.get_restaurants(db)
    assert len(res) == 1
    assert res[0].id == db_restaurant.id


def test_create_restaurant(db, new_restaurant_json):
    res = restaurant_crud.create_restaurant(RestaurantCreate(**new_restaurant_json),
                                            db)
    assert res.id
    assert res.name == new_restaurant_json["name"]
    assert res.phone == new_restaurant_json["phone"]
    assert res.website == new_restaurant_json["website"]
    assert res.address == new_restaurant_json["address"]
    assert res.notes == new_restaurant_json["notes"]


def test_update_restaurant(db, db_restaurant):
    changed_notes = "temp_changed"
    assert db_restaurant.notes != changed_notes

    restaurant_json = restaurant.Restaurant.from_orm(db_restaurant)
    restaurant_json.notes = changed_notes
    restaurant_crud.update_restaurant(restaurant_json, db)

    res = restaurant_crud.get_restaurants_by_ids([db_restaurant.id], db)[0]
    assert res.notes == changed_notes


def test_delete_restaurant(db, db_restaurant):
    restaurant_crud.delete_restaurant(db_restaurant.id, db)
    res = restaurant_crud.get_restaurants_by_ids([db_restaurant.id], db)
    assert not res
