import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


HOST = os.getenv("POSTGRES_HOST", "postgres")
PORT = os.getenv("POSTGRES_PORT", "5432")
DATABASE = os.getenv("POSTGRES_DB", "sxmxdx2")
USER = os.getenv("POSTGRES_USER", "sxmxdx")
PASSWORD = os.getenv("POSTGRES_PASSWORD", "diary")


JDBC_URL = (
    f"jdbc:postgresql://"
    f"{HOST}:{PORT}/{DATABASE}"
)


JDBC_OPTIONS = {
    "url": JDBC_URL,
    "user": USER,
    "password": PASSWORD,
    "driver": "org.postgresql.Driver"
}


def read_table(spark, table):

    return (
        spark.read
        .format("jdbc")
        .options(**JDBC_OPTIONS)
        .option("dbtable", table)
        .load()
    )


def write_table(df, table, mode="append"):

    (
        df.write
        .format("jdbc")
        .options(**JDBC_OPTIONS)
        .option("dbtable", table)
        .mode(mode)
        .save()
    )


def main():

    if len(sys.argv) < 3:

        raise ValueError(
            "Usage : load_parameters.py "
            "<batch_id> <exercice_id>"
        )

    batch_id = int(sys.argv[1])
    exercice_id = int(sys.argv[2])

    spark = (
        SparkSession.builder
        .appName("SXMXDX-Parameters")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    print("=" * 70)
    print("SXMXDX - EXTRACTION DES PARAMETRES")
    print("=" * 70)

    # ========================================================
    # STAGING
    # ========================================================

    staging = (
        read_table(
            spark,
            "staging.import_cell"
        )
        .filter(
            F.col("import_batch_id")
            == batch_id
        )
    )

    # ========================================================
    # DEFINITIONS DES PARAMETRES
    # ========================================================

    definitions = (
        read_table(
            spark,
            "sxmxdx.parametre_definition"
        )
        .filter(
            F.col("actif") == True
        )
    )

    # ========================================================
    # JOINTURE PAR POSITION EXCEL
    # ========================================================

    parameters = (
        definitions.alias("d")
        .join(
            staging.alias("s"),
            (
                F.col("d.excel_sheet")
                == F.col("s.sheet_name")
            )
            &
            (
                F.col("d.excel_cell")
                == F.col("s.cell_reference")
            ),
            "left"
        )
    )

    print("\nParamètres détectés :")

    parameters.select(
        F.col("d.code"),
        F.col("d.libelle"),
        F.col("d.unite"),
        F.col("s.raw_value")
    ).show(
        100,
        truncate=False
    )

    # ========================================================
    # PARAMETRES MANQUANTS
    # ========================================================

    missing = parameters.filter(
        F.col("s.raw_value").isNull()
    )

    missing_count = missing.count()

    if missing_count > 0:

        print(
            f"\nATTENTION : "
            f"{missing_count} paramètre(s) absent(s)"
        )

        missing.select(
            "d.code",
            "d.excel_sheet",
            "d.excel_cell"
        ).show(
            truncate=False
        )

    # ========================================================
    # CONVERSION NUMERIQUE
    # ========================================================

    values = (
        parameters
        .filter(
            F.col("s.raw_value").isNotNull()
        )
        .select(
            F.lit(exercice_id)
            .cast("long")
            .alias("exercice_id"),

            F.col("d.parametre_id")
            .cast("long")
            .alias("parametre_id"),

            F.regexp_replace(
                F.col("s.raw_value"),
                ",",
                "."
            )
            .cast("decimal(20,6)")
            .alias("valeur_numerique"),

            F.lit(None)
            .cast("string")
            .alias("valeur_texte")
        )
    )

    print("\nValeurs normalisées :")

    values.show(
        100,
        truncate=False
    )

    # ========================================================
    # IMPORTANT
    #
    # parametre_exercice possède une contrainte UNIQUE.
    # On supprime donc d'abord les valeurs de cet exercice.
    # ========================================================

    # Spark/JDBC n'est pas pratique pour DELETE.
    # Pour le moment, l'exercice de référence doit être
    # chargé une seule fois.
    #
    # Nous améliorerons ensuite avec UPSERT PostgreSQL.

    existing = (
        read_table(
            spark,
            "sxmxdx.parametre_exercice"
        )
        .filter(
            F.col("exercice_id")
            == exercice_id
        )
    )

    if existing.count() > 0:

        raise RuntimeError(
            "Des paramètres existent déjà pour "
            f"l'exercice {exercice_id}. "
            "Nettoyez-les avant de relancer."
        )

    write_table(
        values,
        "sxmxdx.parametre_exercice"
    )

    print(
        f"\n{values.count()} "
        f"paramètre(s) chargé(s)."
    )

    spark.stop()


if __name__ == "__main__":
    main()