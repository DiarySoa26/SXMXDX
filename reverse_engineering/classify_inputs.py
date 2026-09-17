import csv
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reverse_engineering"
    / "output"
)

CELLS_FILE = OUTPUT_DIR / "cells.csv"
DEPENDENCIES_FILE = OUTPUT_DIR / "dependencies.csv"

RESULT_FILE = OUTPUT_DIR / "classified_cells.csv"
CANDIDATES_FILE = OUTPUT_DIR / "input_candidates.csv"
SUMMARY_FILE = OUTPUT_DIR / "classification_summary.csv"


# ==========================================================
# OUTILS
# ==========================================================

def is_numeric(cell_type):
    return cell_type == "NUMBER"


def normalize_reference(reference):
    """
    Enlève les $ :
    $E$11 -> E11
    """
    if not reference:
        return ""

    return reference.replace("$", "")


def is_single_cell_reference(reference):
    """
    Retourne True pour :
        E11
        $E$11

    False pour :
        E11:E20
        NOM_PLAGE
    """

    ref = normalize_reference(reference)

    return ":" not in ref


# ==========================================================
# CHARGEMENT DES DEPENDANCES
# ==========================================================

def load_usage_count():
    """
    Compte combien de formules utilisent chaque cellule.

    Exemple :
        Données SOMIDA!E11 -> 145 utilisations
    """

    usage = Counter()

    if not DEPENDENCIES_FILE.exists():
        raise FileNotFoundError(
            f"Fichier absent : {DEPENDENCIES_FILE}"
        )

    with DEPENDENCIES_FILE.open(
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if row["reference_type"] != "CELL":
                continue

            sheet = row["target_sheet"]
            reference = normalize_reference(
                row["target_reference"]
            )

            if not sheet or not reference:
                continue

            key = (sheet, reference)

            usage[key] += 1

    return usage


# ==========================================================
# CLASSIFICATION
# ==========================================================

def classify(row, usage_count):

    cell_type = row["type"]
    sheet = row["sheet"]
    cell = row["cell"]
    value = row["value"]

    key = (sheet, cell)

    used_by_formulas = usage_count.get(key, 0)

    # ------------------------------------------------------
    # FORMULE
    # ------------------------------------------------------

    if cell_type == "FORMULA":

        return {
            "classification": "CALCULATED",
            "confidence": "HIGH",
            "reason": "Cellule contenant une formule Excel"
        }

    # ------------------------------------------------------
    # TEXTE
    # ------------------------------------------------------

    if cell_type == "TEXT":

        return {
            "classification": "LABEL",
            "confidence": "MEDIUM",
            "reason": "Constante textuelle"
        }

    # ------------------------------------------------------
    # BOOLEEN
    # ------------------------------------------------------

    if cell_type == "BOOLEAN":

        return {
            "classification": "CANDIDATE_PARAMETER",
            "confidence": "MEDIUM",
            "reason": "Valeur booléenne constante"
        }

    # ------------------------------------------------------
    # NOMBRE
    # ------------------------------------------------------

    if is_numeric(cell_type):

        if used_by_formulas > 0:

            return {
                "classification": "CANDIDATE_PARAMETER",
                "confidence": "HIGH",
                "reason": (
                    f"Constante numérique utilisée par "
                    f"{used_by_formulas} formule(s)"
                )
            }

        return {
            "classification": "CANDIDATE_INPUT",
            "confidence": "MEDIUM",
            "reason": (
                "Constante numérique non calculée ; "
                "validation métier nécessaire"
            )
        }

    # ------------------------------------------------------
    # AUTRES
    # ------------------------------------------------------

    return {
        "classification": "UNKNOWN",
        "confidence": "LOW",
        "reason": f"Type technique : {cell_type}"
    }


# ==========================================================
# MAIN
# ==========================================================

def main():

    if not CELLS_FILE.exists():
        raise FileNotFoundError(
            "cells.csv absent. "
            "Exécute excel_inspector.py avant ce script."
        )

    print("=" * 70)
    print("SXMXDX - CLASSIFICATION DES CELLULES")
    print("=" * 70)

    print("\nChargement des dépendances...")

    usage_count = load_usage_count()

    print(
        f"{len(usage_count)} cellules référencées "
        f"directement par des formules."
    )

    classified_rows = []
    candidate_rows = []

    summary = defaultdict(Counter)

    # ------------------------------------------------------
    # Lecture des cellules
    # ------------------------------------------------------

    with CELLS_FILE.open(
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            result = classify(
                row,
                usage_count
            )

            key = (
                row["sheet"],
                row["cell"]
            )

            usage = usage_count.get(
                key,
                0
            )

            output_row = {
                "sheet": row["sheet"],
                "cell": row["cell"],
                "row": row["row"],
                "column": row["column"],
                "technical_type": row["type"],
                "value": row["value"],
                "classification":
                    result["classification"],
                "confidence":
                    result["confidence"],
                "used_by_formulas":
                    usage,
                "reason":
                    result["reason"],
                "number_format":
                    row["number_format"]
            }

            classified_rows.append(
                output_row
            )

            summary[
                row["sheet"]
            ][
                result["classification"]
            ] += 1

            if result["classification"] in {
                "CANDIDATE_INPUT",
                "CANDIDATE_PARAMETER"
            }:

                candidate_rows.append(
                    output_row
                )

    # ------------------------------------------------------
    # Trier les candidats
    #
    # Les cellules les plus utilisées dans les formules
    # apparaissent en premier.
    # ------------------------------------------------------

    candidate_rows.sort(
        key=lambda x: (
            -int(x["used_by_formulas"]),
            x["sheet"],
            int(x["row"]),
            int(x["column"])
        )
    )

    # ======================================================
    # classified_cells.csv
    # ======================================================

    fields = [
        "sheet",
        "cell",
        "row",
        "column",
        "technical_type",
        "value",
        "classification",
        "confidence",
        "used_by_formulas",
        "reason",
        "number_format"
    ]

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
        writer.writerows(
            classified_rows
        )

    # ======================================================
    # input_candidates.csv
    # ======================================================

    with CANDIDATES_FILE.open(
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
            candidate_rows
        )

    # ======================================================
    # classification_summary.csv
    # ======================================================

    all_classes = sorted({
        classification
        for sheet_counter in summary.values()
        for classification in sheet_counter
    })

    summary_fields = [
        "sheet",
        *all_classes,
        "total"
    ]

    with SUMMARY_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=summary_fields
        )

        writer.writeheader()

        for sheet in sorted(summary):

            row = {
                "sheet": sheet
            }

            total = 0

            for classification in all_classes:

                count = summary[
                    sheet
                ][classification]

                row[
                    classification
                ] = count

                total += count

            row["total"] = total

            writer.writerow(row)

    # ======================================================
    # TERMINAL
    # ======================================================

    print("\nClassification terminée.")

    print(
        f"\nCellules analysées : "
        f"{len(classified_rows)}"
    )

    print(
        f"Candidats INPUT/PARAMETER : "
        f"{len(candidate_rows)}"
    )

    print("\nFichiers générés :")

    print(
        f" - {RESULT_FILE.name}"
    )

    print(
        f" - {CANDIDATES_FILE.name}"
    )

    print(
        f" - {SUMMARY_FILE.name}"
    )

    print("\nTop 30 paramètres potentiels :\n")

    for candidate in candidate_rows[:30]:

        print(
            f"{candidate['sheet']:<25} "
            f"{candidate['cell']:<8} "
            f"{str(candidate['value'])[:18]:<20} "
            f"utilisé {candidate['used_by_formulas']} fois"
        )


if __name__ == "__main__":
    main()