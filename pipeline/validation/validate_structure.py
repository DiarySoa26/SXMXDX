import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(
    PROJECT_ROOT / ".env"
)


# ============================================================
# STRUCTURE CANONIQUE
# ============================================================

REQUIRED_SHEETS = [
    "Données SOMIDA",
    "Commandes",
    "Production",
    "Calcul",
    "Besoins en micas",
    "CA",
    "Sal",
    "Achat",
    "Prestation",
    "CR Nature FD",
    "Etat_Trésorerie FD",
    "AN",
    "Emprunts FD"
]


# Cellules que nous avons déjà identifiées
# pendant le reverse-engineering.

ANCHORS = [
    {
        "sheet": "CA",
        "cell": "B32",
        "expected": "VENTE HT"
    },

    {
        "sheet": "CA",
        "cell": "B33",
        "expected": "TVA COLLECTEE"
    },
]


def get_connection():

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def add_error(
    connection,
    import_batch_id,
    sheet,
    cell,
    code,
    message,
    source_value=None
):

    with connection.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO sxmxdx.import_error
            (
                import_batch_id,
                sheet_name,
                cell_reference,
                error_code,
                message,
                valeur_source
            )
            VALUES
            (
                %s, %s, %s,
                %s, %s, %s
            )
            """,
            (
                import_batch_id,
                sheet,
                cell,
                code,
                message,
                source_value
            )
        )

    connection.commit()


def validate_sheets(
    connection,
    import_batch_id
):

    errors = 0

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT DISTINCT sheet_name
            FROM staging.import_cell
            WHERE import_batch_id = %s
            """,
            (import_batch_id,)
        )

        existing = {
            row[0]
            for row in cursor.fetchall()
        }

    for required in REQUIRED_SHEETS:

        if required not in existing:

            errors += 1

            add_error(
                connection,
                import_batch_id,
                required,
                None,
                "MISSING_SHEET",
                f"Feuille obligatoire absente : {required}"
            )

            print(
                f"ERREUR : feuille absente : "
                f"{required}"
            )

    return errors


def validate_anchors(
    connection,
    import_batch_id
):

    errors = 0

    for anchor in ANCHORS:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT raw_value
                FROM staging.import_cell
                WHERE
                    import_batch_id = %s
                    AND sheet_name = %s
                    AND cell_reference = %s
                """,
                (
                    import_batch_id,
                    anchor["sheet"],
                    anchor["cell"]
                )
            )

            result = cursor.fetchone()

        if result is None:

            errors += 1

            add_error(
                connection,
                import_batch_id,
                anchor["sheet"],
                anchor["cell"],
                "MISSING_ANCHOR",
                "Cellule de contrôle absente"
            )

            continue

        actual = (
            result[0]
            or ""
        ).strip()

        expected = (
            anchor["expected"]
        ).strip()

        if actual.upper() != expected.upper():

            errors += 1

            add_error(
                connection,
                import_batch_id,
                anchor["sheet"],
                anchor["cell"],
                "INVALID_ANCHOR",
                (
                    f"Valeur attendue : "
                    f"{expected}"
                ),
                actual
            )

    return errors


def update_batch(
    connection,
    import_batch_id,
    error_count
):

    status = (
        "VALIDATED"
        if error_count == 0
        else "INVALID"
    )

    with connection.cursor() as cursor:

        cursor.execute(
            """
            UPDATE sxmxdx.import_batch
            SET
                statut = %s,
                nombre_erreurs = %s
            WHERE import_batch_id = %s
            """,
            (
                status,
                error_count,
                import_batch_id
            )
        )

    connection.commit()


def main():

    if len(sys.argv) < 2:

        print(
            "Usage : "
            "python validate_structure.py "
            "<import_batch_id>"
        )

        sys.exit(1)

    import_batch_id = int(
        sys.argv[1]
    )

    print("=" * 72)
    print("SXMXDX - VALIDATION STRUCTURELLE")
    print("=" * 72)

    print(
        f"\nBatch : {import_batch_id}"
    )

    with get_connection() as connection:

        # Nettoyer d'anciennes validations
        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM sxmxdx.import_error
                WHERE import_batch_id = %s
                """,
                (import_batch_id,)
            )

        connection.commit()

        errors = 0

        errors += validate_sheets(
            connection,
            import_batch_id
        )

        errors += validate_anchors(
            connection,
            import_batch_id
        )

        update_batch(
            connection,
            import_batch_id,
            errors
        )

    print("\n" + "=" * 72)

    if errors == 0:

        print(
            "STRUCTURE SOMIDA VALIDÉE"
        )

    else:

        print(
            f"STRUCTURE INVALIDE : "
            f"{errors} erreur(s)"
        )

    print("=" * 72)


if __name__ == "__main__":
    main()