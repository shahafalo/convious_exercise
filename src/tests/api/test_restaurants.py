

def test_read_restaurant(client, some_restaurant) -> None:
    response = client.get(
        f"/restaurants/{some_restaurant['id']}"
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == some_restaurant["name"]
    assert content["address"] == some_restaurant["address"]
    assert content["phone"] == some_restaurant["phone"]
    assert content["website"] == some_restaurant["website"]


def test_read_restaurants(client, multiple_restaurants) -> None:
    response = client.get(f"/restaurants")
    assert response.status_code == 200
    new_restaurants = response.json()
    assert len(new_restaurants) == len(multiple_restaurants)

    restaurant_by_id = {rest["id"]: rest for rest in new_restaurants}
    for rest in multiple_restaurants:
        new_rest = restaurant_by_id[rest.id]
        assert rest.id == new_rest["id"]
        assert rest.name == new_rest["name"]
        assert rest.address == new_rest["address"]
        assert rest.phone == new_rest["phone"]
        assert rest.website == new_rest["website"]
        assert rest.notes == new_rest["notes"]


def test_create_restaurant(client, db, new_restaurant_json) -> None:

    response = client.post(f"/restaurants/", json=new_restaurant_json)

    assert response.status_code == 200, response.json()
    content = response.json()
    assert content["name"] == new_restaurant_json["name"]
    assert content["address"] == new_restaurant_json["address"]
    assert content["phone"] == new_restaurant_json["phone"]
    assert content["website"] == new_restaurant_json["website"]


def test_update_restaurant(fakerer, client, some_restaurant) -> None:
    new_phone = fakerer.phone_number()
    some_restaurant["phone"] = new_phone
    response = client.put(
        f"/restaurants/{some_restaurant['id']}", json=some_restaurant,
    )
    assert response.status_code == 200, response.json()
    content = response.json()
    assert content["phone"] == some_restaurant["phone"] == new_phone
    # unchanged:
    assert content["name"] == some_restaurant["name"]
    assert content["address"] == some_restaurant["address"]
    assert content["website"] == some_restaurant["website"]


def test_delete_restaurant(client, some_restaurant) -> None:
    response = client.delete(
        f"/restaurants/{some_restaurant['id']}"
    )
    assert response.status_code == 200, response.json()
    content = response.json()
    assert content["name"] == some_restaurant["name"]
    assert content["address"] == some_restaurant["address"]
    assert content["phone"] == some_restaurant["phone"]
    assert content["website"] == some_restaurant["website"]

    response = client.get(
        f"/restaurants/{some_restaurant['id']}"
    )
    assert response.status_code == 404
