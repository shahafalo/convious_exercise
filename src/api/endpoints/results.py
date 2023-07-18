import datetime
from typing import Union

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from src.schemas.result import Result, Winner
from src.crud import vote_crud
from src.db.utils import get_db
from src.results_manager.manager import ResultsManager

router = APIRouter()
manager = ResultsManager()


@router.get("/", response_model=list[Result])
async def get_results(date: Union[datetime.date, None] = None, db: Session = Depends(get_db)):
    if not date:
        date = datetime.date.today()
    votes = vote_crud.get_votes_history(start_date=date, end_date=date + datetime.timedelta(days=1), db=db)
    results = manager.calculate_results(votes)
    return [Result(restaurant_id=res[0], score=res[1]) for res in results.items()]


@router.get("/history/{start_date}", response_model=list[Result])
async def get_results_history(start_date: str, end_date: Union[str, None] = None,
                              voter_ids: Union[str, None] = None, restaurant_ids: Union[str, None] = None,
                              db: Session = Depends(get_db)):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    voter_ids = voter_ids.replace("[", "").replace("]", "").split(",") if voter_ids else None
    restaurant_ids = restaurant_ids.replace("[", "").replace("]", "").split(",") if restaurant_ids else None
    votes = vote_crud.get_votes_history(start_date=start_date, end_date=end_date,
                                        voter_ids=voter_ids,
                                        restaurant_ids=restaurant_ids,
                                        db=db)
    results = manager.calculate_results(votes)
    return [Result(restaurant_id=res[0], score=res[1]) for res in results.items()]


@router.get("/winner/", response_model=Winner)
async def get_winner(date: Union[datetime.date, None] = None, db: Session = Depends(get_db)):
    if not date:
        date = datetime.date.today()
    votes = vote_crud.get_votes_history(start_date=date, end_date=date + datetime.timedelta(days=1), db=db)
    winner = manager.get_winner(votes)
    return Winner(restaurant_id=winner[0])
