import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reverse_engineering"
    / "output"
)

INPUT_FILE = (
    OUTPUT_DIR
    / "input_candidates_with_context.csv"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "business_dictionary.csv"
)


# ==========================================================
# PARAMETRES DEJA IDENTIFIES
# ==========================================================
#
# Cette liste constitue le début du mapping canonique
# SXMXDX.
#
# Elle sera enrichie progressivement pendant
# le reverse-engineering.
#

KNOWN_PARAMETERS = {

    ("Données SOMIDA", "E5"): {
        "business_code": "TAUX_CHANGE_USD",
        "business_name": "Taux de change USD",
        "category": "GLOBAL_PARAMETER",
        "unit": "MGA/USD",
    },

    ("Données SOMIDA", "E6"): {
        "business_code": "TAUX_CHANGE_EUR",
        "business_name": "Taux de change EUR",
        "category": "GLOBAL_PARAMETER",
        "unit": "MGA/EUR",
    },

    ("Données SOMIDA", "E7"): {
        "business_code": "AUGMENTATION_GLOBALE_SALAIRE",
        "business_name": "Augmentation globale de salaire",
        "category": "GLOBAL_PARAMETER",
        "unit": "%",
    },

    ("Données SOMIDA", "E8"): {
        "business_code": "TAUX_TVA",
        "business_name": "Taux de TVA",
        "category": "GLOBAL_PARAMETER",
        "unit": "%",
    },

    ("Données SOMIDA", "D58"): {
        "business_code": "RENDEMENT_MICA_BRUT_GAZ",
        "business_name": "Rendement micas bruts vers gaz",
        "category": "GLOBAL_PARAMETER",
        "unit": "%",
    },

    ("Données SOMIDA", "D62"): {
        "business_code": "PART_ACHAT_TRANOMARO",
        "business_name": "Part des achats à Tranomaro",
        "category": "GLOBAL_PARAMETER",
        "unit": "%",
    },

    ("Données SOMIDA", "D63"): {
        "business_code": "PART_ACHAT_AMPANDRANDAVA",
        "business_name": "Part des achats à Ampandrandava",
        "category": "GLOBAL_PARAMETER",
        "unit": "%",
    },

    ("Données SOMIDA", "D64"): {
        "business_code": "PART_ACHAT_FORT_DAUPHIN",
        "business_name": "Part des achats à Fort Dauphin",
        "category": "GLOBAL_PARAMETER",
        "unit": "%",
    },

    ("CA", "C44"): {
        "business_code": "TAUX_PRODUITS_TRANSFORMES",
        "business_name": "Taux appliqué aux produits transformés",
        "category": "GLOBAL_PARAMETER",
        "unit": "%",
    },

    ("Données SOMIDA", "E27"): {
        "business_code": "LOYER_1_MENSUEL",
        "business_name": "Loyer mensuel 1",
        "category": "BUSINESS_INPUT",
        "unit": "MGA/mois",
    },

    ("Données SOMIDA", "E28"): {
        "business_code": "LOYER_2_MENSUEL",
        "business_name": "Loyer mensuel 2",
        "category": "BUSINESS_INPUT",
        "unit": "MGA/mois",
    },
}


def main():

    print("=" * 70)
    print("SXMXDX - BUSINESS DICTIONARY")
    print("=" * 70)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Fichier absent : {INPUT_FILE}"
        )

    rows = []

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for candidate in reader:

            key = (
                candidate["sheet"],
                candidate["cell"]
            )

            known = KNOWN_PARAMETERS.get(key)

            if known:

                status = "VALIDATED"

                business_code = (
                    known["business_code"]
                )

                business_name = (
                    known["business_name"]
                )

                category = known["category"]

                unit = known["unit"]

            else:

                status = "TO_REVIEW"

                business_code = ""

                business_name = ""

                category = ""

                unit = ""

            rows.append({

                "business_code":
                    business_code,

                "business_name":
                    business_name,

                "category":
                    category,

                "unit":
                    unit,

                "sheet":
                    candidate["sheet"],

                "cell":
                    candidate["cell"],

                "value_2024":
                    candidate["value"],

                "technical_classification":
                    candidate["classification"],

                "used_by_formulas":
                    candidate["used_by_formulas"],

                "status":
                    status,

                "context":
                    candidate["context"],
            })

    # Paramètres validés en premier
    rows.sort(
        key=lambda row: (
            0 if row["status"] == "VALIDATED" else 1,
            -int(row["used_by_formulas"]),
            row["sheet"],
            row["cell"]
        )
    )

    fields = [
        "business_code",
        "business_name",
        "category",
        "unit",
        "sheet",
        "cell",
        "value_2024",
        "technical_classification",
        "used_by_formulas",
        "status",
        "context",
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

    validated = sum(
        1
        for row in rows
        if row["status"] == "VALIDATED"
    )

    print(
        f"\nParamètres/données validés : {validated}"
    )

    print(
        f"À examiner : {len(rows) - validated}"
    )

    print(
        f"\nFichier généré : {OUTPUT_FILE}"
    )

    print("\nMapping métier validé :\n")

    for row in rows:

        if row["status"] != "VALIDATED":
            continue

        print(
            f"{row['business_code']:<35}"
            f" <- "
            f"{row['sheet']}!"
            f"{row['cell']} "
            f"({row['value_2024']} {row['unit']})"
        )


if __name__ == "__main__":
    main()