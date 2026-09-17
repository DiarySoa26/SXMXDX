import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CELLS_FILE = (
    PROJECT_ROOT
    / "reverse_engineering"
    / "output"
    / "cells.csv"
)


IMPORTANT_SHEETS = {
    "Données SOMIDA",
    "Commandes",
    "Production",
    "Besoins en micas",
    "CA"
}


def main():

    if not CELLS_FILE.exists():
        raise FileNotFoundError(
            "Exécute d'abord excel_inspector.py"
        )

    with CELLS_FILE.open(
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if row["sheet"] not in IMPORTANT_SHEETS:
                continue

            if row["type"] == "FORMULA":
                continue

            print(
                f"{row['sheet']:<25} "
                f"{row['cell']:<8} "
                f"{row['type']:<10} "
                f"{row['value']}"
            )


if __name__ == "__main__":
    main()