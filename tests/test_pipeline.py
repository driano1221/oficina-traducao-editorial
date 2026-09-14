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

    def test_numbered_chapter_label_does_not_match_decimal_section(self):
        self.assertTrue(engine.is_chapter_label('1. Introduction'))
        self.assertTrue(engine.is_chapter_label('Chapter 2: Methods'))
        self.assertFalse(engine.is_chapter_label('2.1 Background'))
        self.assertFalse(engine.is_chapter_label('Figure 2.1 Results'))

    def test_chapter_scope_stops_before_next_part_divider(self):
        docs = ['chapter1.xhtml', 'part2.xhtml', 'chapter2.xhtml']
        toc = [
            ('chapter1.xhtml', '1. First', 2),
            ('part2.xhtml', 'Part Two', 1),
            ('chapter2.xhtml', '2. Second', 2),
        ]
        chapters = [('chapter1.xhtml', '1. First'), ('chapter2.xhtml', '2. Second')]
        self.assertEqual(engine.chapter_document_slice(docs, toc, chapters, 1), {'chapter1.xhtml'})

    def test_epub_rerun_removes_stale_extracted_sections(self):
        config = self.config(chapters=1)
        source_dir = config.output / 'fonte_epub'
        source_dir.mkdir(parents=True)
        stale = source_dir / 'stale.xhtml'
        stale.write_text('old scope', encoding='utf-8')

        self.run_epub(config)

        self.assertFalse(stale.exists())
        self.assertEqual(len(list(source_dir.glob('*.xhtml'))), 1)

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

    def test_empty_navigation_anchor_is_protected(self):
        source = 'Before <a class="calibre12" id="filepos1"></a> after.'
        protected, tokens = engine.protect_epub_nontext(source, 'test')
        self.assertEqual(len(tokens), 1)
        self.assertNotIn('<a ', protected)
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

    def test_local_validation_blocks_numbers_and_glossary(self):
        report = engine.local_editorial_validation([
            {'id': 'number', 'fonte': 'The estimate is 2.01%.', 'traducao': 'A estimativa é 2,10%.'},
            {'id': 'term', 'fonte': 'Machine learning is useful.', 'traducao': 'Aprendizagem computacional é útil.'},
        ])
        self.assertEqual(report['status'], 'revisar')
        self.assertEqual({problem['tipo'] for problem in report['problemas']}, {'número alterado', 'glossário não aplicado'})
        self.assertEqual(set(report['itens_para_auditoria_semantica']), {'number', 'term'})
        self.assertIn("Fonte: ['201%']", report['problemas'][0]['explicacao'])

    def test_local_validation_sends_only_risky_prose_to_semantic_audit(self):
        report = engine.local_editorial_validation([
            {'id': 'heading', 'fonte': 'Introduction', 'traducao': 'Introdução'},
            {'id': 'long', 'fonte': 'Impact and causal effect. ' * 40, 'traducao': 'Impacto e efeito causal. ' * 40},
        ])
        self.assertNotIn('heading', report['itens_para_auditoria_semantica'])
        self.assertIn('long', report['itens_para_auditoria_semantica'])

    def test_written_english_number_may_become_a_digit(self):
        report = engine.local_editorial_validation([{
            'id': 'movement',
            'fonte': 'The May Fourth Movement began on May 4, 1919.',
            'traducao': 'O Movimento de 4 de Maio começou em 4 de maio de 1919.',
        }])
        self.assertNotIn('número alterado', {problem['tipo'] for problem in report['problemas']})

    def test_semantic_audit_receives_only_locally_selected_pairs(self):
        config = self.config()
        source_dir = config.output / 'fontes_editoriais'
        target_dir = config.output / 'traduzidos_editoriais'
        source_dir.mkdir(parents=True)
        target_dir.mkdir()
        source = {'heading': 'Introduction', 'long': 'Impact and causal effect. ' * 40}
        target = {'heading': 'Introdução', 'long': 'Impacto e efeito causal. ' * 40}
        (source_dir / 'bloco_001.json').write_text(json.dumps(source), encoding='utf-8')
        (target_dir / 'bloco_001.json').write_text(json.dumps(target), encoding='utf-8')

        def review(prompt, cwd, output, model):
            self.assertNotIn('"id": "heading"', prompt)
            self.assertIn('"id": "long"', prompt)
            output.write_text(json.dumps({'status': 'aprovado', 'pares_revisados': 1, 'problemas': []}), encoding='utf-8')
            return 0, ''

        with patch.object(engine, 'run_codex', side_effect=review):
            audit = engine.audit_editorial_translation(config, lambda _: None)
        self.assertEqual(audit['status'], 'aprovado')
        self.assertEqual(audit['pares_totais'], 2)
        self.assertEqual(audit['pares_liberados_localmente'], 1)
        self.assertEqual(audit['pares_revisados'], 1)
        self.assertTrue((config.output / 'validacao_local.json').exists())

    def test_segment_memory_avoids_retranslating_same_content(self):
        memory = self.root / 'library' / 'memory.sqlite3'
        item = {'id': 'p1', 'source': '<strong>A causal effect</strong>.', 'math': {}, 'tags': ['strong']}
        first = engine.JobConfig(self.source, self.root / 'first', [1], memory_db=memory)
        second = engine.JobConfig(self.source, self.root / 'second', [1], memory_db=memory)
        stale_source = first.output / 'fontes_editoriais' / 'bloco_099.json'
        stale_target = first.output / 'traduzidos_editoriais' / 'bloco_099.json'
        stale_meta = first.output / 'traduzidos_editoriais' / 'bloco_099.meta.json'
        stale_source.parent.mkdir(parents=True)
        stale_target.parent.mkdir(parents=True)
        for stale in (stale_source, stale_target, stale_meta):
            stale.write_text('{}', encoding='utf-8')

        def translate(prompt, cwd, output, model):
            output.write_text(json.dumps({'p1': '<strong>Um efeito causal</strong>.'}), encoding='utf-8')
            return 0, ''

        with patch.object(engine, 'run_codex', side_effect=translate) as run:
            result_first = engine.translate_editorial_chunks(first, [item], lambda _: None)
            engine.translation_memory_put(first, [item], result_first)
            result_second = engine.translate_editorial_chunks(second, [item], lambda _: None)
        self.assertEqual(result_first, result_second)
        self.assertEqual(run.call_count, 1)
        self.assertFalse(stale_source.exists())
        self.assertFalse(stale_target.exists())
        self.assertFalse(stale_meta.exists())
        self.assertTrue(memory.exists())
        self.assertEqual(json.loads((second.output / 'memoria_reutilizada.json').read_text())['segmentos'], 1)

    def test_approved_memory_hit_skips_semantic_reaudit(self):
        config = self.config()
        source_dir = config.output / 'fontes_editoriais'
        target_dir = config.output / 'traduzidos_editoriais'
        source_dir.mkdir(parents=True)
        target_dir.mkdir()
        source = {'long': 'Impact and causal effect. ' * 40}
        target = {'long': 'Impacto e efeito causal. ' * 40}
        (source_dir / 'bloco_001.json').write_text(json.dumps(source), encoding='utf-8')
        (target_dir / 'bloco_001.json').write_text(json.dumps(target), encoding='utf-8')
        engine.translation_memory_put(
            config, [{'id': 'long', 'source': source['long'], 'math': {}}], target
        )
        (config.output / 'memoria_reutilizada.json').write_text(json.dumps({'ids': ['long']}), encoding='utf-8')

        with patch.object(engine, 'run_codex') as run:
            audit = engine.audit_editorial_translation(config, lambda _: None)
        run.assert_not_called()
        self.assertEqual(audit['status'], 'aprovado')
        self.assertEqual(audit['pares_reutilizados_memoria'], 1)

    def test_quality_loop_reaudits_only_repaired_ids(self):
        config = self.config()
        config.output.mkdir()
        items = [
            {'id': 'bad', 'source': 'The effect is not zero.', 'math': {}, 'tags': []},
            {'id': 'good', 'source': 'Introduction', 'math': {}, 'tags': []},
        ]
        translated = {'bad': 'O efeito é zero.', 'good': 'Introdução'}
        initial = {'status': 'revisar', 'problemas': [{'id': 'bad', 'tipo': 'negação'}]}
        approved = {'status': 'aprovado', 'problemas': [], 'pares_revisados': 1}

        with patch.object(engine, 'audit_editorial_translation', side_effect=[initial, approved]) as audit, \
                patch.object(engine, 'repair_editorial_translation', return_value={'bad'}):
            final = engine.run_editorial_quality_loop(config, items, translated, lambda _: None)
        self.assertEqual(final['status'], 'aprovado')
        self.assertEqual(audit.call_count, 2)
        self.assertEqual(audit.call_args_list[1].kwargs['force_ids'], {'bad'})

    def test_directed_repair_changes_only_failed_segment(self):
        config = self.config()
        target_dir = config.output / 'traduzidos_editoriais'
        target_dir.mkdir(parents=True)
        current = {'bad': 'O efeito é zero.', 'good': 'Introdução'}
        (target_dir / 'bloco_001.json').write_text(json.dumps(current), encoding='utf-8')
        items = [
            {'id': 'bad', 'source': 'The effect is not zero.', 'math': {}, 'tags': []},
            {'id': 'good', 'source': 'Introduction', 'math': {}, 'tags': []},
        ]
        audit = {'status': 'revisar', 'problemas': [{'id': 'bad', 'tipo': 'negação'}]}

        def repair(prompt, cwd, output, model):
            self.assertIn('"id": "bad"', prompt)
            self.assertNotIn('"id": "good"', prompt)
            output.write_text(json.dumps({'bad': 'O efeito não é zero.'}), encoding='utf-8')
            return 0, ''

        with patch.object(engine, 'run_codex', side_effect=repair):
            repaired = engine.repair_editorial_translation(config, items, current, audit, lambda _: None, 1)
        saved = json.loads((target_dir / 'bloco_001.json').read_text(encoding='utf-8'))
        self.assertEqual(repaired, {'bad'})
        self.assertEqual(saved, {'bad': 'O efeito não é zero.', 'good': 'Introdução'})

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
