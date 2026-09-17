import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


HOST = os.getenv(
    "POSTGRES_HOST",
    "postgres"
)

PORT = os.getenv(
    "POSTGRES_PORT",
    "5432"
)

DATABASE = os.getenv(
    "POSTGRES_DB",
    "sxmxdx2"
)

USER = os.getenv(
    "POSTGRES_USER",
    "sxmxdx"
)

PASSWORD = os.getenv(
    "POSTGRES_PASSWORD",
    "diary"
)


JDBC_URL = (
    f"jdbc:postgresql://"
    f"{HOST}:{PORT}/{DATABASE}"
)


def read_postgres(
    spark,
    table
):

    return (
        spark.read
        .format("jdbc")
        .option(
            "url",
            JDBC_URL
        )
        .option(
            "dbtable",
            table
        )
        .option(
            "user",
            USER
        )
        .option(
            "password",
            PASSWORD
        )
        .option(
            "driver",
            "org.postgresql.Driver"
        )
        .load()
    )


def main():

    if len(sys.argv) < 2:

        raise ValueError(
            "import_batch_id obligatoire"
        )

    batch_id = int(
        sys.argv[1]
    )

    spark = (
        SparkSession
        .builder
        .appName(
            "SXMXDX-Staging-Validation"
        )
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel(
        "WARN"
    )

    print("=" * 70)
    print("SXMXDX - VALIDATION PYSPARK")
    print("=" * 70)

    staging = read_postgres(
        spark,
        "staging.import_cell"
    )

    # --------------------------------------------------------
    # Garder uniquement le batch demandé
    # --------------------------------------------------------

    data = staging.filter(
        F.col(
            "import_batch_id"
        ) == batch_id
    )

    total = data.count()

    print(
        f"\nCellules du batch : "
        f"{total}"
    )

    # ========================================================
    # STATISTIQUES PAR FEUILLE
    # ========================================================

    print(
        "\nCellules par feuille :"
    )

    (
        data
        .groupBy("sheet_name")
        .count()
        .orderBy(
            F.desc("count")
        )
        .show(
            100,
            truncate=False
        )
    )

    # ========================================================
    # STATISTIQUES PAR TYPE
    # ========================================================

    print(
        "\nTypes techniques :"
    )

    (
        data
        .groupBy(
            "technical_type"
        )
        .count()
        .orderBy(
            F.desc("count")
        )
        .show(
            truncate=False
        )
    )

    # ========================================================
    # REFERENCES EXCEL CASSEES
    # ========================================================

    broken = data.filter(
        F.col(
            "raw_value"
        ).contains("#REF!")
    )

    broken_count = (
        broken.count()
    )

    print(
        f"\nRéférences #REF! : "
        f"{broken_count}"
    )

    broken.select(
        "sheet_name",
        "cell_reference",
        "raw_value"
    ).show(
        30,
        truncate=False
    )

    # ========================================================
    # FORMULES
    # ========================================================

    formulas = data.filter(
        F.col(
            "technical_type"
        ) == "FORMULA"
    )

    formula_count = (
        formulas.count()
    )

    print(
        f"\nFormules : "
        f"{formula_count}"
    )

    # ========================================================
    # CONSTANTES NUMERIQUES
    # ========================================================

    numeric = data.filter(
        F.col(
            "technical_type"
        ) == "NUMBER"
    )

    print(
        f"Constantes numériques : "
        f"{numeric.count()}"
    )

    # ========================================================
    # CONTRÔLE FINAL
    # ========================================================

    print("\nRésumé :")

    print(
        f"  cellules : {total}"
    )

    print(
        f"  formules  : {formula_count}"
    )

    print(
        f"  #REF!     : {broken_count}"
    )

    spark.stop()


if __name__ == "__main__":
    main()