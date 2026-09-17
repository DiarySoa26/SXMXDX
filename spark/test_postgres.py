import os

from pyspark.sql import SparkSession


POSTGRES_HOST = os.getenv(
    "POSTGRES_HOST",
    "postgres"
)

POSTGRES_PORT = os.getenv(
    "POSTGRES_PORT",
    "5432"
)

POSTGRES_DB = os.getenv(
    "POSTGRES_DB",
    "sxmxdx2"
)

POSTGRES_USER = os.getenv(
    "POSTGRES_USER",
    "sxmxdx"
)

POSTGRES_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD",
    "diary"
)


JDBC_URL = (
    f"jdbc:postgresql://"
    f"{POSTGRES_HOST}:"
    f"{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)


def main():

    print("=" * 70)
    print("SXMXDX - TEST SPARK / POSTGRESQL")
    print("=" * 70)

    spark = (
        SparkSession
        .builder
        .appName(
            "SXMXDX-Test-PostgreSQL"
        )
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel(
        "WARN"
    )

    print(
        f"\nConnexion JDBC : "
        f"{JDBC_URL}"
    )

    df = (
        spark.read
        .format("jdbc")
        .option(
            "url",
            JDBC_URL
        )
        .option(
            "dbtable",
            "sxmxdx.exercice"
        )
        .option(
            "user",
            POSTGRES_USER
        )
        .option(
            "password",
            POSTGRES_PASSWORD
        )
        .option(
            "driver",
            "org.postgresql.Driver"
        )
        .load()
    )

    print(
        "\nContenu de "
        "sxmxdx.exercice :\n"
    )

    df.show(
        truncate=False
    )

    print(
        "\nNombre d'exercices : "
        f"{df.count()}"
    )

    print(
        "\nConnexion "
        "Spark -> PostgreSQL OK."
    )

    spark.stop()


if __name__ == "__main__":
    main()