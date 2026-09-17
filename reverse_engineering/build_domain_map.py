import csv
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reverse_engineering"
    / "output"
)

SHEETS_FILE = OUTPUT_DIR / "sheets.csv"

OUTPUT_FILE = OUTPUT_DIR / "domain_map.csv"


# ============================================================
# CLASSIFICATION METIER DES FEUILLES
# ============================================================

DOMAIN_MAPPING = {

    # --------------------------------------------------------
    # PARAMETRES
    # --------------------------------------------------------

    "Données SOMIDA": {
        "domain": "PARAMETERS",
        "role": "INPUT_PARAMETER",
        "persist": True
    },

    # --------------------------------------------------------
    # COMMANDES
    # --------------------------------------------------------

    "Commandes": {
        "domain": "ORDERS",
        "role": "BUSINESS_DATA",
        "persist": True
    },

    "Commande à honorer": {
        "domain": "ORDERS",
        "role": "INTERMEDIATE",
        "persist": False
    },

    "Détails": {
        "domain": "ORDERS",
        "role": "DETAIL",
        "persist": True
    },

    # --------------------------------------------------------
    # PRODUCTION
    # --------------------------------------------------------

    "Production": {
        "domain": "PRODUCTION",
        "role": "CALCULATION",
        "persist": True
    },

    "Traitement": {
        "domain": "PRODUCTION",
        "role": "CALCULATION",
        "persist": True
    },

    "Calcul": {
        "domain": "PRODUCTION",
        "role": "TECHNICAL_CALCULATION",
        "persist": False
    },

    # --------------------------------------------------------
    # MATIERES
    # --------------------------------------------------------

    "Besoins en micas": {
        "domain": "MATERIALS",
        "role": "CALCULATION",
        "persist": True
    },

    # --------------------------------------------------------
    # ACHATS
    # --------------------------------------------------------

    "Détails Achats direct": {
        "domain": "PURCHASES",
        "role": "DETAIL",
        "persist": True
    },

    "Achat": {
        "domain": "PURCHASES",
        "role": "CALCULATION",
        "persist": True
    },

    # --------------------------------------------------------
    # CHIFFRE D'AFFAIRES
    # --------------------------------------------------------

    "CA": {
        "domain": "REVENUE",
        "role": "CALCULATION",
        "persist": True
    },

    # --------------------------------------------------------
    # RH
    # --------------------------------------------------------

    "Sal": {
        "domain": "PAYROLL",
        "role": "CALCULATION",
        "persist": True
    },

    "Primes": {
        "domain": "PAYROLL",
        "role": "CALCULATION",
        "persist": True
    },

    "Org": {
        "domain": "PAYROLL",
        "role": "REFERENCE",
        "persist": True
    },

    "Org (2)": {
        "domain": "PAYROLL",
        "role": "REFERENCE",
        "persist": False
    },

    "Organigramme": {
        "domain": "PAYROLL",
        "role": "REPORT",
        "persist": False
    },

    "Feuil3": {
        "domain": "PAYROLL",
        "role": "INTERMEDIATE",
        "persist": False
    },

    # --------------------------------------------------------
    # PRESTATIONS
    # --------------------------------------------------------

    "Prestation": {
        "domain": "SERVICES",
        "role": "BUSINESS_DATA",
        "persist": True
    },

    # --------------------------------------------------------
    # CHARGES
    # --------------------------------------------------------

    "I&T": {
        "domain": "EXPENSES",
        "role": "CALCULATION",
        "persist": True
    },

    "Autres": {
        "domain": "EXPENSES",
        "role": "CALCULATION",
        "persist": True
    },

    # --------------------------------------------------------
    # INVESTISSEMENTS
    # --------------------------------------------------------

    "Invest FD": {
        "domain": "INVESTMENTS",
        "role": "BUSINESS_DATA",
        "persist": True
    },

    "Amort": {
        "domain": "INVESTMENTS",
        "role": "CALCULATION",
        "persist": True
    },

    # --------------------------------------------------------
    # FINANCEMENT
    # --------------------------------------------------------

    "Emprunts FD": {
        "domain": "FINANCING",
        "role": "BUSINESS_DATA",
        "persist": True
    },

    "Frais financier": {
        "domain": "FINANCING",
        "role": "CALCULATION",
        "persist": True
    },

    "Détails FF FD": {
        "domain": "FINANCING",
        "role": "DETAIL",
        "persist": True
    },

    # --------------------------------------------------------
    # ETATS FINANCIERS
    # --------------------------------------------------------

    "CR Nature FD": {
        "domain": "FINANCIAL_STATEMENTS",
        "role": "RESULT",
        "persist": True
    },

    "Etat_Trésorerie FD": {
        "domain": "TREASURY",
        "role": "RESULT",
        "persist": True
    },

    "AN": {
        "domain": "ANALYSIS",
        "role": "RESULT",
        "persist": True
    },

    # --------------------------------------------------------
    # REPORTING
    # --------------------------------------------------------

    "Stat": {
        "domain": "REPORTING",
        "role": "REPORT",
        "persist": False
    },

    "Tableau de bord": {
        "domain": "REPORTING",
        "role": "REPORT",
        "persist": False
    },

    # --------------------------------------------------------
    # SITES
    # --------------------------------------------------------

    "FORT DAUPHIN": {
        "domain": "OPERATIONS",
        "role": "SOURCE_DATA",
        "persist": True
    },

    "AMPANDRANDAVA": {
        "domain": "OPERATIONS",
        "role": "SOURCE_DATA",
        "persist": True
    },

    "BL": {
        "domain": "FINANCIAL_STATEMENTS",
        "role": "ACCOUNTING_DATA",
        "persist": True
    },

    " OKB TRA ABR": {
        "domain": "OPERATIONS",
        "role": "COST_SIMULATION",
        "persist": True
    },

    "OKB FP1": {
        "domain": "OPERATIONS",
        "role": "COST_SIMULATION",
        "persist": True
    },

    "Goodeis": {
        "domain": "OPERATIONS",
        "role": "COST_SIMULATION",
        "persist": True
    },

    "Recap coupeuses FD": {
        "domain": "PAYROLL",
        "role": "SOURCE_DATA",
        "persist": True
    },

    "Recap coupeuses Ampandra": {
        "domain": "PAYROLL",
        "role": "SOURCE_DATA",
        "persist": True
    },

    "Feuil1 (2)": {
        "domain": "PAYROLL",
        "role": "MONTHLY_SUMMARY",
        "persist": True
    },

    "Feuil1": {
        "domain": "PURCHASES",
        "role": "SOURCE_DATA",
        "persist": True
    },
}


def main():

    print("=" * 72)
    print("SXMXDX - DOMAIN MAPPING")
    print("=" * 72)

    if not SHEETS_FILE.exists():
        raise FileNotFoundError(
            f"Fichier absent : {SHEETS_FILE}"
        )

    rows = []

    unmapped = []

    with SHEETS_FILE.open(
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for sheet in reader:

            name = sheet["sheet"]

            config = DOMAIN_MAPPING.get(name)

            if config is None:

                config = {
                    "domain": "TO_REVIEW",
                    "role": "TO_REVIEW",
                    "persist": False
                }

                unmapped.append(name)

            rows.append({

                "sheet": name,

                "domain":
                    config["domain"],

                "role":
                    config["role"],

                "persist":
                    config["persist"],

                "constant_cells":
                    sheet["constant_cells"],

                "formula_cells":
                    sheet["formula_cells"],

                "non_empty_cells":
                    sheet["non_empty_cells"]
            })

    fields = [
        "sheet",
        "domain",
        "role",
        "persist",
        "constant_cells",
        "formula_cells",
        "non_empty_cells"
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

    domain_counter = Counter(
        row["domain"]
        for row in rows
    )

    print("\nDomaines :\n")

    for domain, count in sorted(
        domain_counter.items()
    ):

        print(
            f"{domain:<30} {count:>3} feuille(s)"
        )

    if unmapped:

        print(
            "\n⚠ Feuilles restant à classifier :"
        )

        for sheet in unmapped:
            print(f" - {sheet}")

    print(
        f"\nFichier généré : {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()