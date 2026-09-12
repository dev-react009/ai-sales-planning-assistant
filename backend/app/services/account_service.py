from app.database import get_connection


def get_unassigned_accounts(segment: str | None = None):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            if segment:
                cursor.execute(
                    """
                    SELECT
                        id,
                        territory_id,
                        name,
                        industry,
                        segment,
                        primary_location,
                        annual_revenue
                    FROM accounts
                    WHERE assigned_rep_id IS NULL
                      AND segment = %s
                    ORDER BY name;
                    """,
                    (segment,),
                )
            else:
                cursor.execute(
                    """
                    SELECT
                        id,
                        territory_id,
                        name,
                        industry,
                        segment,
                        primary_location,
                        annual_revenue
                    FROM accounts
                    WHERE assigned_rep_id IS NULL
                    ORDER BY name;
                    """
                )

            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "territory_id": row[1],
                    "name": row[2],
                    "industry": row[3],
                    "segment": row[4],
                    "primary_location": row[5] if row[5] is not None else None,
                    "annual_revenue": (
                        float(row[6]) if row[6] is not None else None
                    ),
                }
                for row in rows
            ]