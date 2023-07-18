import datetime
from sqlalchemy.orm import Session
from typing import Union

from src.models.vote import Vote
from src.results_manager.manager import ResultsManager, TooManyVotesError
from src import schemas


results_manager_client = ResultsManager()


def get_votes_by_ids(vote_ids: list[int], db: Session) -> list[Vote]:
    return db.query(Vote).filter(Vote.id.in_(vote_ids)).all()


def get_votes_by_voter(voter_id: int, db: Session) -> list[Vote]:
    return db.query(Vote).filter(Vote.voter_id == voter_id).all()


def get_votes_history(start_date: datetime.date, db: Session, end_date: Union[datetime.date, None] = None,
                      voter_ids: Union[list[int], None] = None,
                      restaurant_ids: Union[list[int], None] = None) -> list[Vote]:
    query = db.query(Vote).filter(Vote.vote_time >= start_date)

    if end_date:
        query = query.filter(Vote.vote_time < end_date)
    if voter_ids:
        query = query.filter(Vote.voter_id.in_(voter_ids))
    if restaurant_ids:
        query = query.filter(Vote.restaurant_id.in_(restaurant_ids))
    return query.all()


def get_votes(db: Session, skip: int = 0, limit: int = 100) -> list[Vote]:
    return db.query(Vote).offset(skip).limit(limit).all()


def create_vote(vote: schemas.vote.VoteCreate, db: Session) -> Vote:
    db_vote = Vote(**vote.dict())
    db_vote.vote_score = _calculate_vote_score(vote, db)
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    return db_vote


def delete_vote(vote_id: int, db: Session):
    vote = db.get(Vote, vote_id)
    db.delete(vote)
    db.commit()
    _recalculate_scores(vote.voter_id, vote.restaurant_id, vote.vote_time.date(), db)
    return vote


def update_vote(vote: schemas.vote.VoteUpdate, db: Session):
    db_vote = db.get(Vote, vote.id)
    if not db_vote:
        return None

    previous_restaurant_id = db_vote.restaurant_id
    # the only accepted vote update is restaurant_id
    db_vote.restaurant_id = vote.restaurant_id
    db_vote.update_time = datetime.datetime.now()

    db.commit()

    vote_date = db_vote.vote_time.date()
    _recalculate_scores(db_vote.voter_id, db_vote.restaurant_id, vote_date, db)
    _recalculate_scores(db_vote.voter_id, previous_restaurant_id, vote_date, db)

    return db_vote


def _recalculate_scores(voter_id: int, restaurant_id: int, relevant_date: datetime.date, db: Session):
    # Used for cases when a vote is removed or updated so other votes in the same days should updated as well
    db_votes = get_votes_history(
        start_date=relevant_date, db=db, end_date=relevant_date + datetime.timedelta(days=1),
        voter_ids=[voter_id], restaurant_ids=[restaurant_id]
                                 )
    for i, vote in enumerate(db_votes):
        score = results_manager_client.calculate_vote_score(vote, db_votes[:i])

        vote.vote_score = score
    db.commit()


def _calculate_vote_score(vote: schemas.vote.VoteCreate, db) -> int:
    previous_votes = get_votes_history(
        start_date=datetime.date.today(),
        db=db,
        end_date=datetime.date.today() + datetime.timedelta(days=1),
        voter_ids=[vote.voter_id],
    )
    if len(previous_votes) >= results_manager_client.max_allowed_votes:
        raise TooManyVotesError
    score = results_manager_client.calculate_vote_score(vote, previous_votes)
    return score
