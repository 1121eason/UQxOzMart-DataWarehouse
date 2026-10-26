# Run the OzMart project

Two execution paths are available. The portable synthetic demo runs with Python and SQLite. The original SSIS path requires a Windows SQL Server development environment and local connection configuration.

## Portable demonstration

Use Python 3.10 or newer with SQLite 3.25 or newer. No third-party Python packages are required.

```bash
git clone https://github.com/1121eason/UQxOzMart-DataWarehouse.git
cd UQxOzMart-DataWarehouse
python scripts/verify_repository.py
python scripts/run_demo.py
python -m unittest discover -s tests -v
```

The demo writes a SQLite warehouse, six analytical CSV files and a control summary to `demo/output/`. Its controls are **13 order lines, 43 units and 1,680.00 revenue**. All rows are synthetic. Read the [demo notes](../demo/README.md) before comparing its results to the historical report.

## SQL Server and SSIS prerequisites

The supplied project sets `TargetServerVersion` to **SQLServer2025**. Use Visual Studio with an SSIS Projects extension that can open that target and a compatible SQL Server/SSIS environment. Use SQL Server Management Studio for restore, table creation and queries. The package uses ADO.NET database sources/destinations and OLE DB lookups. Its stored OLE DB provider is `SQLNCLI11.1`.

If the required target or provider is unavailable, review the target and connection providers in the SSIS designer and refresh affected metadata. That migration is environment-specific and has not been validated here. This repository does not include a fresh Visual Studio build or a target-version compatibility test.

## Restore the source database

The 112,320,512-byte attachment `ozmart_db_bism7233` is a SQL Server **source database backup**. Its lossless gzip copy is in [data/source](../data/source/README.md). It is not a backup of the completed warehouse. `Assignment1.database` is Visual Studio XML metadata and cannot be restored as a relational database backup.

Run the integrity check, then unpack the backup without changing the compressed copy:

```bash
python scripts/verify_repository.py
python scripts/unpack_source.py
```

The second command writes `data/source/ozmart_db_bism7233.bak` and refuses to overwrite an existing file. In SSMS, inspect the backup header and file list, then restore it as `ozmart_db` using data/log paths appropriate for your SQL Server host. The backup file must be accessible to the SQL Server service account. Review any existing database of that name before restoring.

The gzip payload and its SHA-256 are verified by the repository check. No database restore was performed during portfolio preparation, so engine-version compatibility and database contents still require validation in SQL Server.

## Create the warehouse

Open [01_create_warehouse.sql](../sql/setup/01_create_warehouse.sql) in SSMS. Review the target database name `ozmart_dw`, then run it. The script creates the database if absent and creates five tables with constraints and indexes. It stops if a target table already exists and does not drop or truncate data.

The DDL reconstructs target columns and types from SSIS metadata. Constraints, indexes and identity generation are new design choices. After creating the tables, refresh destination metadata in the SSIS designer if needed and ensure surrogate key columns are not populated by the input streams.

## Configure and execute SSIS

1. Open [Assignment1.dtproj](../ssis/Assignment1/Assignment1.dtproj), then `Package.dtsx`.
2. Configure both source-database connection managers to your restored `ozmart_db` and both target managers to `ozmart_dw`. The public source defaults to local integrated authentication. Supply your own credentials through the local environment if needed. Keep `DontSaveSensitive` when saving shared files.
3. Set each flat-file manager to its actual local file: `Age_Table.csv`, `Customer_Education.csv`, `seller_location.csv` and `State_code.csv` under `data/reference/`. Relative paths in the public package are starting values; SSIS working directories can differ.
4. Enable `DimCustomer`, `DimDate`, `DimProduct` and `DimSeller`. They are disabled in the original saved package. Review all four success constraints into `FactSales` and keep the fact load after its dimensions.
5. Run against a fresh warehouse. Inspect transformation counts, lookup outcomes, warning messages and destinations. These are append loads with no incremental or reload logic.
6. Run [warehouse checks](../sql/validation/01_warehouse_checks.sql), then [source reconciliation](../sql/validation/02_source_reconciliation.sql). Investigate differences before analysing results.
7. Run the [analytical SQL](../sql/analytics/) in the `ozmart_dw` query context. Read the [metric definitions](analytics/business-questions.md) when interpreting state, age, quantity and revenue.

Build a new ISPAC in Visual Studio only after connection and metadata checks pass. The [archived ISPAC](../archive/ssis-v99/README.md) is an earlier sanitised artifact; it is not the deployment build for v101.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Package will not open or build | SSIS extension support for the saved SQLServer2025 target |
| Flat file cannot be found | Set an absolute path in the relevant connection manager |
| Database login fails | Source/target instance, database and local authentication settings |
| OLE DB provider unavailable | Review `SQLNCLI11.1` connection settings in the designer |
| Fact lookup cannot resolve a key | Load dimensions first; check source IDs and date-only `FullDate` |
| Duplicate-key error | Review existing target rows and previous partial/full loads |
| Seller state name is null | Review the location ambiguity and missing state-reference mapping |

The [validation record](validation.md) separates local demo checks from historical SSIS evidence and outstanding native-tool validation.
