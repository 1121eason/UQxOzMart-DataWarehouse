# Portable warehouse demonstration

Run `python scripts/run_demo.py` from the repository root. The script uses only Python's standard library and SQLite with window functions (SQLite 3.25 or newer). It creates a fresh database under `demo/output/` for each run and executes the six queries in `sql/analytics/` without changing their SQL.

All records in `fixtures/` are **synthetic**, newly authored portfolio examples. They do not represent OzMart's source data or the original report results. The customer and product inputs are deliberately flattened to focus on dimensional keys and analytical behaviour. The original multi-source joins remain in the SSIS project.

The fixture has 13 order lines across 7 orders, with control totals of 43 units and 1,680.00 revenue. Queensland ages 25 and 40 each contribute 420.00, exercising deterministic tie handling. Two NSW suppliers share a display name, so supplier IDs must keep them separate. One location has conflicting states; another is absent. Both become `Unknown` in this demo's seller dimension. Exact duplicate location rows are collapsed.

`expected/` holds the six analytical CSV results and a compact control summary generated from these fixtures. `tests/test_demo.py` checks independent control totals and edge cases as well as the saved expected outputs. `output/` is generated locally and ignored by Git.

The demo makes both seller state fields explicitly `Unknown` for unresolved geography. In the original SSIS package only the short state field is explicitly replaced with `Unknown`; the full state name can remain null after the final reference join. This difference is intentional and documented in [data quality](../docs/data-quality.md).
