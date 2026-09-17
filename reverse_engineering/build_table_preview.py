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

REGIONS_FILE = (
    OUTPUT_DIR
    / "detected_table_regions.csv"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "table_region_previews.csv"
)


MAX_PREVIEW_ROWS = 8


def column_letter(number):

    result = ""

    while number:

        number, remainder = divmod(
            number - 1,
            26
        )

        result = (
            chr(65 + remainder)
            + result
        )

    return result


def load_cells():

    cells = {}

    with CELLS_FILE.open(
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for item in reader:

            key = (
                item["sheet"],
                int(item["row"]),
                int(item["column"])
            )

            cells[key] = item

    return cells


def main():

    print("=" * 72)
    print("SXMXDX - APERCU DES ZONES TABULAIRES")
    print("=" * 72)

    cells = load_cells()

    results = []

    with REGIONS_FILE.open(
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for region in reader:

            sheet = region["sheet"]

            start_row = int(
                region["start_row"]
            )

            end_row = int(
                region["end_row"]
            )

            start_column = int(
                region["start_column"]
            )

            end_column = int(
                region["end_column"]
            )

            preview_lines = []

            preview_end = min(
                end_row,
                start_row + MAX_PREVIEW_ROWS - 1
            )

            for row in range(
                start_row,
                preview_end + 1
            ):

                values = []

                for column in range(
                    start_column,
                    end_column + 1
                ):

                    cell = cells.get(
                        (
                            sheet,
                            row,
                            column
                        )
                    )

                    if cell:
                        value = cell["value"]
                    else:
                        value = ""

                    if len(value) > 40:
                        value = value[:37] + "..."

                    values.append(
                        f"{column_letter(column)}={value}"
                    )

                preview_lines.append(
                    " ; ".join(values)
                )

            results.append({

                **region,

                "preview":
                    " || ".join(
                        preview_lines
                    )
            })

    fields = list(
        results[0].keys()
    ) if results else []

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
        writer.writerows(results)

    print(
        f"\n{len(results)} zones analysées."
    )

    print(
        f"\nFichier généré : "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()