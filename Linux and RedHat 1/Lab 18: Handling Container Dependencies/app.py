import os
import psycopg2

def connect_db():
    try:
        conn = psycopg2.connect(
            host="db",
            database="postgres",
            user="postgres",
            password=os.getenv("POSTGRES_PASSWORD")
        )
        print("Successfully connected to database!")
        conn.close()
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    connect_db()
