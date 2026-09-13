"""Verifica o recorte traduzido e extrai os EPUBs para capturas de leitura."""
import hashlib
import json
import re
import zipfile
from pathlib import Path

from bs4 import BeautifulSoup
from preparar import DOC, LOCAL, ROOT, SOURCE_SHA, SOURCE_URL


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    source = LOCAL / 'original-recorte.epub'
    translated = LOCAL / '02_trabalho/livro_ptbr.epub'
    qa = json.loads((LOCAL / '02_trabalho/relatorio_qa.json').read_text(encoding='utf-8'))
    cost = json.loads((LOCAL / '02_trabalho/custo.json').read_text(encoding='utf-8'))
    with zipfile.ZipFile(source) as before, zipfile.ZipFile(translated) as after:
        assert before.namelist() == after.namelist()
        assert after.testzip() is None
        intact = [name for name in before.namelist() if name != DOC]
        assert all(before.read(name) == after.read(name) for name in intact)
        original = BeautifulSoup(before.read(DOC), 'html.parser')
        output = BeautifulSoup(after.read(DOC), 'html.parser')
        assert len(original.find_all(True)) == len(output.find_all(True))
        for a, b in zip(original.body.find_all(True), output.body.find_all(True)):
            attrs = lambda n: {k: v for k, v in n.attrs.items() if k not in {'lang', 'xml:lang'}}
            assert a.name == b.name and attrs(a) == attrs(b), (str(a)[:100], str(b)[:100])
        assert [re.findall(r'\d+(?:\.\d+)?', n.get_text()) for n in original.select('td')] == [re.findall(r'\d+(?:\.\d+)?', n.get_text()) for n in output.select('td')]
        for link in output.select('a[href^="#"]'):
            assert output.find(id=link['href'][1:]) is not None
        assert all('Solução' in n.get_text() for n in output.select('summary'))
        assert 'Figura 2.1' in output.figcaption.get_text()
        assert 'Figura 2.2' in output.find(id='tablepress-3-description').get_text()
        assert 'Figura 2.3' in output.find(id='tablepress-4-description').get_text()
        for label, archive in [('original', before), ('traduzido', after)]:
            folder = LOCAL / 'preview' / label
            for name in archive.namelist():
                target = (folder / name).resolve()
                assert target.is_relative_to(folder.resolve()), name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(name))
    report = {
        'data': '2026-09-13', 'fonte_url': SOURCE_URL,
        'obra': 'Russell, John Morgan (2025). Significant Statistics: An Introduction to Statistics.',
        'licenca_conteudo_e_comparativos': 'CC BY-SA 4.0; fotografia Figura 2.1 em domínio público conforme crédito da obra',
        'recorte': 'Seção 2.1 completa; não é o capítulo 2 inteiro',
        'sha256_epub_oficial': SOURCE_SHA,
        'sha256_recorte_original': digest(source), 'sha256_recorte_traduzido': digest(translated),
        'sha256_motor': digest(ROOT / 'tradutor.py'),
        'elementos_traduzidos': qa['elementos_traduzidos'],
        'tabelas': len(output.select('table')),
        'celulas_de_dados': len(output.select('td')),
        'ocorrencias_de_imagens': len(output.select('img')),
        'formulas_em_imagens': len(output.select('img.ql-img-inline-formula')),
        'legendas_de_figuras_e_tabelas': ['2.1', '2.2', '2.3'],
        'arquivos_fora_do_xhtml_intactos': len(intact),
        'estrutura_tags_atributos_links': 'idêntica no body, exceto lang/xml:lang atualizados nos nós traduzidos',
        'valores_numericos_das_tabelas': 'idênticos, sem conversão de unidades',
        'links_internos': 'todos resolvem para um id existente',
        'auditoria_automatica': qa['auditoria_semantica'],
        'modelo': cost['modelo'],
        'chamadas_registradas_incluindo_reenvios': cost['chamadas_registradas'],
        'tokens': cost['tokens'],
        'equivalente_api_usd': cost['custo_equivalente_api_usd'],
        'cobranca_real_verificada': False,
        'limites': ['Comparativos são recortes de leitura do XHTML dos EPUBs, não do PDF.',
                    'Fontes e CSS originais, sem retoques de texto ou dimensões internas para a captura.',
                    'Atributos de acessibilidade e metadados permanecem no idioma de origem.',
                    'O título descritivo da foto nos créditos foi traduzido; autor, identificação e URL foram mantidos.',
                    'PDF local inspecionado em sete páginas: soluções recolhidas na impressão, caixas divididas e rótulo genérico na capa. Não publicado como exemplo fiel.',
                    'O original chama as tabelas de Figure 2.2 e Figure 2.3: mantido como Figura, sem renumerar.',
                    'A pergunta sobre estudantes termina pedindo gráfico de eleitores no original; inconsistência preservada, não corrigida silenciosamente.'],
    }
    (Path(__file__).parent / 'validacao.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    verify()
