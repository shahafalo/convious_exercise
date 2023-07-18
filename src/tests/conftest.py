import collections
import datetime

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import random

from main import app
from src.db.utils import get_db
from src.db.base import Base
from src.models.restaurant import Restaurant
from src.models.vote import Vote
from src.models.voter import Voter
from src.results_manager.manager import ResultsManager

# todo: add typehints


SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


app.dependency_overrides[get_db] = override_get_db


def _create_multiple_votes(db, multiple_voters, multiple_restaurants, should_add_old_vote_time=False):
    votes = []
    created_at_least_one_vote = False
    voter_to_rest_index = collections.defaultdict(int)
    for voter in multiple_voters:
        for restaurant in multiple_restaurants:
            if random.random() > 0.5 or not created_at_least_one_vote:
                # just adding some random to diversify the data
                vote_time = datetime.date.today()
                if should_add_old_vote_time and random.random() > 0.5:
                    vote_time = datetime.date.today() - datetime.timedelta(days=1)
                key = f"{restaurant.id}_{voter.id}"
                vote_index = voter_to_rest_index[key]
                voter_to_rest_index[key] += 1
                vote_score = ResultsManager().get_vote_score(vote_index)
                temp_vote = Vote(
                    voter_id=voter.id, restaurant_id=restaurant.id, vote_time=vote_time, vote_score=vote_score
                )
                votes.append(temp_vote)
                db.add(temp_vote)
                created_at_least_one_vote = True
        db.commit()
    return votes


@pytest.fixture(scope="function")
def fakerer(faker):
    # original faker has an issue with his seed, this is making all of his starting results the same, so another seed
    # is needed but besides that it's good enough to use it
    faker.seed_instance(random.random())
    yield faker


@pytest.fixture
def results_manager():
    yield ResultsManager()


@pytest.fixture(scope="function")
def client():
    yield TestClient(app)


@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    yield db_session
    db_session.rollback()
    db_session.close()


# todo: rename json fixture to relevant name

@pytest.fixture(scope="function")
def new_restaurant_json(fakerer) -> dict:
    return {
        "name": fakerer.name(), "address": fakerer.address(), "phone": fakerer.phone_number(),
        "website": fakerer.url(), "notes": fakerer.text()
            }


@pytest.fixture(scope="function")
def some_restaurant(client, new_restaurant_json):
    new_restaurant_json_with_id = client.post(f"/restaurants/", json=new_restaurant_json).json()
    return new_restaurant_json_with_id


@pytest.fixture(scope="function")
def multiple_restaurants(fakerer, db):
    restaurants = []
    for _ in range(fakerer.random_digit_not_null()):
        temp_restaurant = Restaurant(
            name=fakerer.name(), address=fakerer.address(), phone=fakerer.phone_number(),
            website=fakerer.url(), notes=fakerer.text()
        )
        restaurants.append(temp_restaurant)
        db.add(temp_restaurant)
    db.commit()
    return restaurants


@pytest.fixture(scope="function")
def db_restaurant(db, new_restaurant_json) -> Restaurant:
    restaurant = Restaurant(**new_restaurant_json)
    db.add(restaurant)
    db.commit()
    return restaurant


@pytest.fixture(scope="function")
def new_vote_json(db_restaurant, db_voter, index=0) -> dict:
    vote_score = ResultsManager().get_vote_score(index)
    return {"voter_id": db_voter.id, "restaurant_id": db_restaurant.id, "vote_score": vote_score}


@pytest.fixture(scope="function")
def some_vote(client, new_vote_json) -> dict:
    vote = client.post(f"/votes/", json=new_vote_json)
    return vote.json()


@pytest.fixture(scope="function")
def multiple_votes_by_voter_ids(db, multiple_voters, multiple_restaurants) -> dict[int, list[Vote]]:
    votes = _create_multiple_votes(db, multiple_voters, multiple_restaurants)
    votes_by_voter_id = collections.defaultdict(list)
    for vote in votes:
        votes_by_voter_id[vote.voter_id].append(vote)
    return votes_by_voter_id


@pytest.fixture(scope="function")
def multiple_votes(db, multiple_voters, multiple_restaurants) -> list[Vote]:
    return _create_multiple_votes(db, multiple_voters, multiple_restaurants)


@pytest.fixture(scope="function")
def multiple_votes_with_various_vote_times(db, multiple_voters, multiple_restaurants) -> list[Vote]:
    return _create_multiple_votes(db, multiple_voters, multiple_restaurants, should_add_old_vote_time=True)


@pytest.fixture(scope="function")
def db_vote(db, new_vote_json) -> Vote:
    vote = Vote(**new_vote_json)
    db.add(vote)
    db.commit()
    return vote


@pytest.fixture(scope="function")
def multiple_db_votes_with_the_same_voter_and_rest(db, new_vote_json) -> Vote:
    votes = []
    for i in range(7):  # arbitrary amount
        vote = Vote(**new_vote_json)
        vote_score = ResultsManager().get_vote_score(i)
        vote.vote_score = vote_score
        db.add(vote)
        votes.append(vote)
    db.commit()
    return votes


@pytest.fixture(scope="function")
def new_voter_json(fakerer) -> dict:
    return {"email": fakerer.email(), "name": fakerer.name()}


@pytest.fixture(scope="function")
def some_voter(client, new_voter_json) -> dict:
    voter = client.post(f"/voters/", json=new_voter_json)
    return voter.json()


@pytest.fixture(scope="function")
def db_voter(db, new_voter_json) -> Voter:
    voter = Voter(**new_voter_json)
    db.add(voter)
    db.commit()
    return voter


@pytest.fixture(scope="function")
def multiple_voters(fakerer, db):
    voters = []
    for _ in range(fakerer.random_digit_not_null()):
        temp_voter = Voter(
            name=fakerer.name(), email=fakerer.email()
        )
        voters.append(temp_voter)
        db.add(temp_voter)
    db.commit()
    return voters
