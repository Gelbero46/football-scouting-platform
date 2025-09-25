from fastapi import APIRouter

from app.api.v1.endpoints import auth, players, coaches, shortlists, reports

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(players.router, prefix="/players", tags=["players"])
api_router.include_router(coaches.router, prefix="/coaches", tags=["coaches"])
api_router.include_router(shortlists.router, prefix="/shortlists", tags=["shortlists"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])