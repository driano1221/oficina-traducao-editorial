# Arquitetura

A menor divisão útil: interface em `app.py`, motor em `tradutor.py`, testes e documentação ao lado. Sem servidor, banco de dados ou fila externa.

## Três caminhos

| Caminho | Unidade traduzida | O que não é reconstruído |
| --- | --- | --- |
| PDF | Texto por página, agrupado em blocos | Geometria original, tabelas semânticas, fórmulas e OCR |
| EPUB | Conteúdo de títulos, parágrafos, listas, células e legendas reconhecidos | Imagens, fórmulas protegidas, CSS e arquivos não selecionados |
| HTML editorial | Elementos do artigo, com notas/legendas tratadas | Layout exato do site |

## EPUB: preservar antes de compor

O motor lê container, manifesto, spine e sumário. Marca os elementos antes de recortar. As imagens necessárias ao HTML ganham nomes derivados do caminho interno para evitar colisões.

Imagens, MathML, SVG, blocos `.math` e marcadores de página recebem placeholders durante a tradução. A resposta precisa conservar chaves, tokens, tags e atributos. Depois o motor restaura os objetos e substitui **apenas o conteúdo dos nós traduzidos** numa cópia do documento original.

Arquivos não alterados do ZIP mantêm seus bytes: imagens, CSS, fontes, sumário e documentos fora do recorte. Nos XHTML alterados, o parser pode normalizar a serialização. O EPUB não é uma cópia binária da origem e formatos incomuns precisam de testes adicionais.

O empacotamento verifica CRC, MIME e XML dos documentos modificados. Não substitui EPUBCheck nem ensaios em leitores reais.

A seleção por capítulos exige inícios em documentos distintos. Se vários capítulos compartilham o mesmo XHTML, o recorte é recusado. Há limites equivalentes para marcadores de página dentro de parágrafos. São recusas explícitas, não truncamento silencioso.

## Tradução e retomada

O Codex CLI recebe texto por stdin, gera resposta final em arquivo e informa eventos JSONL. A execução solicita sandbox somente leitura e ignora a configuração de usuário. O prompt trata o conteúdo do livro como dado, não como instrução. Isso reduz permissões; não é garantia de isolamento completo.

A implementação usa [execução não interativa documentada](https://developers.openai.com/codex/noninteractive). O CLI e suas permissões devem estar configurados pelo usuário.

As chaves de cache incluem conteúdo, modelo, instruções e glossário. Um manifesto de identidade bloqueia reutilização de pasta com outra configuração. No fluxo EPUB/HTML, existe tentativa por bloco e fallback por elemento. A interface mantém ainda uma memória SQLite por segmento na raiz da biblioteca: somente correspondências exatas de ciclos aprovados e estruturalmente válidas são reutilizadas.

A interface captura os campos antes de iniciar a thread de trabalho. Alterações posteriores na tela não mudam a tarefa já iniciada.

## Validação e custo

- PDF: presença de páginas, marcadores, razão de tamanho e possíveis resíduos/repetições.
- EPUB/HTML: contratos de tradução, contagem de objetos, integridade e auditoria bilíngue por modelo.
- Custo: eventos de uso por chamada e equivalente calculado por modelo; dado ausente não vira zero.

Contagem igual de figuras não prova que a figura está legível, e um parecer de LLM não prova equivalência semântica. Revisão visual e humana continuam fora do contrato automatizado.

## Pontos ainda experimentais

A composição HTML/PDF aplica estilo editorial próprio. Fontes e URLs de CSS nem sempre são portáveis para HTML independente. Notas laterais do HTML seguem convenções específicas; não há extrator universal de notas. A triagem reduz a auditoria semântica, mas um livro grande ainda pode produzir muitos trechos de risco. Correções são limitadas a duas rodadas automáticas e podem continuar exigindo revisão humana. Não há testes universais de OCR, bidirecionalidade ou todas as variantes de EPUB.
