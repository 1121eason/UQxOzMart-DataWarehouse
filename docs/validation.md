# Validation status

Portfolio checks were performed locally on **26 October 2026**. The portable demonstration uses synthetic fixtures. Historical SSIS screenshots and current local checks describe different execution environments.

| Check | Result | Scope |
| --- | --- | --- |
| Python demo | Passed | Creates a SQLite warehouse and executes all six analytical SQL files |
| Behavioural tests | 13 passed | Totals, grain, ranking ties, namesakes, geography, shares, missing keys, duplicate IDs and invalid numeric inputs |
| Synthetic controls | 13 lines, 43 units, 1,680.00 revenue | Five customers, six dates, six products and five sellers |
| SSIS XML and ISPAC inspection | Passed | Canonical build 101, archived build 99, saved task states and sensitive-value removal |
| Source backup integrity | Passed | Compressed and uncompressed SHA-256 match the supplied source file |
| Reference-file profiling | Passed | Four CSV counts; 100 seller-location rows, 99 distinct IDs, one TAS/WA conflict |
| Input preservation | Passed | All 17 supplied inputs have documented destinations or exclusions; unchanged files match original hashes |
| Local documentation links | Passed | All linked repository files and images exist |
| SQL Server source restore | Not run | Requires a compatible SQL Server environment |
| Reconstructed SQL Server DDL and reconciliation | Not run | SQLite demo does not validate SQL Server engine behaviour |
| Visual Studio build and SSIS execution | Not run | Requires compatible Windows SSIS tooling and configured connections |
| Production deployment or BI dashboard | Outside implemented scope | Academic warehouse prototype |

## Reproduce the completed local checks

```bash
python scripts/verify_repository.py
python scripts/run_demo.py
python -m unittest discover -s tests -v
```

An optional [GitHub Actions template](examples/github-actions-validate.yml) contains the same checks for pushes and pull requests. Automatic hosted validation is not enabled in this repository. To enable it later, copy the template to `.github/workflows/validate.yml` using GitHub credentials permitted to create workflows.

The [original evidence register](evidence/README.md) explains which artifacts came from the assignment and which were added for the portfolio. Use [setup](setup.md) to perform the remaining native SQL Server and SSIS checks.
