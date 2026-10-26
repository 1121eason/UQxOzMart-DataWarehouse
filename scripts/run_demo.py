"""Build a small synthetic star schema and execute the repository's analytical SQL.

This portable demo does not restore the supplied source backup or execute SSIS.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "demo" / "fixtures"
STATES = {
    "ACT": "Australian Capital Territory", "NSW": "New South Wales",
    "NT": "Northern Territory", "QLD": "Queensland", "SA": "South Australia",
    "TAS": "Tasmania", "VIC": "Victoria", "WA": "Western Australia",
}
SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE DimCustomer (
    CustomerKEY INTEGER PRIMARY KEY, customer_id TEXT NOT NULL UNIQUE,
    Age TEXT, Education_level TEXT, state_name TEXT);
CREATE TABLE DimDate (
    DateKEY INTEGER PRIMARY KEY, Day INTEGER, Month INTEGER, Year INTEGER,
    FullDate TEXT NOT NULL UNIQUE);
CREATE TABLE DimProduct (
    ProductKEY INTEGER PRIMARY KEY, product_id TEXT NOT NULL UNIQUE,
    product_name TEXT, poduct_descriptions TEXT, product_subcategorey_id TEXT,
    Product_Category_ID TEXT, Product_Subcategory TEXT, Product_Category TEXT);
CREATE TABLE DimSeller (
    SellerKEY INTEGER PRIMARY KEY, state TEXT, name TEXT,
    seller_id TEXT NOT NULL UNIQUE, state_name TEXT);
CREATE TABLE FactSales (
    order_item_id TEXT PRIMARY KEY NOT NULL,
    ProductKEY INTEGER NOT NULL REFERENCES DimProduct(ProductKEY),
    SellerKEY INTEGER NOT NULL REFERENCES DimSeller(SellerKEY),
    CustomerKEY INTEGER NOT NULL REFERENCES DimCustomer(CustomerKEY),
    Revenue REAL NOT NULL, QuantitySold INTEGER NOT NULL,
    DateKEY INTEGER NOT NULL REFERENCES DimDate(DateKEY));
"""


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def unique_index(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    result = {}
    for row in rows:
        value = row[key]
        if not value or value in result:
            raise ValueError(f"Missing or duplicate {key}: {value!r}")
        result[value] = row
    return result


def seller_states(locations: list[dict[str, str]]) -> dict[str, str]:
    grouped: dict[str, set[str]] = {}
    for row in locations:
        grouped.setdefault(row["location_id"], set()).add(row["state"])
    return {
        key: next(iter(values)) if len(values) == 1 and next(iter(values)) in STATES else "Unknown"
        for key, values in grouped.items()
    }


def build_warehouse(fixtures: Path = FIXTURES) -> tuple[sqlite3.Connection, dict]:
    inputs = {name: read_csv(fixtures / f"{name}.csv") for name in (
        "customers", "products", "sellers", "seller_locations", "orders", "order_items")}
    customers = unique_index(inputs["customers"], "customer_id")
    products = unique_index(inputs["products"], "product_id")
    sellers = unique_index(inputs["sellers"], "seller_id")
    orders = unique_index(inputs["orders"], "order_id")
    unique_index(inputs["order_items"], "order_item_id")
    for row in customers.values():
        int(row["Age"])  # Numeric ages are a prerequisite of the ranking tie-break.
    dates = sorted({datetime.fromisoformat(row["purchase_timestamp"]).date() for row in orders.values()})
    states = seller_states(inputs["seller_locations"])
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    try:
        with conn:
            for key, row in sorted(customers.items()):
                conn.execute("INSERT INTO DimCustomer(customer_id, Age, Education_level, state_name) VALUES (?, ?, ?, ?)",
                             (key, row["Age"], row["Education_level"], row["state_name"]))
            for day in dates:
                conn.execute("INSERT INTO DimDate(Day, Month, Year, FullDate) VALUES (?, ?, ?, ?)",
                             (day.day, day.month, day.year, day.isoformat()))
            for key, row in sorted(products.items()):
                conn.execute("INSERT INTO DimProduct(product_id, product_name, Product_Category, Product_Subcategory) VALUES (?, ?, ?, ?)",
                             (key, row["product_name"], row["Product_Category"], row["Product_Subcategory"]))
            for key, row in sorted(sellers.items()):
                state = states.get(row["location_id"], "Unknown")
                conn.execute("INSERT INTO DimSeller(seller_id, name, state, state_name) VALUES (?, ?, ?, ?)",
                             (key, row["name"], state, STATES.get(state, "Unknown")))
            customer_keys = dict(conn.execute("SELECT customer_id, CustomerKEY FROM DimCustomer"))
            product_keys = dict(conn.execute("SELECT product_id, ProductKEY FROM DimProduct"))
            seller_keys = dict(conn.execute("SELECT seller_id, SellerKEY FROM DimSeller"))
            date_keys = dict(conn.execute("SELECT FullDate, DateKEY FROM DimDate"))
            for row in inputs["order_items"]:
                try:
                    order = orders[row["order_id"]]
                    day = datetime.fromisoformat(order["purchase_timestamp"]).date().isoformat()
                    revenue = Decimal(row["line_total"])
                    if not revenue.is_finite():
                        raise ValueError("line_total must be finite")
                    quantity = int(row["item_quantity"])
                    if not -32768 <= quantity <= 32767:
                        raise ValueError("item_quantity exceeds original SMALLINT range")
                    values = (row["order_item_id"], product_keys[row["product_id"]],
                              seller_keys[row["seller_id"]], customer_keys[order["customer_id"]],
                              float(revenue), quantity, date_keys[day])
                except (KeyError, ValueError, InvalidOperation) as error:
                    raise ValueError(f"Invalid order line {row['order_item_id']}: {error}") from error
                conn.execute("INSERT INTO FactSales VALUES (?, ?, ?, ?, ?, ?, ?)", values)
        if conn.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Foreign key validation failed")
        total = conn.execute("SELECT COUNT(*) AS order_lines, SUM(QuantitySold) AS units, SUM(Revenue) AS revenue FROM FactSales").fetchone()
        summary = {
            "dataset": "synthetic portfolio fixtures",
            "order_lines": total["order_lines"], "units": total["units"], "revenue": total["revenue"],
            "dimension_rows": {table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                               for table in ("DimCustomer", "DimDate", "DimProduct", "DimSeller")},
            "unknown_sellers": conn.execute("SELECT COUNT(*) FROM DimSeller WHERE state = 'Unknown'").fetchone()[0],
        }
        return conn, summary
    except Exception:
        conn.close()
        raise


def run_analytics(conn: sqlite3.Connection, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for path in sorted((ROOT / "sql" / "analytics").glob("*.sql")):
        result = conn.execute(path.read_text(encoding="utf-8"))
        with (output / f"{path.stem}.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow([col[0] for col in result.description])
            writer.writerows(result.fetchall())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=FIXTURES)
    parser.add_argument("--output", type=Path, default=ROOT / "demo" / "output")
    args = parser.parse_args()
    conn, summary = build_warehouse(args.fixtures)
    try:
        run_analytics(conn, args.output)
        (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        destination = sqlite3.connect(args.output / "ozmart-demo.sqlite")
        try:
            conn.backup(destination)
        finally:
            destination.close()
        print(json.dumps(summary, indent=2))
        print(f"Six analytical CSV files and a SQLite warehouse saved to {args.output}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
