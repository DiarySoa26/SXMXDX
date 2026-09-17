import csv
from collections import defaultdict, Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reverse_engineering"
    / "output"
)

DEPENDENCIES_FILE = (
    OUTPUT_DIR
    / "sheet_dependencies.csv"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "dependency_graph.csv"
)


def main():

    print("=" * 70)
    print("SXMXDX - GRAPHE DE DEPENDANCES")
    print("=" * 70)

    graph = defaultdict(set)
    weights = Counter()
    sheets = set()

    with DEPENDENCIES_FILE.open(
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            source = row["source_sheet"]
            target = row["target_sheet"]

            if not source or not target:
                continue

            sheets.add(source)
            sheets.add(target)

            # Ignorer les références internes
            if source == target:
                continue

            # source dépend de target
            graph[source].add(target)

            weights[
                (source, target)
            ] += int(
                row["reference_count"]
            )

    rows = []

    for source in sorted(graph):

        for target in sorted(graph[source]):

            rows.append({
                "module": source,
                "depends_on": target,
                "reference_count":
                    weights[(source, target)]
            })

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "module",
                "depends_on",
                "reference_count"
            ]
        )

        writer.writeheader()
        writer.writerows(rows)

    print(
        f"\nModules détectés : {len(sheets)}"
    )

    print(
        f"Dépendances inter-feuilles : "
        f"{len(rows)}"
    )

    print("\nPrincipales dépendances :\n")

    for row in sorted(
        rows,
        key=lambda x:
            -x["reference_count"]
    )[:30]:

        print(
            f"{row['module']:<25}"
            f" dépend de "
            f"{row['depends_on']:<25}"
            f" {row['reference_count']:>5} refs"
        )

    print(
        f"\nFichier : {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()