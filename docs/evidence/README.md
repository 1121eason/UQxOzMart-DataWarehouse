# Original evidence and portfolio additions

The original work is preserved so readers can inspect the implementation behind the portfolio narrative. The [PDF report](ozmart-original-report.pdf) and [editable report](ozmart-original-report.docx) are byte-for-byte copies of the supplied submission. Their screenshots record historical activity.

| Material | Provenance | How to interpret it |
| --- | --- | --- |
| `ssis/Assignment1/Package.dtsx` | Supplied loose package, `VersionBuild=101` | Canonical pipeline logic, with credentials removed and local configuration made portable |
| `archive/ssis-v99/Assignment1.ispac` | Supplied build artifact, package build 99 | Sanitised earlier version; not a fresh build of v101 |
| Original report PDF and DOCX | Supplied assignment report | Original design rationale, flow screenshots and query results |
| `docs/assets/etl-*.png` and result images | Extracted original DOCX media | Historical flow and result evidence, unchanged image content |
| `docs/assets/source-erd.png` | Supplied operational ERD | Source relationships, not the warehouse schema |
| `data/reference/` and `docs/reference/` | Supplied case files | Course reference data, dictionary and assignment brief |
| `data/source/ozmart-source.bak.gz` | Supplied 112,320,512-byte source backup | Losslessly compressed original source, not a warehouse backup |
| `sql/setup/` | New portfolio reconstruction | Column types from SSIS metadata, with added constraints and indexes |
| `sql/original/` | SQL transcribed from the report | Original query logic, including its original tie/name grouping behaviour |
| `sql/analytics/` | Refined core queries and three new extensions | Deterministic ordering and stable supplier grouping; run on synthetic fixtures |
| `demo/`, scripts and tests | New portfolio additions | Executable synthetic illustration of key resolution and analysis |
| README and technical guides | New portfolio documentation | Evidence-based explanation of design and engineering decisions |

## Input coverage

[input-inventory.json](input-inventory.json) records all 17 supplied input files, their original byte sizes, SHA-256 hashes and repository destinations. The SSIS user-settings file is intentionally excluded because it is machine-specific. Build caches and operating-system metadata are not project source.

The supplied original report, case brief, source dictionary, ERD and four CSVs are retained. The course brief's instructions describe the original assessment; they do not expand the user's request or govern the portfolio packaging task.

## Sanitisation and version handling

The public SSIS source and archived ISPAC remove stored encrypted password elements and password verifiers. Protection is set to `DontSaveSensitive`. The target catalogue is renamed from the student-specific local name to `ozmart_dw`, database connections use local integrated authentication, CSV defaults point toward the repository's reference folder, and creator-machine metadata is generic. No data-flow logic or saved enabled/disabled state is changed.

The `.dtproj` cached package build number is aligned from 74 to 101 to identify the canonical loose package. This is a metadata correction, not a Visual Studio rebuild. The build-99 ISPAC is archived rather than presented as current. It was repackaged after sanitisation, so its hash differs from the original input.

## Evidence limits

The fact-flow screenshot shows 137,901 rows through its lookup path and a historical execution success message. The date screenshot shows 25,000 source rows reduced to 493 dates. These counts describe the historical run and were not remeasured from a restored database.

The original completed warehouse backup and exported warehouse DDL were not among the supplied files. Accordingly, fresh SQL Server restore, reconstructed DDL execution, Visual Studio build and SSIS execution remain unverified. The Python demo validates its own synthetic dataset and analytical queries only. See [validation status](../validation.md) for completed checks.
