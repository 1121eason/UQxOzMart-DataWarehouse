# Supplied SQL Server source backup

`ozmart-source.bak.gz` is a lossless gzip copy of the supplied `ozmart_db_bism7233` attachment. The original is **112,320,512 bytes**; the compressed copy is **24,892,461 bytes**. It is the operational source backup, not a backup of the completed star schema.

`SHA256SUMS` contains hashes for both the compressed file and the uncompressed payload. Run these commands from the repository root:

```bash
python scripts/verify_repository.py
python scripts/unpack_source.py
```

The unpacked `ozmart_db_bism7233.bak` is ignored by Git. The unpacking script refuses to overwrite an existing file. Restore through SQL Server after inspecting the backup and choosing local database-file paths. Follow the [setup guide](../../docs/setup.md).

Compression and checksum verification establish file integrity. They do not establish SQL Server restore compatibility or a successful database restore. No completed warehouse backup was supplied. Refer to [usage and provenance](../../NOTICE.md) before reusing the case dataset.
