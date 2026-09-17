import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


HOST = os.getenv("POSTGRES_HOST", "postgres")
PORT = os.getenv("POSTGRES_PORT", "5432")
DB = os.getenv("POSTGRES_DB", "sxmxdx2")
USER = os.getenv("POSTGRES_USER", "sxmxdx")
PASSWORD = os.getenv("POSTGRES_PASSWORD", "diary")


URL = (
    f"jdbc:postgresql://"
    f"{HOST}:{PORT}/{DB}"
)


def main():

    batch_id = int(sys.argv[1])

    spark = (
        SparkSession.builder
        .appName("SXMXDX-Inspect-CA")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel(
        "WARN"
    )

    staging = (
        spark.read
        .format("jdbc")
        .option("url", URL)
        .option(
            "dbtable",
            "staging.import_cell"
        )
        .option("user", USER)
        .option("password", PASSWORD)
        .option(
            "driver",
            "org.postgresql.Driver"
        )
        .load()
    )

    ca = (
        staging
        .filter(
            (F.col("import_batch_id") == batch_id)
            &
            (F.col("sheet_name") == "CA")
            &
            (F.col("row_number") >= 55)
        )
    )

    # ========================================================
    # Transformer les cellules en lignes
    #
    # row | B | C | D | E | F | G | H | I | J | K
    # ========================================================

    pivot = (
        ca
        .filter(
            F.col("column_number")
            .between(2, 11)
        )
        .groupBy("row_number")
        .pivot(
            "column_number",
            list(range(2, 12))
        )
        .agg(
            F.first("raw_value")
        )
        .orderBy("row_number")
    )

    (
        pivot
        .withColumnRenamed("2", "reference")
        .withColumnRenamed("3", "type")
        .withColumnRenamed("4", "date")
        .withColumnRenamed("5", "client")
        .withColumnRenamed("6", "pays")
        .withColumnRenamed("7", "quantite")
        .withColumnRenamed("8", "prix_unitaire")
        .withColumnRenamed("9", "montant_mga_excel")
        .withColumnRenamed("10", "montant_usd_excel")
        .withColumnRenamed("11", "montant_eur_excel")
        .show(
            200,
            truncate=False
        )
    )

    spark.stop()


if __name__ == "__main__":
    main()