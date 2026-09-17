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

OUTPUT_FILE = (
    OUTPUT_DIR
    / "detected_table_regions.csv"
)


MIN_COLUMNS = 3
MIN_CONSECUTIVE_ROWS = 2


def load_cells():

    sheets = defaultdict(
        lambda: defaultdict(dict)
    )

    with CELLS_FILE.open(
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for item in reader:

            sheet = item["sheet"]

            row = int(item["row"])
            column = int(item["column"])

            sheets[sheet][row][column] = item

    return sheets


def contiguous_groups(numbers):

    if not numbers:
        return []

    numbers = sorted(numbers)

    groups = []

    current = [numbers[0]]

    for number in numbers[1:]:

        if number == current[-1] + 1:
            current.append(number)

        else:
            groups.append(current)
            current = [number]

    groups.append(current)

    return groups


def detect_regions(sheet_name, rows):

    candidates = []

    active_rows = []

    # --------------------------------------------------------
    # Une ligne est considérée tabulaire lorsqu'elle possède
    # au moins MIN_COLUMNS cellules non vides.
    # --------------------------------------------------------

    for row_number, columns in rows.items():

        if len(columns) >= MIN_COLUMNS:
            active_rows.append(row_number)

    row_groups = contiguous_groups(
        active_rows
    )

    region_number = 1

    for group in row_groups:

        if len(group) < MIN_CONSECUTIVE_ROWS:
            continue

        all_columns = []

        formula_count = 0
        constant_count = 0
        text_count = 0
        numeric_count = 0

        for row_number in group:

            for column_number, cell in (
                rows[row_number].items()
            ):

                all_columns.append(
                    column_number
                )

                cell_type = cell["type"]

                if cell_type == "FORMULA":
                    formula_count += 1

                else:
                    constant_count += 1

                if cell_type == "TEXT":
                    text_count += 1

                if cell_type == "NUMBER":
                    numeric_count += 1

        if not all_columns:
            continue

        min_column = min(all_columns)
        max_column = max(all_columns)

        candidates.append({

            "sheet":
                sheet_name,

            "region_id":
                f"{sheet_name}_R{region_number}",

            "start_row":
                min(group),

            "end_row":
                max(group),

            "start_column":
                min_column,

            "end_column":
                max_column,

            "row_count":
                len(group),

            "column_span":
                max_column - min_column + 1,

            "formula_count":
                formula_count,

            "constant_count":
                constant_count,

            "text_count":
                text_count,

            "numeric_count":
                numeric_count
        })

        region_number += 1

    return candidates


def main():

    print("=" * 72)
    print("SXMXDX - DETECTION DES TABLEAUX EXCEL")
    print("=" * 72)

    if not CELLS_FILE.exists():
        raise FileNotFoundError(
            f"Fichier absent : {CELLS_FILE}"
        )

    sheets = load_cells()

    all_regions = []

    for sheet_name, rows in sheets.items():

        regions = detect_regions(
            sheet_name,
            rows
        )

        all_regions.extend(
            regions
        )

    fields = [
        "sheet",
        "region_id",
        "start_row",
        "end_row",
        "start_column",
        "end_column",
        "row_count",
        "column_span",
        "formula_count",
        "constant_count",
        "text_count",
        "numeric_count"
    ]

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()
        writer.writerows(
            all_regions
        )

    print(
        f"\nZones tabulaires candidates : "
        f"{len(all_regions)}"
    )

    print("\nPar feuille :\n")

    sheet_counts = defaultdict(int)

    for region in all_regions:
        sheet_counts[
            region["sheet"]
        ] += 1

    for sheet, count in sorted(
        sheet_counts.items()
    ):

        print(
            f"{sheet:<30} {count:>3} zone(s)"
        )

    print(
        f"\nFichier généré : "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()