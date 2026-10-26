"""Verify and decompress the supplied source backup without overwriting a file."""
import gzip
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / "data" / "source"
    expected = {line.split()[1]: line.split()[0] for line in (folder / "SHA256SUMS").read_text().splitlines()}
    source = folder / "ozmart-source.bak.gz"
    target = folder / "ozmart_db_bism7233.bak"
    if hashlib.sha256(source.read_bytes()).hexdigest() != expected[source.name]:
        raise ValueError("Compressed source checksum does not match")
    digest = hashlib.sha256()
    with gzip.open(source, "rb") as stream, target.open("xb") as output:
        try:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                output.write(chunk)
                digest.update(chunk)
            if digest.hexdigest() != expected[target.name]:
                raise ValueError("Uncompressed source checksum does not match")
        except BaseException:
            output.close()
            target.unlink(missing_ok=True)
            raise
    print(f"Verified source backup written to {target}")


if __name__ == "__main__":
    main()
