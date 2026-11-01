#!/usr/bin/env python3
"""Extract packaged PPTX media and embedded files without executing them."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path


PREFIXES = ("ppt/media/", "ppt/embeddings/")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    if source.suffix.lower() != ".pptx":
        parser.error("Asset extraction requires a .pptx input.")
    if not source.is_file():
        parser.error(f"Input does not exist: {source}")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    try:
        with zipfile.ZipFile(source) as archive:
            for member in sorted(name for name in archive.namelist() if name.startswith(PREFIXES)):
                relative = Path(*Path(member).parts[1:])
                target = output_dir / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                data = archive.read(member)
                target.write_bytes(data)
                records.append(
                    {
                        "archive_path": member,
                        "output": str(target),
                        "bytes": len(data),
                        "sha256": digest(data),
                    }
                )
    except zipfile.BadZipFile as exc:
        print(f"error: invalid PPTX archive: {exc}", file=sys.stderr)
        return 1

    manifest = output_dir / "asset-manifest.json"
    manifest.write_text(json.dumps({"source": str(source), "assets": records}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output_dir": str(output_dir), "assets": len(records)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
