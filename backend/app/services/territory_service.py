from app.database import get_connection


def get_accounts_by_territory(territory_name: str):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    a.id,
                    a.name,
                    a.industry,
                    a.segment,
                    a.annual_revenue,
                    t.name AS territory,
                    sr.name AS assigned_rep
                FROM accounts a
                JOIN territories t
                    ON a.territory_id = t.id
                LEFT JOIN sales_reps sr
                    ON a.assigned_rep_id = sr.id
                WHERE LOWER(t.name) = LOWER(%s)
                ORDER BY a.name;
                """,
                (territory_name,),
            )

            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "industry": row[2],
                    "segment": row[3],
                    "annual_revenue": (
                        float(row[4]) if row[4] is not None else None
                    ),
                    "territory": row[5],
                    "assigned_rep": row[6],
                }
                for row in rows
            ]