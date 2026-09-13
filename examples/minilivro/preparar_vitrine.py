"""Verifica a execução local e prepara comparativos sem alterar a tradução."""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
WORK = REPO / 'tmp/demo-biblioteca-final/02_trabalho'
PREVIEW = REPO / 'tmp/demo-preview'
ASSETS = REPO / 'docs/images'


def prepare():
    PREVIEW.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'publicados/original.epub'
    translated = WORK / 'livro_ptbr.epub'
    qa = json.loads((WORK / 'relatorio_qa.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(source.read_bytes()).hexdigest() == qa['sha256_origem']
    checks = {}
    with zipfile.ZipFile(source) as before, zipfile.ZipFile(translated) as after:
        assert before.namelist() == after.namelist()
        assert after.testzip() is None
        for name in before.namelist():
            if name not in ('EPUB/chapter1.xhtml', 'EPUB/chapter2.xhtml'):
                assert before.read(name) == after.read(name), name
        checks['arquivos_fora_do_texto_intactos'] = True
        for chapter in (1, 2):
            name = f'EPUB/chapter{chapter}.xhtml'
            original_soup = BeautifulSoup(before.read(name), 'html.parser')
            translated_soup = BeautifulSoup(after.read(name), 'html.parser')
            assert [n.get('id') for n in original_soup.select('[id]')] == [n.get('id') for n in translated_soup.select('[id]')]
            assert [n.get('href') for n in original_soup.select('a[href]')] == [n.get('href') for n in translated_soup.select('a[href]')]
            assert [n.get_text() for n in original_soup.select('td')] == [n.get_text() for n in translated_soup.select('td')]
            assert [str(n) for n in original_soup.select('math')] == [str(n) for n in translated_soup.select('math')]
            assert not translated_soup.select('[data-tr-id], [data-epub-node], [data-epub-src]')
            checks[f'capitulo_{chapter}_ids_links_dados_formulas'] = True
        for label, archive in [('original', before), ('traduzido', after)]:
            folder = PREVIEW / label
            folder.mkdir(exist_ok=True)
            # Só os arquivos conhecidos do minilivro; não extrai ZIPs arbitrários.
            for name in ('chapter1.xhtml', 'chapter2.xhtml', 'style.css', 'measurements.svg'):
                (folder / name).write_bytes(archive.read('EPUB/' + name))
    shutil.copy2(translated, ROOT / 'publicados/traduzido.epub')
    first_cost_path = REPO / 'tmp/demo-biblioteca/02_trabalho/custo.json'
    first_cost = json.loads(first_cost_path.read_text(encoding='utf-8')) if first_cost_path.exists() else None
    report = {
        'data': '2026-09-13', 'motor_commit': 'd06f9c1', 'modelo': qa['custo']['modelo'],
        'origem': 'Minilivro sintético autoral, sem trechos de terceiros',
        'sha256_original': hashlib.sha256(source.read_bytes()).hexdigest(),
        'sha256_traduzido': hashlib.sha256(translated.read_bytes()).hexdigest(),
        'elementos': qa['elementos_traduzidos'], 'objetos': qa['estrutura_saida'],
        'verificacoes': checks, 'auditoria_automatica': qa['auditoria_semantica'],
        'custo_equivalente_api_usd_execucao_final': qa['custo']['custo_equivalente_api_usd'],
        'custo_equivalente_api_usd_incluindo_primeira_tentativa': round(first_cost['custo_equivalente_api_usd'] + qa['custo']['custo_equivalente_api_usd'], 6) if first_cost else None,
        'cobranca_real_verificada': False,
        'observacao': 'Primeira execução localizou MSE para EQM na prosa. Nova execução preservou a sigla por instrução editorial explícita. Não houve retoque manual da tradução. Comparativos mostram XHTML do EPUB, não o PDF refluído.',
    }
    (ROOT / 'publicados/validacao.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    for chapter, title, detail in [(1, 'Texto muda. Estrutura permanece.', 'Tabela numerada, valores, equação e chamada de nota.'), (2, 'A figura fica. A legenda acompanha.', 'Imagem original, legenda traduzida e notas com retorno.')]:
        html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"/><title>Comparativo {chapter}</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#e8eeea;color:#183e43;font:16px Arial,sans-serif;padding:32px 34px}}
header{{display:flex;align-items:end;justify-content:space-between;margin-bottom:24px}}.brand{{font-size:11px;font-weight:bold;letter-spacing:2px;margin-bottom:12px}}h1{{font:normal 36px Georgia,serif;letter-spacing:-.6px;margin:0 0 8px}}header p{{margin:0;color:#526c68;font-size:15px}}.pill{{border:1px solid #b5c9c1;border-radius:30px;padding:10px 14px;font:600 11px Arial,sans-serif;letter-spacing:1px}}
main{{display:grid;grid-template-columns:1fr 1fr;gap:22px}}section{{background:#fffdf8;box-shadow:0 3px 15px #163e4310;border:1px solid #cbd6cc;border-radius:8px;overflow:hidden}}.label{{padding:15px 22px;background:#f3f5ee;color:#4c6761;font-size:11px;font-weight:bold;letter-spacing:1.5px;border-bottom:1px solid #dae1d5}}.pt{{background:#174c4e;color:#e6f2e9}}iframe{{display:block;width:100%;height:1250px;border:0;background:#fffdf8}}footer{{display:flex;justify-content:space-between;gap:20px;font-size:12px;line-height:1.5;color:#617970;margin-top:20px}}
</style></head><body><header><div><div class="brand">OFICINA DE TRADUÇÃO EDITORIAL / EXEMPLO REAL DO APP</div><h1>{title}</h1><p>{detail}</p></div><div class="pill">EPUB → EPUB</div></header><main><section><div class="label">01 / ORIGINAL EM INGLÊS</div><iframe title="Original" src="original/chapter{chapter}.xhtml"></iframe></section><section><div class="label pt">02 / TRADUÇÃO PARA PT-BR</div><iframe title="Tradução" src="traduzido/chapter{chapter}.xhtml"></iframe></section></main><footer><span>Conteúdo sintético autoral • Sem páginas de livros de terceiros</span><span>Mesmo CSS nos dois lados • Tradução sem retoques manuais</span></footer></body></html>'''
        (PREVIEW / f'comparativo-{chapter}.html').write_text(html, encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    prepare()
