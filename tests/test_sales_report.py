import csv
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sales_report import (
    normalize_status,
    clean_orders,
    aggregate_orders,
    save_report,
)

class TestSalesReport(unittest.TestCase):

    def test_normalize_status(self):
        self.assertEqual(
            normalize_status(" Delivered "),
            "delivered"
        )

        self.assertEqual(
            normalize_status("DELIVERED"),
            "delivered"
        )

        self.assertEqual(
            normalize_status("canceled"),
            "cancelled"
        )

        self.assertEqual(
            normalize_status("CANCELLED"),
            "cancelled"
        )

    def test_unknown_status(self):
        with self.assertRaises(ValueError):
            normalize_status("pending")


    def test_duplicate_orders(self):
        order = {
            "order_id": "1001",
            "order_date": "2026-09-01",
            "sku": "ABC",
            "quantity": "2",
            "price": "500",
            "status": "delivered",
        }

        rows = [order, order.copy()]

        cleaned_rows, duplicates = clean_orders(rows)

        self.assertEqual(duplicates, 1)
        self.assertEqual(len(cleaned_rows), 1)
        self.assertEqual(cleaned_rows[0], order)


    def test_aggregate_orders(self):
        rows = [
            {
                "order_id": "1001",
                "order_date": "2026-09-01",
                "sku": "ABC",
                "quantity": "2",
                "price": "500",
                "status": "delivered",
            },
            {
                "order_id": "1002",
                "order_date": "2026-09-01",
                "sku": "ABC",
                "quantity": "",
                "price": "500",
                "status": "cancelled",
            },
            {
                "order_id": "1003",
                "order_date": "2026-09-01",
                "sku": "ABC",
                "quantity": "3",
                "price": "500",
                "status": "delivered",
            },
        ]

        groups = aggregate_orders(rows)
        group = groups[("ABC", "2026-09-01")]

        self.assertEqual(len(group["order_ids"]), 3)
        self.assertEqual(group["revenue"], 2500)


    def test_conflicting_orders(self):
        first_order = {
            "order_id": "1001",
            "order_date": "2026-09-01",
            "sku": "ABC",
            "quantity": "2",
            "price": "500",
            "status": "delivered",
        }

        second_order = first_order.copy()
        second_order["quantity"] = "3"

        with self.assertRaises(ValueError):
            clean_orders([first_order, second_order])


    def test_save_report(self):
        groups = {
            ("SKU-B", "2026-09-02"): {
                "order_ids": {"1003"},
                "revenue": 200,
            },
            ("SKU-A", "2026-09-02"): {
                "order_ids": {"1002"},
                "revenue": 0,
            },
            ("SKU-A", "2026-09-01"): {
                "order_ids": {"1001", "1004"},
                "revenue": 800,
            },
        }

        with TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "daily_by_sku.csv"

            save_report(groups, output_file)

            self.assertTrue(output_file.exists())

            with output_file.open(
                "r", encoding="utf-8", newline=""
            ) as file:
                reader = csv.DictReader(file)
                fieldnames = reader.fieldnames
                rows = list(reader)

            self.assertEqual(
                fieldnames,
                ["sku", "order_date", "orders", "revenue"]
            )

            self.assertEqual(rows, [
                {
                    "sku": "SKU-A",
                    "order_date": "2026-09-01",
                    "orders": "2",
                    "revenue": "800",
                },
                {
                    "sku": "SKU-A",
                    "order_date": "2026-09-02",
                    "orders": "1",
                    "revenue": "0",
                },
                {
                    "sku": "SKU-B",
                    "order_date": "2026-09-02",
                    "orders": "1",
                    "revenue": "200",
                },
            ])



if __name__ == "__main__":
    unittest.main()
