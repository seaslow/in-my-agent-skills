#!/usr/bin/env python3
"""Extract a conservative evidence manifest from PPTX or PDF slides."""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def xml_root(archive: zipfile.ZipFile, member: str) -> ET.Element | None:
    try:
        return ET.fromstring(archive.read(member))
    except (KeyError, ET.ParseError):
        return None


def rels_member(source_part: str) -> str:
    directory, filename = posixpath.split(source_part)
    return posixpath.join(directory, "_rels", filename + ".rels")


def relationships(archive: zipfile.ZipFile, source_part: str) -> dict[str, dict[str, object]]:
    root = xml_root(archive, rels_member(source_part))
    if root is None:
        return {}
    result: dict[str, dict[str, object]] = {}
    for rel in root.findall(f"{{{REL_NS}}}Relationship"):
        target = rel.get("Target", "")
        external = rel.get("TargetMode") == "External"
        if external:
            resolved = target
        elif target.startswith("/"):
            resolved = posixpath.normpath(target.lstrip("/"))
        else:
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source_part), target))
        result[rel.get("Id", "")] = {
            "id": rel.get("Id", ""),
            "kind": rel.get("Type", "").rsplit("/", 1)[-1],
            "target": target,
            "resolved_target": resolved,
            "external": external,
        }
    return result


def all_text(root: ET.Element | None) -> list[str]:
    if root is None:
        return []
    values = []
    for elem in root.iter():
        if local_name(elem.tag) == "t" and elem.text and elem.text.strip():
            values.append(elem.text.strip())
    return values


def numeric_values(root: ET.Element | None) -> list[str]:
    if root is None:
        return []
    values = []
    for elem in root.iter():
        if local_name(elem.tag) == "v" and elem.text and elem.text.strip():
            values.append(elem.text.strip())
    return values


def shape_inventory(root: ET.Element, rels: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    shapes = []
    shape_tags = {"sp", "pic", "graphicFrame", "cxnSp", "contentPart"}
    for elem in root.iter():
        if local_name(elem.tag) not in shape_tags:
            continue
        texts = all_text(elem)
        metadata = None
        for child in elem.iter():
            if local_name(child.tag) == "cNvPr":
                metadata = child
                break
        links = []
        for child in elem.iter():
            if local_name(child.tag) not in {"hlinkClick", "hlinkHover"}:
                continue
            rid = child.get(f"{{{NS['r']}}}id")
            if rid and rid in rels:
                links.append(rels[rid])
        if texts or metadata is not None or links:
            shapes.append(
                {
                    "type": local_name(elem.tag),
                    "name": metadata.get("name") if metadata is not None else None,
                    "title": metadata.get("title") if metadata is not None else None,
                    "description": metadata.get("descr") if metadata is not None else None,
                    "text": texts,
                    "hyperlinks": links,
                }
            )
    return shapes


def related_content(
    archive: zipfile.ZipFile, rels: dict[str, dict[str, object]], archive_names: set[str]
) -> list[dict[str, object]]:
    result = []
    inspect_kinds = {"chart", "diagramData", "diagramDrawing", "oleObject", "package"}
    for rel in rels.values():
        if rel["external"] or rel["kind"] not in inspect_kinds:
            continue
        target = str(rel["resolved_target"])
        item: dict[str, object] = {"kind": rel["kind"], "archive_path": target}
        if target in archive_names and target.endswith(".xml"):
            root = xml_root(archive, target)
            item["text"] = all_text(root)
            item["numeric_values"] = numeric_values(root)
        result.append(item)
    return result


def inspect_pptx(path: Path) -> dict[str, object]:
    with zipfile.ZipFile(path) as archive:
        archive_names = set(archive.namelist())
        presentation = xml_root(archive, "ppt/presentation.xml")
        presentation_rels = relationships(archive, "ppt/presentation.xml")
        slide_parts = []
        if presentation is not None:
            for elem in presentation.iter():
                if local_name(elem.tag) != "sldId":
                    continue
                rid = elem.get(f"{{{NS['r']}}}id")
                if rid and rid in presentation_rels:
                    slide_parts.append(str(presentation_rels[rid]["resolved_target"]))
        if not slide_parts:
            slide_parts = sorted(
                (name for name in archive_names if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)),
                key=lambda name: int(re.search(r"(\d+)", posixpath.basename(name)).group(1)),
            )

        slides = []
        for index, slide_part in enumerate(slide_parts, start=1):
            root = xml_root(archive, slide_part)
            if root is None:
                slides.append({"slide_number": index, "archive_path": slide_part, "parse_error": True})
                continue
            rels = relationships(archive, slide_part)
            shapes = shape_inventory(root, rels)
            notes_text = []
            for rel in rels.values():
                if rel["kind"] == "notesSlide" and not rel["external"]:
                    notes_text.extend(all_text(xml_root(archive, str(rel["resolved_target"]))))
            slide_text = all_text(root)
            slides.append(
                {
                    "slide_number": index,
                    "archive_path": slide_part,
                    "hidden": root.get("show") in {"0", "false", "False"},
                    "title_guess": slide_text[0] if slide_text else None,
                    "text": slide_text,
                    "shapes": shapes,
                    "speaker_notes": notes_text,
                    "relationships": list(rels.values()),
                    "related_content": related_content(archive, rels, archive_names),
                }
            )

        return {
            "format": "pptx",
            "slide_count": len(slides),
            "slides": slides,
            "embedded_media": sorted(
                name for name in archive_names if name.startswith(("ppt/media/", "ppt/embeddings/"))
            ),
            "limitations": [
                "Object geometry, animation timing, and visual meaning require rendered-slide inspection.",
                "Text order follows XML traversal and may not equal reading or reveal order.",
            ],
        }


def run_text(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return completed.stdout


def inspect_pdf(path: Path) -> dict[str, object]:
    if not shutil.which("pdfinfo") or not shutil.which("pdftotext"):
        raise RuntimeError("PDF inspection requires pdfinfo and pdftotext (Poppler).")
    info_text = run_text(["pdfinfo", str(path)])
    match = re.search(r"^Pages:\s+(\d+)", info_text, flags=re.MULTILINE)
    if not match:
        raise RuntimeError("Could not determine PDF page count.")
    page_count = int(match.group(1))
    pages = []
    for page_number in range(1, page_count + 1):
        text = run_text(
            ["pdftotext", "-f", str(page_number), "-l", str(page_number), "-layout", str(path), "-"]
        ).strip()
        pages.append({"slide_number": page_number, "text": text.splitlines(), "title_guess": None})
    return {
        "format": "pdf",
        "slide_count": page_count,
        "slides": pages,
        "pdfinfo": info_text.splitlines(),
        "limitations": [
            "PDF exposes final rendered pages, not reliable object structure, notes, hidden slides, or animation timing.",
            "Extracted text is an index only; every page still requires direct visual inspection.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    if not source.is_file():
        parser.error(f"Input does not exist: {source}")
    suffix = source.suffix.lower()
    if suffix == ".pptx":
        payload = inspect_pptx(source)
    elif suffix == ".pdf":
        payload = inspect_pdf(source)
    else:
        parser.error("Supported inputs are .pptx and .pdf. Convert .ppt or Keynote first.")

    manifest = {
        "schema_version": 1,
        "source": str(source),
        "source_sha256": sha256(source),
        **payload,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "slides": manifest["slide_count"], "format": suffix[1:]}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, zipfile.BadZipFile, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
