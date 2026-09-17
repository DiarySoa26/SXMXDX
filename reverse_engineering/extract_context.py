import csv
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reverse_engineering"
    / "output"
)

CELLS_FILE = OUTPUT_DIR / "cells.csv"
CANDIDATES_FILE = OUTPUT_DIR / "input_candidates.csv"

RESULT_FILE = (
    OUTPUT_DIR
    / "input_candidates_with_context.csv"
)


# Nombre de cellules autour du candidat
RADIUS_ROW = 2
RADIUS_COLUMN = 2


def load_cells():

    cells = {}

    with CELLS_FILE.open(
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            key = (
                row["sheet"],
                int(row["row"]),
                int(row["column"])
            )

            cells[key] = row

    return cells


def get_context(
    cells,
    sheet,
    row,
    column
):

    context = []

    for r in range(
        max(1, row - RADIUS_ROW),
        row + RADIUS_ROW + 1
    ):

        for c in range(
            max(1, column - RADIUS_COLUMN),
            column + RADIUS_COLUMN + 1
        ):

            # ne pas remettre la cellule elle-même
            if r == row and c == column:
                continue

            key = (
                sheet,
                r,
                c
            )

            neighbor = cells.get(key)

            if not neighbor:
                continue

            value = neighbor["value"]

            if not value:
                continue

            context.append(
                f"{neighbor['cell']}={value}"
            )

    return " | ".join(context)


def main():

    print("=" * 70)
    print("SXMXDX - EXTRACTION DU CONTEXTE METIER")
    print("=" * 70)

    if not CELLS_FILE.exists():
        raise FileNotFoundError(
            "cells.csv absent"
        )

    if not CANDIDATES_FILE.exists():
        raise FileNotFoundError(
            "input_candidates.csv absent. "
            "Exécute classify_inputs.py."
        )

    print("\nChargement des cellules...")

    cells = load_cells()

    print(
        f"{len(cells)} cellules chargées."
    )

    results = []

    with CANDIDATES_FILE.open(
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for candidate in reader:

            row_number = int(
                candidate["row"]
            )

            column_number = int(
                candidate["column"]
            )

            context = get_context(
                cells,
                candidate["sheet"],
                row_number,
                column_number
            )

            result = dict(candidate)

            result[
                "context"
            ] = context

            results.append(result)

    fields = list(
        results[0].keys()
    ) if results else []

    with RESULT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()
        writer.writerows(results)

    print(
        f"\n{len(results)} candidats enrichis."
    )

    print(
        f"Fichier : {RESULT_FILE}"
    )

    print("\nExemples :\n")

    for result in results[:20]:

        print("-" * 70)

        print(
            f"{result['sheet']}!"
            f"{result['cell']}"
        )

        print(
            f"Valeur : "
            f"{result['value']}"
        )

        print(
            f"Utilisations : "
            f"{result['used_by_formulas']}"
        )

        print(
            f"Contexte : "
            f"{result['context']}"
        )


if __name__ == "__main__":
    main()