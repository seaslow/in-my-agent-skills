#!/usr/bin/env python3
"""Normalize fonts in a .pptx: Latin/cs -> Times New Roman, East Asian -> 等线.
Also strips supplemental theme fonts, fixes docProps/app.xml, and with
--fix-notes-theme gives notes masters lacking a theme a copy of theme1.
Usage: pptx_fonts.py IN.pptx [OUT.pptx] [--latin NAME] [--ea NAME] [--fix-notes-theme]"""
import argparse, re, shutil, tempfile, zipfile, pathlib
from lxml import etree
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
THEME_T = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme"

def fix_xml(path, latin, ea):
    t = etree.parse(str(path)); root = t.getroot(); ch = False
    for el in root.iter(f"{{{A}}}latin", f"{{{A}}}cs"):
        if el.get("typeface") not in (latin,) and not el.get("typeface", "").startswith("+"):
            el.set("typeface", latin); ch = True
    for el in root.iter(f"{{{A}}}ea"):
        if el.get("typeface") != ea and not el.get("typeface", "").startswith("+"):
            el.set("typeface", ea); ch = True
    for rpr in root.iter(f"{{{A}}}rPr", f"{{{A}}}defRPr", f"{{{A}}}endParaRPr"):
        lat = rpr.find(f"{{{A}}}latin")
        if lat is not None and rpr.find(f"{{{A}}}ea") is None:
            e = etree.Element(f"{{{A}}}ea"); e.set("typeface", ea); lat.addnext(e); ch = True
    for tag in ("majorFont", "minorFont"):
        for mf in root.iter(f"{{{A}}}{tag}"):
            for sub, face in (("latin", latin), ("ea", ea), ("cs", latin)):
                el = mf.find(f"{{{A}}}{sub}")
                if el is not None: el.set("typeface", face); ch = True
            for f in mf.findall(f"{{{A}}}font"):
                mf.remove(f); ch = True
    if ch: t.write(str(path), xml_declaration=True, encoding="UTF-8", standalone=True)

def fix_app(d, latin, ea):
    p = d / "docProps/app.xml"
    if not p.exists(): return
    s = p.read_text(encoding="utf-8")
    faces = set(re.findall(r"<vt:lpstr>([^<]+)</vt:lpstr>", s))
    for f in faces:
        if f in ("Arial", "Calibri", "Calibri Light", "等线 Light", "游ゴシック", "Noto Sans CJK SC", "Microsoft YaHei"):
            s = s.replace(f"<vt:lpstr>{f}</vt:lpstr>", f"<vt:lpstr>{latin}</vt:lpstr>")
    p.write_text(s, encoding="utf-8")

def fix_notes_theme(d):
    for rels in (d / "ppt/notesMasters/_rels").glob("*.rels"):
        t = etree.parse(str(rels))
        master_themes = set()
        for mr in (d / "ppt/slideMasters/_rels").glob("*.rels"):
            master_themes |= {r.get("Target") for r in etree.parse(str(mr)).getroot() if r.get("Type") == THEME_T}
        own = [r for r in t.getroot() if r.get("Type") == THEME_T]
        if own and not ({r.get("Target") for r in own} & master_themes): continue
        for r in own: t.getroot().remove(r)
        themes = sorted((d / "ppt/theme").glob("theme*.xml"))
        n = max(int(re.search(r"(\d+)", x.name).group(1)) for x in themes) + 1
        shutil.copy(d / "ppt/theme/theme1.xml", d / f"ppt/theme/theme{n}.xml")
        ids = [r.get("Id") for r in t.getroot()]
        rid = next(f"rId{i}" for i in range(1, 99) if f"rId{i}" not in ids)
        r = etree.SubElement(t.getroot(), f"{{{REL}}}Relationship")
        r.set("Id", rid); r.set("Type", THEME_T); r.set("Target", f"../theme/theme{n}.xml")
        t.write(str(rels), xml_declaration=True, encoding="UTF-8", standalone=True)
        ct = etree.parse(str(d / "[Content_Types].xml"))
        o = etree.SubElement(ct.getroot(), f"{{{CT}}}Override")
        o.set("PartName", f"/ppt/theme/theme{n}.xml")
        o.set("ContentType", "application/vnd.openxmlformats-officedocument.theme+xml")
        ct.write(str(d / "[Content_Types].xml"), xml_declaration=True, encoding="UTF-8", standalone=True)
        print(f"added notes theme theme{n}.xml for {rels.name}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out", nargs="?")
    ap.add_argument("--latin", default="Times New Roman"); ap.add_argument("--ea", default="等线")
    ap.add_argument("--fix-notes-theme", action="store_true")
    a = ap.parse_args(); out = a.out or a.inp
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        with zipfile.ZipFile(a.inp) as z: names = z.namelist(); z.extractall(d)
        for f in d.rglob("*.xml"): fix_xml(f, a.latin, a.ea)
        fix_app(d, a.latin, a.ea)
        if a.fix_notes_theme: fix_notes_theme(d)
        names = ["[Content_Types].xml"] + [n for n in names if n != "[Content_Types].xml"]
        extra = [str(p.relative_to(d)) for p in d.rglob("*") if p.is_file() and str(p.relative_to(d)) not in names]
        tmp = out + ".tmp"
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
            for n in names + extra:
                if (d / n).is_file(): z.write(d / n, n)
        shutil.move(tmp, out)
    print("fonts normalized ->", out)

if __name__ == "__main__": main()
