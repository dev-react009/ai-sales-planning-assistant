from app.database import get_connection

def test_connection():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result

            print("Database connection successful!")
            print("Result:", result)



if __name__ == "__main__":
    test_connection()
