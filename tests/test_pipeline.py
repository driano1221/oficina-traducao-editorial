"""Fixtures inteiramente sintéticas. Nenhum livro, rede ou chamada paga nos testes."""
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

import app
import tradutor as engine


def synthetic_epub(path, inline_cut=False, shared_chapters=False):
    pagebreak = '<span id="pg_2" role="doc-pagebreak"></span>'
    paragraph = '<p id="later">Original outside selection.</p>'
    if inline_cut:
        paragraph = '<p id="later">Before ' + pagebreak + ' after.</p>'
        pagebreak = ''
    chapter = '''<html xmlns="http://www.w3.org/1999/xhtml"><head><title>Example</title>
<link rel="stylesheet" href="style.css"/></head><body>
<h1 id="chapter1">Chapter 1: Example</h1><span id="pg_1" role="doc-pagebreak"></span>
<p id="first">A test <a href="#note1"><sup>1</sup></a>.</p>
<figure id="f1"><img src="images/plot.svg" alt="Original"/><figcaption>Figure 1: Test.</figcaption></figure>
<table id="table1"><caption>Table 1: Values.</caption><tr><th>Value</th><td>12</td></tr></table>
<p id="equation">Equation <math xmlns="http://www.w3.org/1998/Math/MathML"><mi>x</mi><mo>=</mo><mn>1</mn></math></p>
<p id="note1">A synthetic reference.</p><details><summary id="solution"><strong>Solution</strong></summary><p>A test answer.</p></details>''' + pagebreak + paragraph + '</body></html>'
    second = '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>Second</title></head><body><h1>Chapter 2</h1><p>Untranslated second chapter.</p></body></html>'
    second_href = 'chapter.xhtml#later' if shared_chapters else 'second.xhtml'
    files = {
        'mimetype': 'application/epub+zip',
        'META-INF/container.xml': '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/package.opf"/></rootfiles></container>',
        'OEBPS/package.opf': '''<package xmlns="http://www.idpf.org/2007/opf" version="2.0"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Synthetic book</dc:title><dc:language>en</dc:language></metadata><manifest>
<item id="c1" href="chapter.xhtml" media-type="application/xhtml+xml"/>
<item id="c2" href="second.xhtml" media-type="application/xhtml+xml"/>
<item id="css" href="style.css" media-type="text/css"/>
<item id="toc" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
<item id="image" href="images/plot.svg" media-type="image/svg+xml"/>
</manifest><spine toc="toc"><itemref idref="c1"/><itemref idref="c2"/></spine></package>''',
        'OEBPS/chapter.xhtml': chapter,
        'OEBPS/second.xhtml': second,
        'OEBPS/style.css': 'table{width:45%}sup{font-size:70%}',
        'OEBPS/images/plot.svg': '<svg xmlns="http://www.w3.org/2000/svg" width="80" height="40"><rect width="80" height="40" fill="teal"/></svg>',
        'OEBPS/toc.ncx': '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/"><navMap><navPoint id="c1"><navLabel><text>Chapter 1</text></navLabel><content src="chapter.xhtml#chapter1"/></navPoint><navPoint id="c2"><navLabel><text>Chapter 2</text></navLabel><content src="' + second_href + '"/></navPoint></navMap></ncx>',
    }
    with zipfile.ZipFile(path, 'w') as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return files


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source.epub'
        self.original = synthetic_epub(self.source)

    def config(self, **kwargs):
        return engine.JobConfig(pdf=self.source, output=self.root / 'work', pages=[1], **kwargs)

    def run_epub(self, config):
        def translate(config, items, log):
            return {item['id']: item['source'].replace('A test', 'Um teste').replace('Figure 1', 'Figura 1').replace('Table 1', 'Tabela 1').replace('Solution', 'Solução') for item in items}
        fake_document = MagicMock()
        fake_document.__enter__.return_value = fake_document
        fake_document.page_count = 2
        fake_page = MagicMock()
        fake_page.get_text.return_value = 'Texto sintético de teste.'
        fake_document.__iter__.return_value = iter([fake_page])
        with patch.object(engine, 'translate_editorial_chunks', side_effect=translate), patch.object(engine, 'audit_editorial_translation', return_value={'status': 'aprovado', 'problemas': []}), patch.object(engine, 'print_html_to_pdf'), patch.object(engine.fitz, 'open', return_value=fake_document):
            return engine.run_epub_job(config, lambda _: None)

    def test_page_parser_sorts_and_deduplicates(self):
        self.assertEqual(engine.parse_pages('3-1,2,5', 5), [1, 2, 3, 5])

    def test_page_parser_rejects_out_of_range(self):
        for spec in ('0', '1-9', ''):
            with self.assertRaises(ValueError):
                engine.parse_pages(spec, 5)

    def test_markers_are_preserved_in_order(self):
        self.assertEqual(engine.expected_markers('<!-- PAGINA_FISICA_002 -->\n<!-- PAGINA_FISICA_010 -->'), [2, 10])

    def test_epub_inventory(self):
        inventory = app.epub_inventory(self.source)
        self.assertEqual(len(inventory['chapters']), 2)
        self.assertEqual(inventory['printed_pages'], 2)

    def test_disclosure_summary_is_translated_with_structure_preserved(self):
        config = self.config(chapters=1)
        self.run_epub(config)
        with zipfile.ZipFile(config.output / 'livro_ptbr.epub') as archive:
            doc = BeautifulSoup(archive.read('OEBPS/chapter.xhtml'), 'html.parser')
        self.assertEqual(doc.select_one('details > summary#solution > strong').get_text(), 'Solução')
        self.assertEqual(doc.select_one('details > p').get_text(), 'Um teste answer.')

    def test_math_and_image_roundtrip(self):
        source = '<b>Test</b><img src="x.svg"/><math><mi>x</mi></math><span class="math">x+1</span>'
        protected, tokens = engine.protect_epub_nontext(source, 'test')
        self.assertEqual(len(tokens), 3)
        self.assertEqual(engine.restore_math(protected, tokens), str(BeautifulSoup(source, 'html.parser')))

    def test_nested_protected_objects_do_not_duplicate(self):
        source = '<span class="math"><img src="equation.svg"/></span>'
        protected, tokens = engine.protect_epub_nontext(source, 'test')
        self.assertEqual(len(tokens), 1)
        self.assertEqual(engine.restore_math(protected, tokens), str(BeautifulSoup(source, 'html.parser')))

    def test_changed_link_rejected(self):
        item = {'id': 'i', 'source': '<a href="#note">Note</a>', 'tags': ['a'], 'math': {}}
        path = self.root / 'translation.json'
        path.write_text(json.dumps({'i': '<a href="#wrong">Nota</a>'}), encoding='utf-8')
        self.assertIsNone(engine.parse_editorial_result(path, [item]))

    def test_valid_translation_accepted(self):
        item = {'id': 'i', 'source': '<a href="#note">Note</a>', 'tags': ['a'], 'math': {}}
        path = self.root / 'translation.json'
        expected = {'i': '<a href="#note">Nota</a>'}
        path.write_text(json.dumps(expected), encoding='utf-8')
        self.assertEqual(engine.parse_editorial_result(path, [item]), expected)

    def test_missing_protection_rejected(self):
        item = {'id': 'i', 'source': 'Formula [[[MATH_i_0001]]]', 'tags': [], 'math': {'[[[MATH_i_0001]]]': '<math/>'}}
        path = self.root / 'translation.json'
        path.write_text('{"i":"Formula removida"}', encoding='utf-8')
        self.assertIsNone(engine.parse_editorial_result(path, [item]))

    def test_partial_epub_keeps_original_remainder_and_assets(self):
        config = self.config()
        qa = self.run_epub(config)
        self.assertEqual(qa['status'], 'aprovado')
        with zipfile.ZipFile(config.output / 'livro_ptbr.epub') as output:
            self.assertEqual(output.infolist()[0].filename, 'mimetype')
            self.assertEqual(output.infolist()[0].compress_type, zipfile.ZIP_STORED)
            for name, contents in self.original.items():
                if name != 'OEBPS/chapter.xhtml':
                    self.assertEqual(output.read(name), contents.encode())
            soup = BeautifulSoup(output.read('OEBPS/chapter.xhtml'), 'html.parser')
            self.assertIn('Um teste', soup.select_one('#first').get_text())
            self.assertEqual(soup.select_one('#first a')['href'], '#note1')
            self.assertEqual(soup.select_one('#later').get_text(), 'Original outside selection.')
            self.assertTrue(soup.select_one('#pg_2'))
            self.assertEqual(soup.img['src'], 'images/plot.svg')
            self.assertEqual(soup.caption.get_text(), 'Tabela 1: Values.')
            self.assertEqual(soup.math.get_text(), 'x=1')
            self.assertFalse(soup.select('[data-tr-id], [data-epub-node], [data-epub-src]'))

    def test_chapter_scope_not_truncated_by_page_markers(self):
        config = self.config(chapters=1)
        self.run_epub(config)
        html = (config.output / 'livro_ptbr.html').read_text(encoding='utf-8')
        self.assertIn('Original outside selection.', html)
        self.assertNotIn('Untranslated second chapter.', html)

    def test_inline_page_cut_is_rejected(self):
        synthetic_epub(self.source, inline_cut=True)
        with self.assertRaisesRegex(ValueError, 'dentro de um parágrafo'):
            self.run_epub(self.config())

    def test_shared_chapter_document_is_rejected(self):
        synthetic_epub(self.source, shared_chapters=True)
        with self.assertRaisesRegex(ValueError, 'mesmo XHTML'):
            self.run_epub(self.config(chapters=1))

    def test_usage_parsing(self):
        usage, errors = engine.parse_codex_usage('{"type":"turn.completed","usage":{"input_tokens":1000,"cached_input_tokens":200,"output_tokens":300}}')
        self.assertFalse(errors)
        self.assertAlmostEqual(engine.api_equivalent_cost('gpt-5.6-sol', usage), .00928)

    def test_unknown_model_cost_is_unavailable(self):
        self.assertIsNone(engine.api_equivalent_cost('unknown', {}))

    def test_missing_usage_is_not_zero_cost(self):
        config = self.config()
        config.output.mkdir()
        engine.record_codex_usage(config.output, Path('call.json'), config.model, {})
        with patch.object(engine.subprocess, 'run', side_effect=OSError):
            cost = engine.write_cost_report(config)
        self.assertIsNone(cost['custo_equivalente_api_usd'])
        self.assertIsNone(cost['cobranca_api_adicional'])

    def test_cost_sums_each_model_separately(self):
        config = self.config()
        config.output.mkdir()
        usage = {'input_tokens': 1000000, 'output_tokens': 0}
        engine.record_codex_usage(config.output, Path('one.json'), 'gpt-5.6-sol', usage)
        engine.record_codex_usage(config.output, Path('two.json'), 'gpt-5.6-luna', usage)
        with patch.object(engine.subprocess, 'run', side_effect=OSError):
            cost = engine.write_cost_report(config)
        self.assertEqual(cost['custo_equivalente_api_usd'], 4.2)

    def test_scope_creates_distinct_project(self):
        self.assertNotEqual(app.choose_project(self.source, self.root, '1-10'), app.choose_project(self.source, self.root, '1-20'))

    def test_changed_job_identity_rejected_before_translation(self):
        config = self.config()
        config.output.mkdir()
        (config.output / 'job_identity.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'outra|outro'):
            engine.run_job(config)

    def test_delivery_includes_original_page_assets(self):
        project = self.root / 'library'
        config = engine.JobConfig(self.source, project / '02_trabalho', [1])
        assets = config.output / 'paginas_originais'
        assets.mkdir(parents=True)
        (assets / 'test.png').write_bytes(b'synthetic')
        app.publish_project(project, self.source, config, {'status': 'revisar'}, '1')
        self.assertEqual((project / '03_entrega_atual/paginas_originais/test.png').read_bytes(), b'synthetic')
        self.assertEqual((project / '01_original/livro_original.epub').read_bytes(), self.source.read_bytes())


if __name__ == '__main__':
    unittest.main()
