"""Verifica os EPUBs sintéticos publicados, sem chamar modelo ou rede."""
import hashlib
import json
import unittest
import zipfile
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1] / 'examples/minilivro/publicados'


class PublishedDemoTests(unittest.TestCase):
    def test_public_artifacts_match_recorded_hashes(self):
        report = json.loads((ROOT / 'validacao.json').read_text(encoding='utf-8'))
        for label in ('original', 'traduzido'):
            digest = hashlib.sha256((ROOT / f'{label}.epub').read_bytes()).hexdigest()
            self.assertEqual(digest, report[f'sha256_{label}'])

    def test_real_translation_keeps_assets_data_math_and_note_targets(self):
        with zipfile.ZipFile(ROOT / 'original.epub') as original, zipfile.ZipFile(ROOT / 'traduzido.epub') as translated:
            self.assertEqual(original.namelist(), translated.namelist())
            self.assertIsNone(translated.testzip())
            for name in original.namelist():
                if name not in ('EPUB/chapter1.xhtml', 'EPUB/chapter2.xhtml'):
                    self.assertEqual(original.read(name), translated.read(name), name)
                    continue
                before = BeautifulSoup(original.read(name), 'html.parser')
                after = BeautifulSoup(translated.read(name), 'html.parser')
                self.assertEqual([n.get_text() for n in before.select('td')], [n.get_text() for n in after.select('td')])
                self.assertEqual([str(n) for n in before.select('math')], [str(n) for n in after.select('math')])
                self.assertEqual([n['href'] for n in before.select('a[href]')], [n['href'] for n in after.select('a[href]')])
                for link in after.select('a[href^="#"]'):
                    self.assertIsNotNone(after.find(id=link['href'][1:]))
                self.assertIn('Capítulo', after.h1.get_text())
                self.assertFalse(after.select('[data-tr-id], [data-epub-node]'))
            chapter = BeautifulSoup(translated.read('EPUB/chapter1.xhtml'), 'html.parser')
            self.assertIn('MSE =', chapter.get_text())
            self.assertNotIn('EQM', chapter.get_text())


if __name__ == '__main__':
    unittest.main()
