from fastapi import APIRouter, Query

from app.services.quota_service import get_reps_below_quota 

router = APIRouter(prefix="/api/quota", tags=["quota"]) 

@router.get("/below")

def reps_below_quota(
    threshold:float = Query(default=70.0,gt=0,le=100) 
):
    return get_reps_below_quota(threshold)
