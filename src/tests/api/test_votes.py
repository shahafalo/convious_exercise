import datetime
import pytest


def test_read_vote(client, some_vote) -> None:
    response = client.get(
        f"/votes/vote/{some_vote['voter_id']}/"
    )
    assert response.status_code == 200
    vote = response.json()
    assert vote
    assert vote["voter_id"] == some_vote["voter_id"]
    assert vote["restaurant_id"] == some_vote["restaurant_id"]


def test_read_votes_by_voter(client, multiple_votes_by_voter_ids) -> None:
    for voter_id in multiple_votes_by_voter_ids:
        response = client.get(f"/votes/voter/{voter_id}")
        assert response.status_code == 200
        votes = response.json()
        assert len(votes) == len(multiple_votes_by_voter_ids[voter_id])
        for vote in votes:
            db_vote = [d for d in multiple_votes_by_voter_ids[voter_id] if d.id == vote["id"]][0]
            assert db_vote.voter_id == vote["voter_id"]
            assert db_vote.restaurant_id == vote["restaurant_id"]


def test_read_votes(client, multiple_votes) -> None:
    response = client.get(f"/votes")
    assert response.status_code == 200
    new_votes = response.json()
    assert len(new_votes) == len(multiple_votes)

    for vote in new_votes:
        db_vote = [d for d in multiple_votes if d.id == vote["id"]][0]
        assert vote["voter_id"] == db_vote.voter_id
        assert vote["restaurant_id"] == db_vote.restaurant_id


@pytest.mark.parametrize("should_filter_end_date,should_filter_voter_ids,should_filter_restaurants_ids",
                         [
                             (False, False, False),
                             (True, False, False),
                             (False, True, False),
                             (False, False, True),
                             (True, True, False),
                             (False, True, True),
                             (True, False, True),
                             (True, True, True),
                          ]
                         )
def test_get_votes_history(client, multiple_votes_with_various_vote_times, should_filter_end_date,
                           should_filter_voter_ids, should_filter_restaurants_ids):
    start_date = datetime.date.today() - datetime.timedelta(days=1)
    expected_votes = [v for v in multiple_votes_with_various_vote_times if v.vote_time.date() >= start_date]

    end_date = None
    if should_filter_end_date:
        end_date = datetime.date.today()
        expected_votes = [v for v in expected_votes if v.vote_time.date() < end_date]

    voter_ids = None
    if should_filter_voter_ids:
        voter_ids = list({multiple_votes_with_various_vote_times[-1].voter_id,
                          multiple_votes_with_various_vote_times[0].voter_id})  # arbitrary voter ids
        expected_votes = [v for v in expected_votes if v.voter_id in voter_ids]

    restaurants_ids = None
    if should_filter_restaurants_ids:
        restaurants_ids = list({multiple_votes_with_various_vote_times[-1].restaurant_id,
                                multiple_votes_with_various_vote_times[0].restaurant_id})  # arbitrary restaurants ids
        expected_votes = [v for v in expected_votes if v.restaurant_id in restaurants_ids]

    vote_search_request = {"end_date": str(end_date) if end_date else None,
                           "voter_ids": str(voter_ids) if voter_ids else None,
                           "restaurant_ids": str(restaurants_ids) if restaurants_ids else None}
    response = client.get(f"/votes/history/{str(start_date)}", params=vote_search_request)
    assert response.status_code == 200
    res = response.json()
    assert len(res) == len(expected_votes)
    expected_vote_ids = {v.id for v in expected_votes}
    res_vote_ids = {v["id"] for v in res}
    assert expected_vote_ids == res_vote_ids


def test_create_vote(client, new_vote_json) -> None:

    response = client.post(f"/votes/", json=new_vote_json)

    assert response.status_code == 200, response.json()
    content = response.json()
    assert content["voter_id"] == new_vote_json["voter_id"]
    assert content["restaurant_id"] == new_vote_json["restaurant_id"]


def test_create_protest_vote(client, db_voter) -> None:
    protest_vote = {"voter_id": db_voter.id, "restaurant_id": None}
    response = client.post(f"/votes/", json=protest_vote)

    assert response.status_code == 200, response.json()
    content = response.json()
    assert content["voter_id"] == protest_vote["voter_id"]
    assert content["restaurant_id"] is None


def test_update_vote(client, some_vote, multiple_restaurants) -> None:
    another_restaurant = [res for res in multiple_restaurants if res.id != some_vote["id"]][0]
    assert some_vote["restaurant_id"] != another_restaurant.id
    some_vote["restaurant_id"] = another_restaurant.id
    response = client.put(
        f"/votes/{some_vote['id']}", json=some_vote,
    )
    assert response.status_code == 200, response.json()
    content = response.json()
    assert content["restaurant_id"] == some_vote["restaurant_id"] == another_restaurant.id
    # unchanged:
    assert content["voter_id"] == some_vote["voter_id"]


def test_delete_vote(client, some_vote) -> None:
    response = client.delete(
        f"/votes/{some_vote['id']}"
    )
    assert response.status_code == 200, response.json()
    content = response.json()
    assert content["voter_id"] == some_vote["voter_id"]
    assert content["restaurant_id"] == some_vote["restaurant_id"]

    response = client.get(
        f"/votes/vote/{some_vote['voter_id']}"
    )
    assert response.status_code == 404
