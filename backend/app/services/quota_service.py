from app.database import get_connection


def get_reps_below_quota(threshold:float= 70.0):
    with get_connection() as connection:
        with connection.cursor() as cursor: 
            cursor.execute("""SELECT id,name,email,quota,achieved,territory_id 
            FROM sales_reps 
            WHERE quota > 0
                  AND (achieved / quota * 100) < %s
                ORDER BY (achieved / quota * 100) ASC;

            """,(threshold,))
            rows = cursor.fetchall();  

            return [{
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "quota": row[3],
                "achieved": row[4],
                "territory_id": row[5],
                "attainment": round(
                        (float(row[4]) / float(row[3])) * 100,
                        2,),
                        
            } for row in rows]


