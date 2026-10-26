# Supplied reference CSV files

These are unchanged case inputs used by the SSIS flat-file managers.

| File | Data rows | Purpose |
| --- | --- | --- |
| `Age_Table.csv` | 78 | Age key to age description |
| `Customer_Education.csv` | 6 | Education ID to education level |
| `seller_location.csv` | 100 | Seller location attributes, including state |
| `State_code.csv` | 8 | Australian state and territory codes and full names |

The seller-location file contains 99 distinct location IDs and one ID with conflicting TAS/WA states. Read the [quality case](../../docs/data-quality.md) before replacing that reference with a first-match lookup. File row counts exclude headers. BOM-aware UTF-8 decoding is used by the verification script.

These are supplied teaching materials; see [usage and provenance](../../NOTICE.md).
