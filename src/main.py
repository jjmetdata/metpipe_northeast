from pathlib import Path
import os
import subprocess
import sys
import psycopg2


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "sql"


def run_sql_file(cursor, file_path):
    with open(file_path, "r") as file:
        sql = file.read()

    cursor.execute(sql)


def main():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "northeast_weather_2024_phase2"),
        user=os.getenv("DB_USER") or os.getenv("USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    conn.autocommit = True
    cursor = conn.cursor()

    print("Connected to the database.")
    print("Starting the pipeline...")
    print(" ")

    try:
        # Step 1: Create the database tables and views
        print("Running schema.sql...")

        run_sql_file(
            cursor,
            SQL_DIR / "schema.sql"
        )

        print("schema.sql executed successfully.")
        print(" ")

        # Step 2: Run the Python ingestion script
        print("Running ingest.py...")

        subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "src" / "ingest.py")
            ],
            check=True
        )

        print("ingest.py executed successfully.")
        print(" ")

    except Exception as error:
        print(f"Error running the pipeline: {error}")
        raise

    finally:
        cursor.close()
        conn.close()

        print("Database connection closed.")

    print("Database setup and data ingestion complete.")


if __name__ == "__main__":
    main()
