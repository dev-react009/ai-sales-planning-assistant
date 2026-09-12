from app.tools.sales_tools import (
    get_quota_attainment,
    get_unassigned_accounts,
    get_accounts_by_territory,
)


if __name__ == "__main__":
    print("\n--- Reps below 70% quota ---")

    reps = get_quota_attainment(70)

    for rep in reps:
        print(
            f"{rep['name']} - "
            f"{rep['attainment']}%"
        )

    print("\n--- Unassigned Enterprise accounts ---")

    accounts = get_unassigned_accounts()

    for account in accounts:
        print(
            f"{account['name']} - "
            f"{account['industry']}"
        )

    print("\n--- Hyderabad accounts ---")

    territory_accounts = get_accounts_by_territory("Hyderabad")

    for account in territory_accounts:
        print(
            f"{account['name']} - "
            f"{account['segment']} - "
            f"Rep: {account['assigned_rep']}"
        )