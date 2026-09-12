from app.database import get_connection



def get_sales_reps(): 
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT id,name,email,quota,achieved,territory_id
            FROM sales_reps   ORDER BY id """)

            rows = cursor.fetchall()
            
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "quota":float( row[3]),
                    "achieved":float(row[4]),
                    "territory_id": row[5]
                } 

                for row in rows
            ]
    
        