import datetime
from typing import Union

from sqlalchemy.orm import Session

from fastapi import APIRouter, HTTPException, Depends

from src.schemas.vote import Vote, VoteCreate, VoteUpdate
from src.crud import vote_crud, voter_crud, restaurant_crud
from src.db.utils import get_db
from src.results_manager.manager import TooManyVotesError

router = APIRouter()


@router.get("/", response_model=list[Vote])
async def read_votes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    votes = vote_crud.get_votes(db, skip, limit)
    return votes


@router.get("/voter/{voter_id}", response_model=list[Vote])
async def read_all_voter_votes(voter_id: int, db: Session = Depends(get_db)):
    if not voter_crud.get_voters_by_ids([voter_id], db):
        raise HTTPException(status_code=404, detail="Voter not found")
    return vote_crud.get_votes_by_voter(voter_id, db)


@router.get("/history/{start_date}", response_model=list[Vote])
async def read_votes_history(start_date: str, end_date: Union[str, None] = None,
                             voter_ids: Union[str, None] = None, restaurant_ids: Union[str, None] = None,
                             db: Session = Depends(get_db)):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    voter_ids = voter_ids.replace("[", "").replace("]", "").split(",") if voter_ids else None
    restaurant_ids = restaurant_ids.replace("[", "").replace("]", "").split(",") if restaurant_ids else None
    return vote_crud.get_votes_history(start_date=start_date,
                                       end_date=end_date,
                                       voter_ids=voter_ids,
                                       restaurant_ids=restaurant_ids,
                                       db=db)


@router.get("/vote/{vote_id}", response_model=Vote)
async def read_vote(vote_id: int, db: Session = Depends(get_db)):
    vote = vote_crud.get_votes_by_ids([vote_id], db)
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")
    return vote[0]


@router.post("/", response_model=Vote)
async def create_vote(vote_in: VoteCreate, db: Session = Depends(get_db)):
    if not vote_in.voter_id or not voter_crud.get_voters_by_ids([vote_in.voter_id], db):
        raise HTTPException(status_code=400, detail="Illegal voter id")
    if vote_in.restaurant_id and not restaurant_crud.get_restaurants_by_ids([vote_in.restaurant_id], db):
        # A protest vote is acceptable, therefore vote without restaurant id is valid
        raise HTTPException(status_code=400, detail="Illegal restaurant id")
    try:
        vote = vote_crud.create_vote(vote_in, db)
    except TooManyVotesError:
        raise HTTPException(status_code=400, detail=f"Passed max allowed votes per day")
    return vote


@router.put("/{vote_id}", response_model=Vote)
async def update_vote(vote_id: int, vote_update_in: VoteUpdate, db: Session = Depends(get_db)):
    db_votes = vote_crud.get_votes_by_ids([vote_id], db)
    if not db_votes:
        raise HTTPException(status_code=404, detail="Vote not found")
    db_vote = db_votes[0]
    if vote_update_in.voter_id != db_vote.voter_id:
        raise HTTPException(status_code=400, detail="Can't change voter id")
    # todo: validate not changing vote id
    return vote_crud.update_vote(vote_update_in, db)


@router.delete("/{vote_id}", response_model=Vote)
async def delete_vote(vote_id: int, db: Session = Depends(get_db)):
    if not vote_crud.get_votes_by_ids([vote_id], db):
        raise HTTPException(status_code=404, detail="Vote not found")
    return vote_crud.delete_vote(vote_id, db)
