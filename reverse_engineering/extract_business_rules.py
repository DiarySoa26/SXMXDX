import csv
import re
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reverse_engineering"
    / "output"
)

FORMULAS_FILE = OUTPUT_DIR / "formulas.csv"

OUTPUT_FILE = (
    OUTPUT_DIR
    / "formula_patterns.csv"
)


def normalize_formula(formula):
    """
    Normalise une formule pour regrouper les copies
    mensuelles d'une même règle.

    Exemple :

        =C10*C11
        =D10*D11
        =E10*E11

    deviennent approximativement le même pattern.
    """

    if not formula:
        return ""

    result = formula.upper()

    # Retirer $
    result = result.replace("$", "")

    # Remplacer les références de cellule
    result = re.sub(
        r"(?<![A-Z0-9_])"
        r"([A-Z]{1,3})(\d+)",
        "CELL",
        result
    )

    # Réduire espaces
    result = re.sub(
        r"\s+",
        "",
        result
    )

    return result


def main():

    print("=" * 70)
    print("SXMXDX - EXTRACTION DES PATTERNS DE FORMULES")
    print("=" * 70)

    patterns = Counter()

    examples = {}

    sheet_patterns = Counter()

    with FORMULAS_FILE.open(
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            formula = row["formula"]

            pattern = normalize_formula(
                formula
            )

            key = (
                row["sheet"],
                pattern
            )

            patterns[key] += 1

            if key not in examples:

                examples[key] = {
                    "sheet": row["sheet"],
                    "cell": row["cell"],
                    "formula": formula
                }

    rows = []

    for (
        sheet,
        pattern
    ), count in patterns.most_common():

        example = examples[
            (sheet, pattern)
        ]

        rows.append({

            "sheet": sheet,

            "pattern":
                pattern,

            "occurrences":
                count,

            "example_cell":
                example["cell"],

            "example_formula":
                example["formula"],

            "business_rule_code":
                "",

            "business_description":
                "",

            "status":
                "TO_REVIEW"
        })

    fields = [
        "sheet",
        "pattern",
        "occurrences",
        "example_cell",
        "example_formula",
        "business_rule_code",
        "business_description",
        "status"
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

        writer.writerows(rows)

    print(
        f"\nPatterns différents : "
        f"{len(rows)}"
    )

    print(
        f"\nFichier généré : "
        f"{OUTPUT_FILE}"
    )

    print(
        "\nTop 30 règles répétitives :\n"
    )

    for row in rows[:30]:

        print(
            f"{row['sheet']:<25}"
            f"{row['occurrences']:>5}x  "
            f"{row['example_cell']:<8} "
            f"{row['example_formula'][:70]}"
        )


if __name__ == "__main__":
    main()