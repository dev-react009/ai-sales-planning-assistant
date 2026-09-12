from app.services.quota_service import get_reps_below_quota


if __name__ == "__main__":
    reps = get_reps_below_quota(70)

    print("Sales reps below 70% quota:")
    for rep in reps:
        print(
            f"{rep['name']} - "
            f"{rep['attainment']}%"
        )





