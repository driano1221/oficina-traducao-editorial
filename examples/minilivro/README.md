# Um livro pequeno, uma verificação concreta

**Field notes: a synthetic learning guide** é um minilivro autoral com dois capítulos. O primeiro explica erro de predição com quatro observações inventadas; o segundo interpreta o gráfico e distingue descrição de causalidade. Não é um estudo empírico nem um trecho adaptado de outro livro.

Texto, dados, diagrama e estilo foram criados com assistência de IA para esta demonstração. A tradução foi produzida pelo motor público, commit `d06f9c1`, usando GPT-5.6 Sol, sem edição manual do resultado. Licença da amostra: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). Scripts: AGPL-3.0.

## Arquivos

| Arquivo | O que é |
| --- | --- |
| [Original](publicados/original.epub) | EPUB em inglês, com os dois capítulos |
| [Traduzido](publicados/traduzido.epub) | Saída real do motor em pt-BR |
| [Validação](publicados/validacao.json) | Hashes, objetos verificados, auditoria e custo sem dados pessoais |
| `fonte/` | XHTML, CSS e SVG autorais que compõem o original |
| `gerar.py` | Empacota a fonte e, opcionalmente, executa a tradução |
| `preparar_vitrine.py` | Verifica a execução e monta os comparativos a partir dos EPUBs |

## Reproduzir

Na raiz do repositório, depois de instalar as dependências:

```powershell
python examples/minilivro/gerar.py
```

O comando acima não chama modelo. Reutiliza o EPUB existente quando o conteúdo da fonte não mudou.

```powershell
python examples/minilivro/gerar.py --traduzir
python examples/minilivro/preparar_vitrine.py
```

**`--traduzir` consome uso do Codex CLI.** A execução fica em `tmp/demo-biblioteca-final`, separada dos EPUBs publicados. Mudar fonte/modelo/instruções exige arquivar a pasta de trabalho anterior ou usar outro caminho no gerador, por causa da proteção de identidade. Não apague sua biblioteca para reproduzir um exemplo.

O modelo recebe as instruções padrão mais: “Preserve a sigla MSE também na prosa, pois ela identifica a equação matemática preservada.” O glossário padrão do repositório permanece ativo. A tradução pode variar entre execuções.

## Como as imagens foram feitas

Os arquivos de cada EPUB foram extraídos para pastas de prévia, sem alterar texto ou CSS. Dois iframes do mesmo tamanho renderizam os capítulos no Chrome. Cabeçalho, rótulos de idioma e moldura ficam **fora** dos documentos. O tamanho vertical acomoda os dois conteúdos inteiros; nenhuma passagem foi apagada para melhorar o comparativo.

O preparador gera `tmp/demo-preview/comparativo-1.html` e `comparativo-2.html`. Para refazer as capturas, abra essas páginas no Chrome a 1500 px de largura, ajuste os iframes à altura integral dos capítulos e capture a página completa. Na captura publicada, o painel mais alto determina a altura comum. As imagens ficam em `docs/images/`.

A interface foi fotografada na versão pública, após analisar uma cópia da amostra em `C:\Users\Public\Documents\OficinaDemo`. Não há caminhos de usuário particular. Ela mostra a configuração, não simula uma execução concluída.

## Resultado e limites

- 48 elementos traduzidos e revisados pela auditoria automática.
- CSS, SVG, metadados e navegação mantêm os bytes originais.
- IDs e links de notas são iguais; os destinos foram conferidos no conteúdo.
- Valores das 20 células de dados e a fórmula MathML foram preservados.
- Legendas continuam identificadas como Tabela 1 e Figura 1.
- Ambos os capítulos foram lidos e conferidos visualmente, sem sobreposição ou corte nos comparativos.

MSE e erro absoluto médio são 0,5 neste conjunto. Isso não significa que as métricas sejam equivalentes em geral. O gráfico representa exatamente as quatro linhas da tabela; não é uma imagem decorativa gerada por IA.

Na primeira execução, MSE virou EQM na prosa e permaneceu MSE na fórmula protegida. A auditoria automática aprovou esse resultado. A revisão identificou a inconsistência e levou a uma nova execução com a instrução acima. Isso ilustra por que “QA aprovado” não dispensa revisão.

O EPUB mantém o sumário e os textos alternativos das imagens no idioma original. O diagrama usa símbolos independentes do idioma: não estamos demonstrando OCR nem tradução dentro de imagens. Os screenshots mostram XHTML do EPUB em Chrome, não um leitor EPUB específico.

**O PDF refluído não é o comparativo publicado.** Ele foi inspecionado e gerou quatro páginas, deixando o último item da lista e a nota numa página adicional. Essa limitação de paginação foi mantida como evidência local, não retocada ou apresentada como fidelidade perfeita. Não há download de PDF nesta amostra.

## Custo medido

Execução final, incluindo auditoria: US$ 0,087464 de equivalente API (aproximadamente R$ 0,45 ao câmbio de referência de 5,13). Incluindo também a primeira execução: US$ 0,179140, aproximadamente R$ 0,92.

A estimativa prévia na interface era US$ 0,02: subestimou instruções, contexto do CLI e auditoria. Os números finais usam os eventos registrados. Não representam cobrança real nem incluem o trabalho de desenvolvimento desta demonstração. A conta utiliza autenticação própria; fatura e franquia não foram consultadas.
