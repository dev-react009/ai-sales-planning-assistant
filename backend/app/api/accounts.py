from fastapi import APIRouter,Query

from app.services.account_service import get_unassigned_accounts


router = APIRouter(
    prefix="/api/accounts",
    tags=["Accounts"],
)


@router.get("/unassigned")
def unassigned_accounts(
    segment: str | None = Query(default=None)
):
    return get_unassigned_accounts(segment)