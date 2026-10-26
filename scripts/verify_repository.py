"""Check portable project integrity without executing SQL Server or SSIS."""
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DTS = "{www.microsoft.com/SqlServer/Dts}"
SSIS = "{www.microsoft.com/SqlServer/SSIS}"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest_stream(stream):
    digest = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def clean_xml(data, label):
    text = data.decode("utf-8-sig")
    require("AQAAANCMnd8" not in text, f"Encrypted credential payload remains in {label}")
    require("PasswordVerifier" not in text, f"Password verifier remains in {label}")
    root = ET.fromstring(text)
    require(not root.findall(".//" + DTS + "Password"), f"Password element remains in {label}")
    for param in root.iter(SSIS + "Parameter"):
        if "password" in param.get(SSIS + "Name", "").lower():
            values = [p.text for p in param.iter(SSIS + "Property") if p.get(SSIS + "Name") == "Value"]
            require(not any(values), f"Password parameter has a stored value in {label}")
    return root


def main():
    package = clean_xml((ROOT / "ssis/Assignment1/Package.dtsx").read_bytes(), "canonical package")
    require(package.get(DTS + "VersionBuild") == "101", "Canonical package must be build 101")
    require(package.get(DTS + "ProtectionLevel") == "0", "Canonical package must use DontSaveSensitive")
    tasks = package.findall("./" + DTS + "Executables/" + DTS + "Executable")
    require({t.get(DTS + "ObjectName") for t in tasks} == {"DimCustomer", "DimDate", "DimProduct", "DimSeller", "FactSales"}, "Missing SSIS task")
    for task in tasks:
        expected = "False" if task.get(DTS + "ObjectName") == "FactSales" else "True"
        require(task.get(DTS + "Disabled", "False") == expected, "Saved task state changed")
    project = clean_xml((ROOT / "ssis/Assignment1/Assignment1.dtproj").read_bytes(), "project")
    require(project.find(".//TargetServerVersion").text == "SQLServer2025", "Unexpected project target")
    require(all(p.get(SSIS + "ProtectionLevel") == "DontSaveSensitive" for p in project.iter(SSIS + "Project")), "Project protection mismatch")
    for path in (ROOT / "ssis/Assignment1").glob("*"):
        if path.suffix in (".database", ".params"):
            clean_xml(path.read_bytes(), path.name)
    with zipfile.ZipFile(ROOT / "archive/ssis-v99/Assignment1.ispac") as archive:
        old = clean_xml(archive.read("Package.dtsx"), "archived package")
        require(old.get(DTS + "VersionBuild") == "99", "Archived package must be build 99")
        require(old.get(DTS + "ProtectionLevel") == "0", "Archived package protection mismatch")
        manifest = clean_xml(archive.read("@Project.manifest"), "archived manifest")
        require(manifest.get(SSIS + "ProtectionLevel") == "DontSaveSensitive", "Archived manifest protection mismatch")
    print("SSIS XML and archive parsed; credentials removed; versions, target and task states checked")

    folder = ROOT / "data/source"
    expected = {line.split()[1]: line.split()[0] for line in (folder / "SHA256SUMS").read_text().splitlines()}
    source = folder / "ozmart-source.bak.gz"
    with source.open("rb") as stream:
        require(digest_stream(stream) == expected[source.name], "Compressed backup checksum mismatch")
    with gzip.open(source, "rb") as stream:
        require(digest_stream(stream) == expected["ozmart_db_bism7233.bak"], "Source backup payload checksum mismatch")
    print("Compressed and uncompressed source backup SHA-256 verified")

    for name, count in {"Age_Table.csv":78, "Customer_Education.csv":6, "seller_location.csv":100, "State_code.csv":8}.items():
        with (ROOT / "data/reference" / name).open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        require(len(rows) == count, f"Unexpected row count in {name}")
        if name == "seller_location.csv":
            locations = {}
            for row in rows:
                locations.setdefault(row["location_id"], set()).add(row["state"])
            require(len(locations) == 99, "Seller location distinct-key count changed")
            conflicts = {key: sorted(values) for key, values in locations.items() if len(values) > 1}
            require(conflicts == {"ece22fa5b9e06f5b": ["TAS", "WA"]}, "Seller ambiguity profile changed")
    print("Four original CSV profiles verified, including the conflicting seller location")

    inventory = json.loads((ROOT / "docs/evidence/input-inventory.json").read_text())
    require(len(inventory) == 17, "Input inventory must cover all 17 supplied files")
    for item in inventory:
        target = item["repository_location"]
        if target.startswith("Excluded:"):
            continue
        path = ROOT / target.split(" (", 1)[0]
        require(path.is_file(), f"Missing inventoried file: {target}")
        if " (" not in target:
            require(hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256_original"], f"Original file changed: {target}")
    print("All 17 input dispositions checked; unchanged public inputs match their original SHA-256")

    broken = []
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        for target in re.findall(r"!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            destination = unquote(target.split("#", 1)[0])
            if destination and not (path.parent / destination).exists():
                broken.append(f"{path.relative_to(ROOT)} -> {destination}")
    require(not broken, "Broken local links:\n" + "\n".join(broken))
    print("All local Markdown file and image link targets exist")


if __name__ == "__main__":
    main()
