

def test_read_voter(client, some_voter) -> None:
    response = client.get(
        f"/voters/{some_voter['id']}"
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == some_voter["name"]
    assert content["email"] == some_voter["email"]


def test_read_voters(client, multiple_voters) -> None:
    response = client.get(f"/voters")
    assert response.status_code == 200
    new_voters = response.json()
    assert len(new_voters) == len(multiple_voters)

    voter_by_id = {rest["id"]: rest for rest in new_voters}
    for rest in multiple_voters:
        new_rest = voter_by_id[rest.id]
        assert rest.id == new_rest["id"]
        assert rest.name == new_rest["name"]
        assert rest.email == new_rest["email"]


def test_create_voter(client, db, new_voter_json) -> None:

    response = client.post(f"/voters/", json=new_voter_json)

    assert response.status_code == 200, response.json()
    content = response.json()
    assert content["name"] == new_voter_json["name"]
    assert content["email"] == new_voter_json["email"]


def test_update_voter(fakerer, client, some_voter) -> None:
    new_email = fakerer.email()
    some_voter["email"] = new_email
    response = client.put(
        f"/voters/{some_voter['id']}", json=some_voter,
    )
    assert response.status_code == 200, response.json()
    content = response.json()
    assert content["email"] == some_voter["email"] == new_email
    # unchanged:
    assert content["name"] == some_voter["name"]


def test_delete_voter(client, some_voter) -> None:
    response = client.delete(
        f"/voters/{some_voter['id']}"
    )
    assert response.status_code == 200, response.json()
    content = response.json()
    assert content["name"] == some_voter["name"]
    assert content["email"] == some_voter["email"]

    response = client.get(
        f"/voters/{some_voter['id']}"
    )
    assert response.status_code == 404
