"""Gera um EPUB autoral; --traduzir executa o motor real e consome uso."""
import argparse
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO))
from tradutor import DEFAULT_INSTRUCTIONS, JobConfig, run_job
from app import publish_project

def create_epub():
    output = ROOT / "publicados"
    output.mkdir(exist_ok=True)
    path = output / "original.epub"
    package = '''<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="book-id">urn:uuid:7bd6b701-532e-4c5d-a9f7-88613a15cb72</dc:identifier><dc:title>Field notes: a synthetic learning guide</dc:title><dc:creator>Oficina de Tradução Editorial</dc:creator><dc:language>en</dc:language><dc:rights>Material original de demonstração; CC0 1.0.</dc:rights><meta property="dcterms:modified">2026-09-13T00:00:00Z</meta></metadata><manifest>
<item id="c1" href="chapter1.xhtml" media-type="application/xhtml+xml" properties="mathml"/>
<item id="c2" href="chapter2.xhtml" media-type="application/xhtml+xml"/>
<item id="css" href="style.css" media-type="text/css"/>
<item id="figure" href="measurements.svg" media-type="image/svg+xml"/>
<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
</manifest><spine><itemref idref="c1"/><itemref idref="c2"/></spine></package>'''
    nav = '''<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en"><head><title>Contents</title></head><body><nav epub:type="toc"><h1>Contents</h1><ol><li><a href="chapter1.xhtml#chapter1">Chapter 1: Measuring prediction error</a></li><li><a href="chapter2.xhtml#chapter2">Chapter 2: Read the pattern, question the claim</a></li></ol></nav></body></html>'''
    if path.exists():
        with zipfile.ZipFile(path) as existing:
            same_sources = all(existing.read("EPUB/" + source.name) == source.read_bytes() for source in (ROOT / "fonte").iterdir())
            if same_sources and existing.read("EPUB/package.opf") == package.encode() and existing.read("EPUB/nav.xhtml") == nav.encode():
                return path
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        archive.writestr("META-INF/container.xml", '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0"><rootfiles><rootfile full-path="EPUB/package.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
        archive.writestr("EPUB/package.opf", package)
        archive.writestr("EPUB/nav.xhtml", nav)
        for source in sorted((ROOT / "fonte").iterdir()):
            archive.writestr("EPUB/" + source.name, source.read_bytes())
    return path

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--traduzir", action="store_true")
    parser.add_argument("--model", default="gpt-5.6-sol")
    args = parser.parse_args()
    source = create_epub()
    print(source)
    if args.traduzir:
        project = REPO / "tmp" / "demo-biblioteca-final"
        instructions = DEFAULT_INSTRUCTIONS + " Preserve a sigla MSE também na prosa, pois ela identifica a equação matemática preservada."
        config = JobConfig(source, project / "02_trabalho", [], chapters=2, model=args.model, instructions=instructions)
        qa = run_job(config)
        publish_project(project, source, config, qa, "2 capítulos sintéticos")
        print(json.dumps(qa, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
