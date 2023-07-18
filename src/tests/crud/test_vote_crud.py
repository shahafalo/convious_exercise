import datetime

import pytest

from src.crud import vote_crud
from src.schemas.vote import VoteCreate, VoteUpdate


def test_get_vote(db, db_vote):
    results = vote_crud.get_votes_by_ids([db_vote.id], db)
    assert results
    res = results[0]
    assert res.voter_id == db_vote.voter_id
    assert res.vote_time == db_vote.vote_time
    assert res.restaurant_id == db_vote.restaurant_id


def test_get_votes_by_voter(db, db_vote):
    res = vote_crud.get_votes_by_voter(db_vote.voter_id, db)
    assert len(res) == 1
    assert res[0].id == db_vote.id


def test_get_votes(db, db_vote):
    res = vote_crud.get_votes(db)
    assert len(res) == 1
    assert res[0].id == db_vote.id


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
def test_get_votes_history(db, multiple_votes_with_various_vote_times, should_filter_end_date,
                           should_filter_voter_ids, should_filter_restaurants_ids):
    expected_votes = [v for v in multiple_votes_with_various_vote_times]
    start_date = datetime.date.today() - datetime.timedelta(days=1)

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

    res = vote_crud.get_votes_history(start_date=start_date, end_date=end_date,
                                      voter_ids=voter_ids, restaurant_ids=restaurants_ids, db=db)
    assert len(res) == len(expected_votes)
    expected_vote_ids = {v.id for v in expected_votes}
    res_vote_ids = {v.id for v in res}
    assert expected_vote_ids == res_vote_ids


def test_create_vote(db, new_vote_json):
    res = vote_crud.create_vote(VoteCreate(**new_vote_json), db)
    assert res.id
    assert res.voter_id == new_vote_json["voter_id"]
    assert res.restaurant_id == new_vote_json["restaurant_id"]
    assert res.vote_score == 1

    res = vote_crud.create_vote(VoteCreate(**new_vote_json), db)
    assert res.vote_score == 0.5

    res = vote_crud.create_vote(VoteCreate(**new_vote_json), db)
    assert res.vote_score == 0.25


def test_update_vote(db, multiple_db_votes_with_the_same_voter_and_rest):
    vote_to_update = multiple_db_votes_with_the_same_voter_and_rest[1]
    first_vote = multiple_db_votes_with_the_same_voter_and_rest[0]
    third_vote = multiple_db_votes_with_the_same_voter_and_rest[2]
    forth_vote = multiple_db_votes_with_the_same_voter_and_rest[3]
    assert first_vote.vote_score == 1
    assert vote_to_update.vote_score == 0.5
    assert third_vote.vote_score == 0.25
    assert forth_vote.vote_score == 0.25
    changed_restaurant_id = vote_to_update.restaurant_id + 1
    vote_json = VoteUpdate.from_orm(vote_to_update)
    vote_json.restaurant_id = changed_restaurant_id
    vote_crud.update_vote(vote_json, db)
    res = vote_crud.get_votes_by_ids([vote_to_update.id], db)[0]
    assert res.restaurant_id == changed_restaurant_id
    assert res.vote_score == 1
    assert first_vote.vote_score == 1
    assert third_vote.vote_score == 0.5
    assert forth_vote.vote_score == 0.25


def test_delete_vote(db, multiple_db_votes_with_the_same_voter_and_rest):
    vote_to_delete = multiple_db_votes_with_the_same_voter_and_rest[1]
    first_vote = multiple_db_votes_with_the_same_voter_and_rest[0]
    third_vote = multiple_db_votes_with_the_same_voter_and_rest[2]
    assert vote_crud.get_votes_by_ids([vote_to_delete.id], db)
    assert first_vote.vote_score == 1
    assert third_vote.vote_score == 0.25

    vote_crud.delete_vote(vote_to_delete.id, db)

    assert not vote_crud.get_votes_by_ids([vote_to_delete.id], db)
    assert first_vote.vote_score == 1
    assert third_vote.vote_score == 0.5
