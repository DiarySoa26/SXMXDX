import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "reverse_engineering" / "output"

FORMULAS_FILE = OUTPUT_DIR / "formulas.csv"
DICTIONARY_FILE = OUTPUT_DIR / "business_dictionary.csv"

OUTPUT_FILE = OUTPUT_DIR / "business_rule_catalog.csv"
SUMMARY_FILE = OUTPUT_DIR / "rule_family_summary.csv"


# ============================================================
# MAPPING CELLULE -> CODE METIER
# ============================================================

def load_business_mapping():

    mapping = {}

    if not DICTIONARY_FILE.exists():
        return mapping

    with DICTIONARY_FILE.open(
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if row["status"] != "VALIDATED":
                continue

            code = row["business_code"].strip()

            if not code:
                continue

            key = (
                row["sheet"],
                row["cell"].replace("$", "")
            )

            mapping[key] = code

    return mapping


# ============================================================
# NORMALISATION
# ============================================================

def normalize_formula(formula, business_mapping):

    if not formula:
        return ""

    result = formula.upper()

    # --------------------------------------------------------
    # Remplacer d'abord les paramètres métier connus
    # --------------------------------------------------------

    for (sheet, cell), code in business_mapping.items():

        escaped_sheet = re.escape(sheet.upper())
        escaped_cell = re.escape(cell.upper())

        # patterns = [
        #     rf"'{escaped_sheet}'!\$?{escaped_cell[0:-len(re.findall(r'\d+$', cell)[0])]}\$?{re.findall(r'\d+$', cell)[0]}",
        #     rf"{escaped_sheet}!\$?{escaped_cell}"
        # ]

        match = re.match(r"([A-Za-z]+)(\d+)$", cell)

        if not match:
            return False  # ou continue selon l'endroit où se trouve ton code

        column = re.escape(match.group(1))
        row = match.group(2)

        patterns = [
            rf"'{escaped_sheet}'!\$?{column}\$?{row}",
            rf"{escaped_sheet}!\$?{column}\$?{row}"
        ]

        # méthode plus simple / robuste en complément
        variants = [
            f"'{sheet.upper()}'!${cell[0]}${cell[1:]}",
            f"'{sheet.upper()}'!{cell}",
            f"{sheet.upper()}!${cell[0]}${cell[1:]}",
            f"{sheet.upper()}!{cell}"
        ]

        for variant in variants:
            result = result.replace(
                variant,
                f"PARAM[{code}]"
            )

    # --------------------------------------------------------
    # Supprimer les anciens +
    # Exemple =+A1 devient =A1
    # --------------------------------------------------------

    result = result.replace("=+", "=")

    # --------------------------------------------------------
    # Références inter-feuilles restantes
    #
    # 'Production'!D9
    # devient
    # REF[PRODUCTION]
    # --------------------------------------------------------

    result = re.sub(
        r"'([^']+)'!\$?[A-Z]{1,3}\$?\d+",
        lambda m: f"REF[{m.group(1)}]",
        result
    )

    result = re.sub(
        r"([A-ZÀ-Ÿ0-9 _&().-]+)!"
        r"\$?[A-Z]{1,3}\$?\d+",
        lambda m: f"REF[{m.group(1).strip()}]",
        result
    )

    # --------------------------------------------------------
    # Plages locales
    # --------------------------------------------------------

    result = re.sub(
        r"\$?[A-Z]{1,3}\$?\d+"
        r":"
        r"\$?[A-Z]{1,3}\$?\d+",
        "LOCAL_RANGE",
        result
    )

    # --------------------------------------------------------
    # Cellules locales
    # --------------------------------------------------------

    result = re.sub(
        r"\$?[A-Z]{1,3}\$?\d+",
        "LOCAL_CELL",
        result
    )

    result = re.sub(
        r"\s+",
        "",
        result
    )

    return result


# ============================================================
# IDENTIFICATION DE FAMILLE
# ============================================================

def identify_family(pattern):

    p = pattern.upper()

    if "#REF!" in p:
        return "BROKEN_REFERENCE"

    if "SUBTOTAL(" in p:
        return "AGGREGATION"

    if (
        "SUM(" in p
        or "SUMIF(" in p
        or "SUMIFS(" in p
    ):
        return "AGGREGATION"

    if "PARAM[TAUX_CHANGE_" in p:
        return "CURRENCY_CONVERSION"

    if "PARAM[TAUX_TVA]" in p:
        return "TAX"

    if "PARAM[RENDEMENT_" in p:
        return "YIELD_CALCULATION"

    if (
        "PARAM[PART_ACHAT_" in p
    ):
        return "PURCHASE_ALLOCATION"

    if "REF[PRODUCTION]" in p:
        return "PRODUCTION_DEPENDENCY"

    if "REF[BESOINS EN MICAS]" in p:
        return "MATERIAL_REQUIREMENT_DEPENDENCY"

    if "REF[COMMANDES]" in p:
        return "ORDER_DEPENDENCY"

    if "REF[SAL]" in p:
        return "SALARY_DEPENDENCY"

    if "REF[ACHAT]" in p:
        return "PURCHASE_DEPENDENCY"

    if "REF[PRESTATION]" in p:
        return "SERVICE_DEPENDENCY"

    if "REF[" in p:
        return "CROSS_SHEET_REFERENCE"

    if "*" in p:
        return "MULTIPLICATION"

    if "/" in p:
        return "DIVISION"

    if "+" in p or "-" in p:
        return "ARITHMETIC"

    if "LOCAL_CELL" in p:
        return "LOCAL_REFERENCE"

    return "OTHER"


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 72)
    print("SXMXDX - CONSTRUCTION DU CATALOGUE DES REGLES")
    print("=" * 72)

    if not FORMULAS_FILE.exists():
        raise FileNotFoundError(
            f"Fichier absent : {FORMULAS_FILE}"
        )

    business_mapping = load_business_mapping()

    print(
        f"\nParamètres métier connus : "
        f"{len(business_mapping)}"
    )

    grouped = {}
    counter = Counter()

    with FORMULAS_FILE.open(
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            pattern = normalize_formula(
                row["formula"],
                business_mapping
            )

            family = identify_family(pattern)

            key = (
                row["sheet"],
                family,
                pattern
            )

            counter[key] += 1

            if key not in grouped:

                grouped[key] = {
                    "sheet": row["sheet"],
                    "family": family,
                    "pattern": pattern,
                    "example_cell": row["cell"],
                    "example_formula": row["formula"]
                }

    # ========================================================
    # CREATION DU CATALOGUE
    # ========================================================

    rows = []

    rule_number = 1

    for key, occurrences in counter.most_common():

        item = grouped[key]

        rows.append({
            "rule_id":
                f"RULE_{rule_number:04d}",

            "sheet":
                item["sheet"],

            "family":
                item["family"],

            "occurrences":
                occurrences,

            "pattern":
                item["pattern"],

            "example_cell":
                item["example_cell"],

            "example_formula":
                item["example_formula"],

            "business_name":
                "",

            "business_description":
                "",

            "python_function":
                "",

            "status":
                (
                    "INVALID"
                    if item["family"]
                    == "BROKEN_REFERENCE"
                    else "TO_REVIEW"
                )
        })

        rule_number += 1

    fields = [
        "rule_id",
        "sheet",
        "family",
        "occurrences",
        "pattern",
        "example_cell",
        "example_formula",
        "business_name",
        "business_description",
        "python_function",
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

    # ========================================================
    # RESUME DES FAMILLES
    # ========================================================

    family_counter = Counter()

    for row in rows:
        family_counter[
            row["family"]
        ] += int(row["occurrences"])

    summary_rows = []

    for family, occurrences in (
        family_counter.most_common()
    ):

        pattern_count = sum(
            1
            for row in rows
            if row["family"] == family
        )

        summary_rows.append({
            "family": family,
            "pattern_count": pattern_count,
            "formula_occurrences": occurrences
        })

    with SUMMARY_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "family",
                "pattern_count",
                "formula_occurrences"
            ]
        )

        writer.writeheader()
        writer.writerows(summary_rows)

    # ========================================================
    # TERMINAL
    # ========================================================

    print(
        f"\nRègles candidates : {len(rows)}"
    )

    print("\nFamilles détectées :\n")

    for row in summary_rows:

        print(
            f"{row['family']:<38}"
            f"{row['pattern_count']:>5} patterns   "
            f"{row['formula_occurrences']:>6} formules"
        )

    print(
        f"\nCatalogue : {OUTPUT_FILE}"
    )

    print(
        f"Résumé    : {SUMMARY_FILE}"
    )


if __name__ == "__main__":
    main()