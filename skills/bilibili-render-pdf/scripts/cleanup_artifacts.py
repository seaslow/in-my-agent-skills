#!/usr/bin/env python3
"""Clean large intermediate artifacts from a bilibili-render-pdf output dir."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

NEWCOMMAND_RE = re.compile(r"\\newcommand\{\\([A-Za-z@]+)\}\{([^}]*)\}")
INCLUDEGRAPHICS_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}")
GRAPHIC_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg", ".webp")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Remove bulky intermediate artifacts while preserving the final "
            "bilibili-render-pdf note set."
        )
    )
    parser.add_argument("output_dir", help="Output directory produced by bilibili-render-pdf.")
    parser.add_argument(
        "--mode",
        choices=("reproducible", "final-only", "debug"),
        default="reproducible",
        help=(
            "reproducible: keep tex/pdf + referenced assets + metadata/subtitles; "
            "final-only: keep final pdf + metadata/subtitles; "
            "debug: report only and delete nothing."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be deleted without deleting it.",
    )
    return parser.parse_args()


def resolve_output_dir(path_str: str) -> Path:
    path = Path(path_str).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise SystemExit(f"Output directory does not exist or is not a directory: {path}")
    return path


def find_root_tex_files(output_dir: Path) -> list[Path]:
    return sorted(path.resolve() for path in output_dir.glob("*.tex") if path.is_file())


def parse_macros(tex_path: Path) -> dict[str, str]:
    text = tex_path.read_text(encoding="utf-8", errors="ignore")
    return {name: body.strip() for name, body in NEWCOMMAND_RE.findall(text)}


def resolve_graphic_ref(tex_path: Path, token: str, macros: dict[str, str]) -> Path | None:
    candidate = token.strip()
    if not candidate:
        return None
    if candidate.startswith("\\"):
        candidate = macros.get(candidate[1:], candidate).strip()
    if not candidate or candidate.startswith("\\"):
        return None

    base = (tex_path.parent / candidate).resolve()
    if base.exists() and base.is_file():
        return base
    if base.suffix:
        return None
    for ext in GRAPHIC_EXTENSIONS:
        with_ext = base.with_suffix(ext)
        if with_ext.exists() and with_ext.is_file():
            return with_ext.resolve()
    return None


def referenced_assets(tex_path: Path) -> set[Path]:
    text = tex_path.read_text(encoding="utf-8", errors="ignore")
    macros = parse_macros(tex_path)
    keep: set[Path] = set()
    for token in INCLUDEGRAPHICS_RE.findall(text):
        resolved = resolve_graphic_ref(tex_path, token, macros)
        if resolved is not None:
            keep.add(resolved)
    return keep


def build_keep_set(output_dir: Path, mode: str) -> set[Path]:
    keep: set[Path] = set()
    tex_files = find_root_tex_files(output_dir)

    for tex_path in tex_files:
        if mode != "final-only":
            keep.add(tex_path)
        pdf_path = tex_path.with_suffix(".pdf")
        if pdf_path.exists() and pdf_path.is_file():
            keep.add(pdf_path.resolve())
        if mode != "final-only":
            keep.update(referenced_assets(tex_path))

    for pattern in ("*.info.json", "*.srt"):
        for path in output_dir.glob(pattern):
            if path.is_file():
                keep.add(path.resolve())

    keep.add((output_dir / "cleanup-report.json").resolve())
    return keep


def keep_directories(output_dir: Path, keep_files: set[Path]) -> set[Path]:
    output_dir = output_dir.resolve()
    keep_dirs = {output_dir}
    for path in keep_files:
        current = path.resolve().parent
        while True:
            if current == output_dir:
                keep_dirs.add(current)
                break
            if output_dir not in current.parents:
                break
            keep_dirs.add(current)
            current = current.parent
    return keep_dirs


def list_deletions(output_dir: Path, keep_files: set[Path], keep_dirs: set[Path]) -> tuple[list[Path], list[Path]]:
    files_to_delete: list[Path] = []
    dirs_to_delete: list[Path] = []

    for path in output_dir.rglob("*"):
        resolved = path.resolve()
        if path.is_file() or path.is_symlink():
            if resolved not in keep_files:
                files_to_delete.append(resolved)
        elif path.is_dir():
            if resolved not in keep_dirs:
                dirs_to_delete.append(resolved)

    dirs_to_delete.sort(key=lambda path: len(path.parts), reverse=True)
    files_to_delete.sort()
    return files_to_delete, dirs_to_delete


def byte_size(paths: list[Path]) -> int:
    total = 0
    for path in paths:
        try:
            total += path.stat().st_size
        except FileNotFoundError:
            continue
    return total


def remove_paths(files_to_delete: list[Path], dirs_to_delete: list[Path]) -> None:
    for path in files_to_delete:
        try:
            path.unlink()
        except FileNotFoundError:
            continue
    for path in dirs_to_delete:
        try:
            path.rmdir()
        except FileNotFoundError:
            continue
        except OSError:
            shutil.rmtree(path, ignore_errors=True)


def write_report(
    output_dir: Path,
    mode: str,
    dry_run: bool,
    keep_files: set[Path],
    files_to_delete: list[Path],
    dirs_to_delete: list[Path],
    reclaimed_bytes: int,
) -> Path:
    report_path = output_dir / "cleanup-report.json"
    payload = {
        "mode": mode,
        "dry_run": dry_run,
        "kept_files": sorted(str(path.relative_to(output_dir)) for path in keep_files if path.exists() and output_dir in path.parents),
        "deleted_files": sorted(str(path.relative_to(output_dir)) for path in files_to_delete),
        "deleted_directories": sorted(str(path.relative_to(output_dir)) for path in dirs_to_delete),
        "estimated_reclaimed_bytes": reclaimed_bytes,
    }
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report_path


def main() -> None:
    args = parse_args()
    output_dir = resolve_output_dir(args.output_dir)
    effective_dry_run = args.dry_run or args.mode == "debug"

    keep_files = build_keep_set(output_dir, args.mode)
    keep_dirs = keep_directories(output_dir, keep_files)
    files_to_delete, dirs_to_delete = list_deletions(output_dir, keep_files, keep_dirs)
    reclaimed_bytes = byte_size(files_to_delete)

    if not effective_dry_run:
        remove_paths(files_to_delete, dirs_to_delete)

    report_path = write_report(
        output_dir=output_dir,
        mode=args.mode,
        dry_run=effective_dry_run,
        keep_files=keep_files,
        files_to_delete=files_to_delete,
        dirs_to_delete=dirs_to_delete,
        reclaimed_bytes=reclaimed_bytes,
    )

    summary = {
        "output_dir": str(output_dir),
        "mode": args.mode,
        "dry_run": effective_dry_run,
        "kept_count": len(keep_files),
        "deleted_file_count": len(files_to_delete),
        "deleted_directory_count": len(dirs_to_delete),
        "estimated_reclaimed_bytes": reclaimed_bytes,
        "report_path": str(report_path),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
