import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "sales.csv"


def main():
    with INPUT_FILE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)

        print("Колонки:", reader.fieldnames)

        total_rows = 0

        for row in reader:
            total_rows += 1

            if total_rows <= 3:
                print(row)

        print("Всего строк:", total_rows)


if __name__ == "__main__":
    main()
