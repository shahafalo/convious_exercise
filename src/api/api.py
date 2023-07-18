from fastapi import APIRouter

from src.api.endpoints import restaurants
from src.api.endpoints import results
from src.api.endpoints import votes
from src.api.endpoints import voters


api_router = APIRouter()
api_router.include_router(restaurants.router, prefix="/restaurants", tags=["restaurants"])
api_router.include_router(results.router, prefix="/results", tags=["results"])
api_router.include_router(votes.router, prefix="/votes", tags=["votes"])
api_router.include_router(voters.router, prefix="/voters", tags=["voters"])
