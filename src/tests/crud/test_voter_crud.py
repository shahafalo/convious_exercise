from crud import voter_crud
from schemas.voter import VoterCreate, Voter


def test_get_voter(db, db_voter):
    results = voter_crud.get_voters_by_ids([db_voter.id], db)
    assert results
    res = results[0]
    assert res
    assert res.id == db_voter.id
    assert res.email == db_voter.email
    assert res.name == db_voter.name


def test_get_voters(db, db_voter):
    res = voter_crud.get_voters(db)
    assert len(res) == 1
    assert res[0].id == db_voter.id


def test_get_voter_by_email(db, db_voter):
    res = voter_crud.get_voter_by_email(db_voter.email, db)
    assert res
    assert res.id == db_voter.id


def test_create_voter(db, new_voter_json):
    res = voter_crud.create_voter(VoterCreate(**new_voter_json), db)
    assert res.id
    assert res.email == new_voter_json["email"]
    assert res.name == new_voter_json["name"]


def test_update_voter(db, db_voter):
    changed_name = "temp_changed"
    assert db_voter.name != changed_name

    voter_json = Voter.from_orm(db_voter)
    voter_json.name = changed_name
    voter_crud.update_voter(voter_json, db)

    res = voter_crud.get_voters_by_ids([db_voter.id], db)[0]
    assert res.name == changed_name


def test_delete_voter(db, db_voter):
    voter_crud.delete_voter(db_voter.id, db)
    res = voter_crud.get_voters_by_ids([db_voter.id], db)
    assert not res
