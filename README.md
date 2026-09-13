# Oficina de Tradução Editorial

Livro entra. Tradução revisável sai.

Aplicativo local para Windows que traduz PDF e EPUB para português brasileiro, organiza original, entrega e relatórios e registra uma estimativa de custo a partir do uso informado pelo Codex CLI.

Nasceu de uma necessidade de estudo: traduzir sem transformar notas em parágrafos soltos, perder legendas ou desmontar o livro inteiro para trocar o idioma.

> O caminho mais fiel hoje é EPUB → EPUB: substituir texto dentro do pacote original. PDF → PDF ainda é um modo de estudo, não uma réplica da diagramação.

[![Testes](https://github.com/driano1221/oficina-traducao-editorial/actions/workflows/tests.yml/badge.svg)](https://github.com/driano1221/oficina-traducao-editorial/actions/workflows/tests.yml)

## Comece aqui

| Quero… | Onde |
| --- | --- |
| Instalar e traduzir | [Como usar](docs/COMO_USAR.md) |
| Entender o que é preservado | [Arquitetura e limites](docs/ARQUITETURA.md) |
| Conferir os testes | [Auditoria](docs/AUDITORIA.md) |
| Gerar o executável Windows | [Build e distribuição](docs/BUILD_E_DISTRIBUICAO.md) |
| Entender a origem do projeto | [Origem e próximos passos](docs/ORIGEM_E_LIMITES.md) |
| Contribuir | [CONTRIBUTING](CONTRIBUTING.md) |

## O que ele faz

- Interface em português para escolher arquivo, páginas ou primeiros capítulos.
- EPUB estruturado: troca o conteúdo dos elementos traduzidos e mantém os demais arquivos do pacote.
- Preserva imagens e protege fórmulas no fluxo EPUB. Texto dentro de imagens permanece no idioma original.
- Mantém links, identificadores e atributos dos elementos traduzidos; rejeita respostas que alterem essa estrutura.
- Usa glossário editável e cache por conteúdo, modelo e instruções.
- Separa livros e configurações diferentes em projetos distintos.
- Gera relatórios de estrutura e, nos modos editoriais, revisão bilíngue automática.
- Mostra estimativa antes da execução e equivalente API ao final, quando há dados de uso.

## Escolha o caminho

| Entrada | Entrega | Fidelidade nesta beta |
| --- | --- | --- |
| EPUB com capítulos reconhecidos ou marcadores de página | EPUB + PDF + HTML + texto | EPUB mantém imagens, CSS, navegação e conteúdo fora do recorte; PDF/HTML são refluídos |
| PDF com texto extraível | PDF + HTML + Markdown | Imagem da página original para conferência e texto traduzido; sem reconstrução geométrica |
| HTML oficial com `<article>`, informado manualmente | PDF + HTML + texto | Experimental: traduz os artigos inteiros; o intervalo do PDF não recorta essas URLs |

EPUB não tem paginação fixa. O recorte por página só funciona com marcadores `pg_N` compatíveis. Capítulos são reconhecidos por títulos como `Chapter 1`, `Capítulo 1` e `第1章`, em documentos separados. Nem todo EPUB usa esse formato.

## Rodar

Requisitos: Windows 10/11, Python 3.11 com Tkinter, Codex CLI instalado e autenticado, acesso a um modelo compatível. Chrome ou Edge é necessário para o PDF editorial. A tradução exige internet.

No PowerShell, dentro da pasta do projeto:

```powershell
.\setup.ps1
.\iniciar.ps1
```

Para o executável local:

```powershell
.\build_exe.ps1
```

Saída: `dist/OficinaTraducao.exe`. O executável empacota Python e a interface; **não inclui o Codex CLI, login, modelo nem navegador**.

A primeira publicação contém código-fonte e instruções de build. Não há binário público pronto para download nesta beta.

## Saídas organizadas

```text
resultados/
└── nome_do_livro_identificador/
    ├── LEIA-ME.md
    ├── projeto.json
    ├── 01_original/        # cópia do arquivo recebido
    ├── 02_trabalho/        # extração, blocos, cache e uso
    ├── 03_entrega_atual/   # arquivos para leitura e seus ativos
    └── 04_relatorios/      # QA, manifesto e custo
```

Repetir a mesma configuração permite retomar blocos válidos. Mudar o recorte, modelo ou instruções cria outro projeto na interface. Pela CLI, use uma pasta nova ao alterar a configuração.

## Custo não é fatura

A estimativa usa uma tabela local de preços de referência e o câmbio informado. O relatório final soma as chamadas registradas por modelo, incluindo tentativas e auditoria.

**Equivalente API ≠ valor cobrado na sua conta.** O app não consulta faturas, saldo ou limites do plano. Falta de telemetria aparece como indisponível, não como tradução grátis. Veja [custos e privacidade](docs/COMO_USAR.md#custos-e-privacidade).

## Mapa

```text
app.py                interface e organização da biblioteca
tradutor.py           extração, tradução, exportação, QA e custo
glossario.json        terminologia padrão, editável
tests/                testes com conteúdo sintético
docs/                 uso, decisões, limites e validação
.github/workflows/    testes no Windows
```

## Estado

Beta de estudo. Há 20 testes automatizados com dados sintéticos, sem chamadas pagas, além de um teste manual curto da integração com Codex CLI. Isso verifica contratos do pipeline; não prova qualidade de tradução em qualquer livro.

Não faz OCR, não remove DRM, não traduz diagramas rasterizados automaticamente e não promete fidelidade visual absoluta. Uma revisão humana continua necessária. Não use documentos não confiáveis ou sensíveis sem avaliar os riscos.

## Origem e licença

Inspirado no fluxo do [translate-book](https://github.com/deusyu/translate-book), de Rainman, distribuído sob MIT. O foco aqui é uma aplicação Windows com preservação estrutural de EPUB, organização das entregas e rastreabilidade.

Não é um novo modelo de tradução, nem uma reivindicação de ter inventado tradução de livros com LLMs. É um projeto de aplicação e integração, desenvolvido com assistência de IA e orientado por problemas reais de uso.

Código deste projeto sob [AGPL-3.0](LICENSE), considerando o uso de PyMuPDF. Créditos e dependências em [NOTICE](NOTICE.md). Sem vínculo oficial com OpenAI ou com os projetos citados.

O repositório não distribui livros, traduções de obras, credenciais ou arquivos pessoais. Use apenas materiais para os quais você tenha os direitos ou permissões necessários.
