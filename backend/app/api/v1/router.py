from fastapi import APIRouter

from app.api.v1 import auth, hosted_zones, meta, records

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(hosted_zones.router)
api_router.include_router(records.router)
api_router.include_router(meta.router)
