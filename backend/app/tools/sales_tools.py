from app.services.account_service import get_unassigned_accounts as fetch_unassigned_accounts

from app.services.quota_service import get_reps_below_quota as fetch_reps_below_quota
    
from app.services.territory_service import get_accounts_by_territory as fetch_accounts_by_territory


def get_quota_attainment(threshold: float = 70.0):
    reps = fetch_reps_below_quota(threshold)

    return [
        {
            "name": rep["name"],
            "quota": rep["quota"],
            "achieved": rep["achieved"],
            "attainment": rep["attainment"],
        }
        for rep in reps
    ]


def get_unassigned_accounts():
    accounts  =fetch_unassigned_accounts("Enterprise")
    return [
        {
            "id": account["id"],
            "territory_id": account["territory_id"],
            "name": account["name"],
            "industry": account["industry"],
            "segment": account["segment"],
             "primary_location": account["primary_location"],
            "annual_revenue": account["annual_revenue"],
            "assignment_status": "UNASSIGNED_TO_SALES_REP",
        }
        for account in accounts
    ]


def get_accounts_by_territory(territory_name: str):
    return fetch_accounts_by_territory(territory_name)