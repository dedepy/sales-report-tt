
import csv
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "sales.csv"


def normalize_status(raw_status):
    status = raw_status.strip().lower()

    if status == "canceled":
        status = "cancelled"

    if status not in {"delivered", "cancelled"}:
        raise ValueError(f"Неизвестный статус: {raw_status!r}")

    return status


def clean_orders(rows):
    unique_orders = {}
    duplicate_count = 0

    for row in rows:
        cleaned_row = row.copy()
        cleaned_row["status"] = normalize_status(row["status"])

        order_id = cleaned_row["order_id"]

        if order_id in unique_orders:
            if unique_orders[order_id] != cleaned_row:
                raise ValueError(
                    f"Противоречивые данные заказа {order_id}"
                )

            duplicate_count += 1
            continue

        unique_orders[order_id] = cleaned_row

    return list(unique_orders.values()), duplicate_count


def main():
    with INPUT_FILE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        rows = list(csv.DictReader(file))

    cleaned_rows, duplicates = clean_orders(rows)

    print("Исходных строк:", len(rows))
    print("Удалено дублей:", duplicates)
    print("Уникальных заказов:", len(cleaned_rows))

    statuses = Counter(
        row["status"] for row in cleaned_rows
    )

    print("\nСтатусы после очистки:")
    for status, count in statuses.items():
        print(f"  {status}: {count}")

    missing_quantity = [
        row for row in cleaned_rows
        if not row["quantity"].strip()
    ]

    print("\nЗаказов без quantity:", len(missing_quantity))

    for row in missing_quantity:
        print(
            f"  Заказ {row['order_id']}, "
            f"статус: {row['status']}"
        )


if __name__ == "__main__":
    main()
