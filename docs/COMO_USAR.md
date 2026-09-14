# Como usar

## Preparação

1. Instale Python 3.11 para Windows, incluindo Tkinter e o lançador `py`.
2. Instale e autentique o Codex CLI conforme a [documentação oficial](https://developers.openai.com/codex/cli).
3. Confirme `codex --version` e `codex login status` no terminal.
4. Instale Chrome ou Edge para gerar PDF a partir de EPUB/HTML.
5. Na pasta do projeto, execute `.\setup.ps1` e depois `.\iniciar.ps1`.

Se o PowerShell bloquear scripts, use os comandos Python diretamente, respeitando as políticas do computador:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

## Primeira tradução

Escolha um PDF/EPUB e uma pasta de biblioteca fora do repositório, se preferir. Leia o diagnóstico de entrada. Comece por um recorte curto.

- PDF: `1-10`, `1-10,15` ou livro inteiro. As páginas são físicas, contando capa e sumário.
- EPUB: primeiros N capítulos reconhecidos ou todos os capítulos detectados. O reconhecimento aceita títulos como `1. Introduction`, `Chapter 1`, `Capítulo 1` e `第1章`, sem tratar seções decimais como `2.1 Background` como capítulos. Isso não equivale necessariamente ao livro inteiro: apêndices e matéria inicial dependem do sumário e do spine.
- EPUB por páginas: sequência contínua começando em 1. Exige marcadores `pg_N` com `role="doc-pagebreak"`. Limites dentro de parágrafos são recusados para não perder texto.
- URL editorial: opção experimental, apenas em PDF. Cada URL deve conter `<article>`. Todo o artigo é processado, independentemente das páginas selecionadas no PDF.

Escolha um modelo disponível na sua conta. O campo aceita um identificador manual; modelos sem preço local podem traduzir, mas não têm estimativa conhecida. Ajuste o câmbio e as instruções. O glossário padrão está em `glossario.json`; adapte-o à área do livro.

Clique em **Traduzir e gerar entrega**. O botão não publica nada na internet: gera arquivos na biblioteca local. Pode haver novas tentativas automáticas e revisão bilíngue, que também consomem uso.

Não feche o aplicativo durante o processamento. Não há botão de cancelamento nesta beta. Em caso de interrupção, retome com a mesma configuração. Blocos incompletos são processados novamente.

## Conferência

Abra `03_entrega_atual` e `04_relatorios`. O estado `aprovado` significa apenas que as verificações implementadas não encontraram problemas; não é certificação editorial.

Confira pelo menos uma tabela, uma equação, uma figura com legenda, notas e links. Em EPUB parcial, confira também o primeiro trecho fora do escopo. Compare com o original em mais de um leitor, se possível.

Os nomes e links da navegação original do EPUB são mantidos; os rótulos do sumário podem continuar no idioma original. O EPUB mantém o pacote de origem. PDF/HTML usam composição própria e podem mudar paginação, fontes e quebras.

## CLI

```powershell
.\.venv\Scripts\python.exe tradutor.py translate "C:\Livros\exemplo.pdf" --pages "1-10" --output "C:\Traducoes\exemplo_pdf"
.\.venv\Scripts\python.exe tradutor.py translate "C:\Livros\exemplo.epub" --chapters 2 --output "C:\Traducoes\exemplo_epub"
```

A CLI escreve diretamente em `--output`; as quatro pastas de biblioteca são organizadas pela interface. Não reutilize a pasta para outro arquivo ou configuração. O bloqueio de identidade evita misturar caches, não é um sistema de versionamento nem um bloqueio entre processos: execute um trabalho por pasta de cada vez. Na interface, `memoria_traducao.sqlite3` fica na raiz da biblioteca e reaproveita segmentos idênticos. Na CLI, use `--memory-db CAMINHO` para obter o mesmo comportamento entre pastas.

## Custos e privacidade

A tabela local, conferida em 12/09/2026, usa preços por milhão de tokens:

| Modelo | Entrada | Entrada em cache | Saída |
| --- | ---: | ---: | ---: |
| GPT-5.6 Luna | US$ 0,20 | US$ 0,02 | US$ 1,20 |
| GPT-5.6 Terra | US$ 2,00 | US$ 0,20 | US$ 12,00 |
| GPT-5.6 Sol | US$ 4,00 | US$ 0,40 | US$ 20,00 |

Fontes oficiais: [Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna), [Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra), [Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol). Os valores podem mudar; não há atualização automática.

O cálculo simples não reproduz descontos, impostos, tarifas de ferramentas, escrita de cache nem sobretaxas por contexto longo. A auditoria envia somente os pares escolhidos pela triagem de risco; uma correção posterior envia somente os IDs reprovados. Ainda assim, recortes grandes podem consumir bastante contexto. Confira a fatura no serviço utilizado; login ChatGPT pode consumir franquia/créditos, e não torna o uso gratuito.

Os trechos traduzidos, o glossário e as instruções são enviados à OpenAI pelo Codex CLI. Os arquivos de trabalho ficam no computador. O app não tem backend próprio nem pede a sua chave; usa a autenticação existente do CLI. Não publique sua biblioteca, logs ou relatórios sem revisão.

O modo editorial usa KaTeX de CDN para renderizar certas fórmulas em HTML/PDF. Ativos externos e estilos de uma fonte podem exigir rede. A saída não é garantidamente offline.

Trate EPUB e HTML como conteúdo ativo, não como formatos sanitizados. Use apenas fontes confiáveis. Não há remoção de DRM nem busca/download de livros no aplicativo.
