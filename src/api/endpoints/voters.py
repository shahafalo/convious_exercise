from sqlalchemy.orm import Session

from fastapi import APIRouter, HTTPException, Depends

from schemas.voter import Voter, VoterCreate
from crud import voter_crud
from db.utils import get_db

router = APIRouter()


@router.get("/", response_model=list[Voter])
async def read_voters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return voter_crud.get_voters(db, skip, limit)


@router.get("/{voter_id}", response_model=Voter)
async def read_voter(voter_id: int, db: Session = Depends(get_db)):
    db_voter = voter_crud.get_voters_by_ids([voter_id], db)
    if not db_voter:
        raise HTTPException(status_code=404, detail="Voter not found")
    return Voter.from_orm(db_voter[0])


@router.post("/", response_model=Voter)
async def create_voter(voter_in: VoterCreate, db: Session = Depends(get_db)):
    if not voter_in.name:
        raise HTTPException(status_code=400, detail="Voter name can't be empty")
    other_db_voter = voter_crud.get_voter_by_email(voter_in.email, db)
    if other_db_voter:
        raise HTTPException(status_code=409, detail=f"Voter email already used. Voter id: {other_db_voter.id}")
    db_voter = voter_crud.create_voter(voter_in, db)
    return Voter.from_orm(db_voter)


@router.put("/{voter_id}", response_model=Voter)
async def update_voter(voter_id: int, voter_in: Voter, db: Session = Depends(get_db)):
    if not voter_crud.get_voters_by_ids([voter_id], db):
        raise HTTPException(status_code=404, detail="Voter not found")
    db_voter = voter_crud.update_voter(voter_in, db)
    return Voter.from_orm(db_voter)


@router.delete("/{voter_id}", response_model=Voter)
async def delete_voter(voter_id: int, db: Session = Depends(get_db)):
    if not voter_crud.get_voters_by_ids([voter_id], db):
        raise HTTPException(status_code=404, detail="Voter not found")
    db_voter = voter_crud.delete_voter(voter_id, db)
    return Voter.from_orm(db_voter)
