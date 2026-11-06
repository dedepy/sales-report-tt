
import csv
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "sales.csv"
OUTPUT_FILE = BASE_DIR / "daily_by_sku.csv"


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


def aggregate_orders(rows):
    groups = {}

    for row in rows:
        key = (row["sku"], row["order_date"])

        if key not in groups:
            groups[key] = {
                "order_ids": set(),
                "revenue": 0
            }

        group = groups[key]

        group["order_ids"].add(row["order_id"])

        if row["status"] == "delivered":
            quantity = int(row["quantity"])
            price = int(row["price"])

            group["revenue"] += quantity * price

    return groups



def save_report(groups, output_file):
    with output_file.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "sku", "order_date", "orders", "revenue"
        ])

        for sku, order_date in sorted(groups):
            group = groups[(sku, order_date)]

            writer.writerow([
                sku,
                order_date,
                len(group["order_ids"]),
                group["revenue"]
            ])


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


    groups = aggregate_orders(cleaned_rows)

    total_orders = sum(
        len(group["order_ids"])
        for group in groups.values()
    )

    total_revenue = sum(
        group["revenue"]
        for group in groups.values()
    )

    print("\nРезультаты группировки:")
    print("Количество групп:", len(groups))
    print("Всего заказов:", total_orders)
    print("Общая выручка:", total_revenue, "руб.")

    save_report(groups, OUTPUT_FILE)
    print(f"\nОтчёт сохранён: {OUTPUT_FILE}")


    with OUTPUT_FILE.open(
        "r", encoding="utf-8", newline=""
    ) as file:
        report_rows = list(csv.DictReader(file))

    print("\nПроверка выходного файла:")
    print("Строк:", len(report_rows))
    print(
        "Всего заказов:",
        sum(int(row["orders"]) for row in report_rows)
    )
    print(
        "Общая выручка:",
        sum(int(row["revenue"]) for row in report_rows)
    )

    keys = [
        (row["sku"], row["order_date"])
        for row in report_rows
    ]
    print("Сортировка верная:", keys == sorted(keys))
    print("Нет повторных групп:", len(keys) == len(set(keys)))


if __name__ == "__main__":
    main()
