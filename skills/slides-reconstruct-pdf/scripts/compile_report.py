#!/usr/bin/env python3
"""Compile a reconstruction LaTeX document and verify the resulting PDF."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def page_count(pdf: Path) -> int:
    pdfinfo = shutil.which("pdfinfo")
    if not pdfinfo:
        return 0
    result = subprocess.run([pdfinfo, str(pdf)], check=True, capture_output=True, text=True)
    match = re.search(r"^Pages:\s+(\d+)", result.stdout, flags=re.MULTILINE)
    return int(match.group(1)) if match else 0


def compile_tex(tex: Path, build_dir: Path, cache_dir: Path) -> Path:
    tectonic = shutil.which("tectonic")
    if tectonic:
        cache_dir.mkdir(parents=True, exist_ok=True)
        environment = os.environ.copy()
        environment["TECTONIC_CACHE_DIR"] = str(cache_dir)
        environment["XDG_CACHE_HOME"] = str(cache_dir)
        subprocess.run(
            [tectonic, str(tex), "--outdir", str(build_dir), "--keep-logs"],
            cwd=tex.parent,
            check=True,
            env=environment,
        )
        return build_dir / f"{tex.stem}.pdf"

    xelatex = shutil.which("xelatex")
    if xelatex:
        command = [
            xelatex,
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={build_dir}",
            str(tex),
        ]
        subprocess.run(command, cwd=tex.parent, check=True)
        subprocess.run(command, cwd=tex.parent, check=True)
        return build_dir / f"{tex.stem}.pdf"

    raise RuntimeError("Neither tectonic nor xelatex is available.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tex", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    tex = args.tex.expanduser().resolve()
    if not tex.is_file():
        parser.error(f"LaTeX source does not exist: {tex}")
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="slides-report-") as temp_name:
        built_pdf = compile_tex(tex, Path(temp_name), output.parent / ".tectonic-cache")
        if not built_pdf.is_file() or built_pdf.stat().st_size == 0:
            raise RuntimeError("LaTeX compiler did not produce a non-empty PDF.")
        shutil.copy2(built_pdf, output)

    pages = page_count(output)
    print(json.dumps({"output": str(output), "bytes": output.stat().st_size, "pages": pages}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
