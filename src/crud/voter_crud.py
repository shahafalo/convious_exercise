from sqlalchemy.orm import Session

from models.voter import Voter
from schemas.voter import VoterCreate
from schemas.voter import Voter as Voter_Schema


def get_voters_by_ids(voter_ids: list[int], db: Session) -> list[Voter]:
    return db.query(Voter).filter(Voter.id.in_(voter_ids)).all()


def get_voters(db: Session, skip: int = 0, limit: int = 100) -> list[Voter]:
    return db.query(Voter).offset(skip).limit(limit).all()


def get_voter_by_email(email: str, db: Session):
    return db.query(Voter).filter(Voter.email == email).first()


def create_voter(voter: VoterCreate, db: Session) -> Voter:
    db_voter = Voter(**voter.dict())
    db.add(db_voter)
    db.commit()
    db.refresh(db_voter)
    return db_voter


def delete_voter(voter_id: int, db: Session):
    voter = db.get(Voter, voter_id)
    db.delete(voter)
    db.commit()
    return voter


def update_voter(voter: Voter_Schema, db: Session):
    db_voter = db.get(Voter, voter.id)
    if not db_voter:
        return None

    db_voter.name = voter.name
    db_voter.email = voter.email

    db.commit()
    return db_voter
