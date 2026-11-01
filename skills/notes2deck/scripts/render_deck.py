#!/usr/bin/env python3
"""Render PPTX or PDF slides to a normalized PDF and numbered PNG pages."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"Required tool not found: {name}")
    return path


def convert_to_pdf(source: Path, destination: Path) -> None:
    if source.suffix.lower() == ".pdf":
        if source != destination:
            shutil.copy2(source, destination)
        return
    if source.suffix.lower() != ".pptx":
        raise RuntimeError("Supported inputs are .pptx and .pdf.")
    soffice = require_tool("soffice")
    with tempfile.TemporaryDirectory(prefix="slides-render-") as temp_name:
        temp_dir = Path(temp_name)
        profile = (temp_dir / "lo-profile").as_uri()
        subprocess.run(
            [
                soffice,
                "--headless",
                f"-env:UserInstallation={profile}",
                "--convert-to",
                "pdf",
                "--outdir",
                str(temp_dir),
                str(source),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        produced = temp_dir / f"{source.stem}.pdf"
        if not produced.is_file():
            raise RuntimeError("LibreOffice did not produce the expected PDF.")
        shutil.copy2(produced, destination)


def page_count(pdf: Path) -> int:
    pdfinfo = require_tool("pdfinfo")
    result = subprocess.run([pdfinfo, str(pdf)], check=True, capture_output=True, text=True)
    match = re.search(r"^Pages:\s+(\d+)", result.stdout, flags=re.MULTILINE)
    if not match:
        raise RuntimeError("Could not determine rendered PDF page count.")
    return int(match.group(1))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--dpi", type=int, default=160)
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    if not source.is_file():
        parser.error(f"Input does not exist: {source}")
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    normalized_pdf = output_dir / "source.pdf"
    convert_to_pdf(source, normalized_pdf)

    pdftoppm = require_tool("pdftoppm")
    count = page_count(normalized_pdf)
    with tempfile.TemporaryDirectory(prefix="slides-pages-") as temp_name:
        prefix = Path(temp_name) / "page"
        subprocess.run(
            [pdftoppm, "-png", "-r", str(args.dpi), str(normalized_pdf), str(prefix)],
            check=True,
            capture_output=True,
            text=True,
        )
        rendered = sorted(
            Path(temp_name).glob("page-*.png"),
            key=lambda item: int(item.stem.rsplit("-", 1)[-1]),
        )
        if len(rendered) != count:
            raise RuntimeError(f"Expected {count} page images, found {len(rendered)}.")
        width = max(3, len(str(count)))
        pages = []
        for index, image in enumerate(rendered, start=1):
            target = output_dir / f"slide-{index:0{width}d}.png"
            shutil.copy2(image, target)
            pages.append({"slide_number": index, "image": str(target)})

    manifest_path = output_dir / "render-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {"source": str(source), "source_pdf": str(normalized_pdf), "dpi": args.dpi, "pages": pages},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"output_dir": str(output_dir), "pages": count, "source_pdf": str(normalized_pdf)}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)

