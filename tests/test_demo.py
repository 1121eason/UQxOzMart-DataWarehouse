import csv
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_demo", ROOT / "scripts" / "run_demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class WarehouseTests(unittest.TestCase):
    def setUp(self):
        self.conn, self.summary = demo.build_warehouse()

    def tearDown(self):
        self.conn.close()

    def query(self, name):
        return [dict(row) for row in self.conn.execute((ROOT / "sql" / "analytics" / name).read_text())]

    def test_independent_control_totals_and_grain(self):
        self.assertEqual(self.summary["order_lines"], 13)
        self.assertEqual(self.summary["units"], 43)
        self.assertAlmostEqual(self.summary["revenue"], 1680.0)
        self.assertEqual(self.summary["dimension_rows"], {"DimCustomer": 5, "DimDate": 6, "DimProduct": 6, "DimSeller": 5})
        self.assertEqual(self.conn.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_revenue_tie_uses_numeric_age(self):
        rows = self.query("01_top_customer_age_by_state.sql")
        winner = next(r for r in rows if r["state_name"] == "Queensland")
        self.assertEqual(winner["MostImportantCustomerAge"], "25")
        self.assertAlmostEqual(winner["TotalRevenue"], 420.0)

    def test_product_top_five_and_customer_geography(self):
        rows = self.query("02_top_product_types_by_state.sql")
        qld = [r for r in rows if r["state_name"] == "Queensland"]
        self.assertEqual(len(qld), 5)
        self.assertEqual(qld[0]["Product_Subcategory"], "Hobbies")
        self.assertEqual(qld[0]["TotalQuantitySold"], 13)
        self.assertNotIn("Pretend Play", [r["Product_Subcategory"] for r in qld])

    def test_nsw_suppliers_keep_namesakes_and_cross_state_sales(self):
        rows = self.query("03_top_nsw_suppliers_by_year.sql")
        year = [r for r in rows if r["Year"] == 2022]
        self.assertEqual([(r["seller_id"],r["TotalQuantitySold"]) for r in year], [("S001",11),("S002",7)])
        self.assertEqual(len({r["SupplierName"] for r in year}), 1)
        self.assertEqual({r["Year"] for r in rows}, {2022,2023})

    def test_uncertain_and_missing_seller_locations(self):
        rows = dict(self.conn.execute("SELECT seller_id, state FROM DimSeller"))
        self.assertEqual(rows["S004"], "Unknown")
        self.assertEqual(rows["S005"], "Unknown")
        self.assertEqual(rows["S003"], "QLD")
        self.assertEqual(self.summary["unknown_sellers"], 2)

    def test_monthly_totals_reconcile_to_facts(self):
        rows = self.query("04_monthly_state_sales.sql")
        self.assertEqual(sum(r["OrderLines"] for r in rows),13)
        self.assertEqual(sum(r["UnitsSold"] for r in rows),43)
        self.assertAlmostEqual(sum(r["Revenue"] for r in rows),1680.0)

    def test_supplier_shares_sum_to_one_hundred_by_year(self):
        rows = self.query("05_nsw_supplier_concentration.sql")
        for year in (2022,2023):
            group = [r for r in rows if r["Year"] == year]
            self.assertAlmostEqual(sum(r["UnitSharePct"] for r in group),100.0)
            self.assertAlmostEqual(group[-1]["CumulativeUnitSharePct"],100.0)
        self.assertAlmostEqual(rows[0]["UnitSharePct"],100.0*11/18)

    def test_age_revenue_shares_use_state_totals(self):
        rows = self.query("06_customer_age_revenue_share.sql")
        qld = [r for r in rows if r["state_name"] == "Queensland"]
        self.assertEqual([r["RevenueSharePct"] for r in qld],[50.0,50.0])
        for state in {r["state_name"] for r in rows}:
            self.assertAlmostEqual(sum(r["RevenueSharePct"] for r in rows if r["state_name"]==state),100.0)

    def test_all_analytical_exports_match_saved_examples(self):
        with tempfile.TemporaryDirectory() as path:
            output = Path(path)
            demo.run_analytics(self.conn,output)
            for expected in (ROOT / "demo" / "expected").glob("*.csv"):
                with self.subTest(expected=expected.name):
                    self.assertEqual((output/expected.name).read_text(),expected.read_text())
            self.assertEqual(self.summary,json.loads((ROOT / "demo" / "expected" / "summary.json").read_text()))


class InvalidInputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.fixtures = Path(self.temp.name) / "fixtures"
        shutil.copytree(demo.FIXTURES,self.fixtures)

    def tearDown(self):
        self.temp.cleanup()

    def change_first_line(self, **changes):
        path = self.fixtures / "order_items.csv"
        rows = demo.read_csv(path)
        rows[0].update(changes)
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream,fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    def test_duplicate_line_id_is_rejected(self):
        self.change_first_line(order_item_id="I002")
        with self.assertRaisesRegex(ValueError,"duplicate order_item_id"):
            demo.build_warehouse(self.fixtures)

    def test_unresolved_product_is_rejected(self):
        self.change_first_line(product_id="MISSING")
        with self.assertRaisesRegex(ValueError,"Invalid order line I001"):
            demo.build_warehouse(self.fixtures)

    def test_non_finite_revenue_is_rejected(self):
        self.change_first_line(line_total="NaN")
        with self.assertRaisesRegex(ValueError,"finite"):
            demo.build_warehouse(self.fixtures)

    def test_quantity_overflow_is_rejected(self):
        self.change_first_line(item_quantity="32768")
        with self.assertRaisesRegex(ValueError,"SMALLINT"):
            demo.build_warehouse(self.fixtures)


if __name__ == "__main__":
    unittest.main()
