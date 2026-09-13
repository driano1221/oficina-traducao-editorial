"""Recorta a seção 2.1 do EPUB oficial; não reescreve o XHTML nem o CSS."""
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / 'tmp/significant-statistics'
DOC = 'EPUB/chapter-007-descriptive-statistics-and-frequency-distributions.xhtml'
SOURCE_URL = 'https://vtechworks.lib.vt.edu/bitstreams/0345ade7-4647-4dcc-8d6b-b88c172b3500/download'
SOURCE_SHA = 'f96dd4dbfef4b35979ccc171d7b21809833ca02fff5fdd5e45351fe4dd3e8fc9'


def prepare():
    source = LOCAL / 'original-completo.epub'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == SOURCE_SHA, 'Edição diferente: revise o recorte e as licenças.'
    with zipfile.ZipFile(source) as archive:
        doc = BeautifulSoup(archive.read(DOC), 'html.parser')
        assets = {'EPUB/' + n['src'] for n in doc.select('img[src]')}
        css = archive.read('EPUB/mcluhan.css')
        assets.update('EPUB/' + n for n in re.findall(r'url\(([^)]+)\)', css.decode()) if not n.startswith('data:'))
        names = {DOC, 'EPUB/mcluhan.css', 'mimetype', 'META-INF/container.xml'} | assets
        # Novo pacote de recorte; conteúdo e recursos da seção ficam byte a byte iguais.
        package = ET.fromstring(archive.read('EPUB/book.opf'))
        ns = '{http://www.idpf.org/2007/opf}'
        dc = '{http://purl.org/dc/elements/1.1/}'
        metadata = package.find(ns + 'metadata')
        metadata.find(dc + 'title').text += ' — Section 2.1 excerpt'
        ET.SubElement(metadata, dc + 'source').text = 'https://doi.org/10.21061/significantstatistics'
        ET.SubElement(metadata, dc + 'description').text = 'Unofficial excerpt prepared by driano1221 for Oficina de Tradução Editorial. Section XHTML, CSS and assets unchanged. CC BY-SA 4.0. No endorsement implied.'
        for node in list(metadata):
            if node.tag == ns + 'meta' and (node.get('name') == 'cover' or node.get('property', '').startswith('schema:')):
                metadata.remove(node)
        manifest = package.find(ns + 'manifest')
        for item in list(manifest):
            if 'EPUB/' + item.get('href', '') not in names:
                manifest.remove(item)
        ET.SubElement(manifest, ns + 'item', {'id': 'demo-nav', 'href': 'demo-nav.xhtml', 'media-type': 'application/xhtml+xml', 'properties': 'nav'})
        spine = package.find(ns + 'spine')
        spine.clear()
        selected = next(n for n in manifest if 'EPUB/' + n.get('href', '') == DOC)
        ET.SubElement(spine, ns + 'itemref', {'idref': selected.get('id')})
        for node in list(package):
            if node.tag not in {ns + 'metadata', ns + 'manifest', ns + 'spine'}:
                package.remove(node)
        nav = f'''<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en"><head><title>Excerpt navigation</title></head><body><nav epub:type="toc"><h1>Section excerpt</h1><ol><li><a href="{Path(DOC).name}">Chapter 2 — Section 2.1 only</a></li></ol></nav><p>Russell, John Morgan (2025). Significant Statistics: An Introduction to Statistics. Virginia Tech. <a href="https://doi.org/10.21061/significantstatistics">Original and attribution</a>. <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>. Unofficial excerpt / translation demonstration by driano1221, no endorsement implied.</p></body></html>'''
        with zipfile.ZipFile(LOCAL / 'original-recorte.epub', 'w', zipfile.ZIP_DEFLATED) as output:
            output.writestr('mimetype', archive.read('mimetype'), compress_type=zipfile.ZIP_STORED)
            for name in sorted(names - {'mimetype'}):
                output.writestr(name, archive.read(name))
            output.writestr('EPUB/book.opf', ET.tostring(package, encoding='utf-8', xml_declaration=True))
            output.writestr('EPUB/demo-nav.xhtml', nav)
    print('Recorte preparado: seção 2.1; XHTML, CSS, imagens e fontes originais preservados.')


def translate():
    sys.path.insert(0, str(ROOT))
    from tradutor import DEFAULT_INSTRUCTIONS, JobConfig, run_job
    instructions = DEFAULT_INSTRUCTIONS + ' Preserve RF, f e n, valores numéricos, separadores decimais e unidades originais (inches = polegadas, sem converter para cm). Preserve a numeração: o original chama as tabelas de Figure 2.2 e Figure 2.3; use Figura 2.2 e Figura 2.3, sem renumerar. Não corrija silenciosamente inconsistências didáticas da fonte. Mantenha títulos bibliográficos e URLs originais.'
    config = JobConfig(pdf=LOCAL / 'original-recorte.epub', output=LOCAL / '02_trabalho', pages=[], chapters=1, instructions=instructions)
    run_job(config, lambda message: print(message, flush=True))


if __name__ == '__main__':
    if '--traduzir' in sys.argv:
        translate()
    else:
        prepare()
