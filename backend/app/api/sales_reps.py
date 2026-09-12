from fastapi import APIRouter 
from app.services.sales_reps import get_sales_reps 


router = APIRouter(prefix="/api/sales-reps", tags=["sales-reps"])

@router.get("/") 
def list_sales_reps():
    return get_sales_reps()

