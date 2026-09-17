import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


MIGRATIONS = [
    PROJECT_ROOT / "database/migrations/001_core.sql",
    PROJECT_ROOT / "database/migrations/002_business.sql",
    PROJECT_ROOT / "database/migrations/003_staging.sql",
]

SEEDS = [
    PROJECT_ROOT / "database/seed/001_reference.sql"
]


def get_connection():

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def execute_sql_file(connection, path):

    print(f"Exécution : {path.name}")

    sql = path.read_text(
        encoding="utf-8"
    )

    with connection.cursor() as cursor:
        cursor.execute(sql)

    connection.commit()


def main():

    print("=" * 70)
    print("SXMXDX - INITIALISATION POSTGRESQL")
    print("=" * 70)

    with get_connection() as connection:

        for migration in MIGRATIONS:

            if not migration.exists():
                raise FileNotFoundError(
                    migration
                )

            execute_sql_file(
                connection,
                migration
            )

        for seed in SEEDS:

            execute_sql_file(
                connection,
                seed
            )

    print("\nBase SXMXDX initialisée.")


if __name__ == "__main__":
    main()