# Um livro aberto. Uma tradução verificável.

O exemplo principal agora usa uma obra real em inglês: **Significant Statistics: An Introduction to Statistics**, de John Morgan Russell (2025), publicada pelo Department of Statistics da Virginia Tech, em associação com Virginia Tech Publishing e Open Education Initiative.

Traduzimos a **seção 2.1 completa**, “Descriptive Statistics and Frequency Distributions”. Não é o capítulo 2 inteiro. Os comparativos mostram recortes dessa seção, produzidos pelo motor do aplicativo com GPT-5.6 Sol, sem retoques manuais no texto traduzido.

![Tabela com dados e fórmulas preservados](../../docs/images/statistics-tabela.png)

![Fotografia com legenda traduzida e numeração original](../../docs/images/statistics-figura.png)

## Por que este livro

Além do texto corrido, a seção contém duas tabelas, legenda de fotografia, fórmulas em imagens, referências, links internos e exercícios com soluções expansíveis. É um teste mais realista que uma página de prosa.

O EPUB veio do [repositório oficial da Virginia Tech](https://hdl.handle.net/10919/118481). A [página oficial da obra](https://pressbooks.lib.vt.edu/significantstatistics/) declara **CC BY-SA 4.0**, que permite adaptações com atribuição e compartilhamento pela mesma licença. É uma obra aberta licenciada, **não um livro inteiro em domínio público**.

## Créditos e licença dos comparativos

Russell, John Morgan (2025). *Significant Statistics: An Introduction to Statistics*. Blacksburg: Virginia Tech Department of Statistics. [DOI: 10.21061/significantstatistics](https://doi.org/10.21061/significantstatistics). Copyright © 2025 John Morgan Russell. [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), salvo indicação em contrário.

Atribuições indicadas pela obra: *Introductory Statistics*, de Barbara Illowsky e Susan Dean (OpenStax, CC BY 4.0); *OpenIntro Statistics*, de David Diez, Mine Çetinkaya-Rundel e Christopher D. Barr; e *Introductory Statistics for the Life and Biomedical Sciences*, de Julie Vu e David Harrington (os dois últimos, CC BY-SA 3.0 segundo os créditos desta edição).

A fotografia da Figura 2.1 é de Staff Sgt. William Greeson / U.S. Marine Corps (2009), identificada como domínio público nos [créditos da seção](https://pressbooks.lib.vt.edu/significantstatistics/chapter/descriptive-statistics-and-frequency-distributions/) e disponível no [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:US_Navy_090821-M-0440G-043_Voting_ballots_organized_and_arranged_for_counting_by_Afghan_presidential_election_workers_at_a_local_school_in_the_Nawa_District.jpg).

Alterações: seleção da seção, tradução automática para pt-BR e montagem dos comparativos por driano1221, com assistência de IA. **Os comparativos `statistics-tabela.png` e `statistics-figura.png` e a tradução neles reproduzida são distribuídos sob CC BY-SA 4.0**, preservadas as exceções acima. Não são uma tradução oficial, nem implicam aprovação dos autores ou da universidade. A licença AGPL do código não substitui as licenças deste conteúdo.

## O que foi conferido

| Evidência | Resultado |
| --- | --- |
| Texto | 119 elementos traduzidos; leitura comparativa da amostra e auditoria automática |
| Tabelas | 2 tabelas, 54 células de dados; mesmos valores numéricos e unidades |
| Imagens | 13 ocorrências, incluindo 12 fórmulas rasterizadas; arquivos idênticos |
| Identificação | Figura 2.1, Figura 2.2 e Figura 2.3 mantidas |
| Estrutura | Tags e atributos do corpo iguais, salvo `lang`/`xml:lang` dos nós traduzidos |
| Recursos | 28 arquivos fora do XHTML traduzido byte a byte intactos |
| Links internos | Todos apontam para identificadores existentes |
| Exercícios | Os quatro rótulos `Solution` passaram a `Solução`, preservando `details/summary` |

O original chama as tabelas de **Figure 2.2 e Figure 2.3**. Mantivemos **Figura**, sem inventar outra numeração. A mesma política preservou os pontos decimais e as polegadas: traduzir não é converter os dados.

Os screenshots foram capturados no Chrome, com janela de leitura de 520 px, os mesmos arquivos CSS/fontes nos dois lados e ampliação uniforme de 135% na montagem. Cortamos apenas o enquadramento: a caixa de exemplo até a legenda da tabela, e a figura com sua legenda. O EPUB e seus estilos não foram redesenhados para o screenshot. Pequenas diferenças de largura e quebra de linha decorrem do texto em português e do layout automático da tabela.

## O que o exemplo também revelou

- O motor não incluía `summary` entre os elementos traduzíveis. Foi corrigido e ganhou teste de regressão.
- As primeiras tentativas alteraram atributos `aria-label`. A validação recusou as respostas; a instrução foi reforçada e a execução retomada. Não afrouxamos a validação para aceitar a saída.
- A auditoria automática aprovou os 119 pares, mas não substitui revisão: o título descritivo da foto nos créditos também foi traduzido. Autor, identificação e URL permanecem; não equivale a preservação literal de toda referência bibliográfica.
- A fonte contém uma pergunta sobre horas trabalhadas por estudantes que termina pedindo um gráfico de eleitores. A inconsistência foi preservada, não corrigida silenciosamente.
- Os textos alternativos e alguns metadados continuam em inglês. Esta amostra não certifica acessibilidade totalmente localizada.
- A exportação PDF local tem sete páginas e composição própria. A inspeção visual encontrou soluções recolhidas que não aparecem impressas e divisões de caixas entre páginas; a capa também usa um rótulo genérico de capítulos. **Por isso, o PDF não é publicado como demonstração de fidelidade.** O EPUB mantém as soluções expansíveis.

## Custo observado

**US$ 0,792213 de equivalente API** para esta demonstração, incluindo as tentativas recusadas, a retomada e a auditoria: 20 chamadas, 345.362 tokens de entrada (242.560 em cache) e 14.199 de saída. Pela tabela de referência do app e câmbio informado de R$ 5,13/US$, isso corresponde a **R$ 4,06**.

Não é cobrança comprovada. A execução usou login ChatGPT; o app não consulta faturas ou consumo financeiro real do plano. O trabalho de pesquisa, programação e preparação desta conversa não está contabilizado nesses números. Veja [o relatório público sem caminhos pessoais](validacao.json).

## Reproduzir

No PowerShell, a partir da raiz do projeto, com o ambiente instalado:

```powershell
New-Item -ItemType Directory -Force tmp/significant-statistics
curl.exe -L --fail "https://vtechworks.lib.vt.edu/bitstreams/0345ade7-4647-4dcc-8d6b-b88c172b3500/download" -o tmp/significant-statistics/original-completo.epub
.venv/Scripts/python.exe examples/significant-statistics/preparar.py
.venv/Scripts/python.exe examples/significant-statistics/preparar.py --traduzir
.venv/Scripts/python.exe examples/significant-statistics/verificar.py
```

`--traduzir` consome uso do Codex. O preparador verifica o SHA-256 da edição consultada, cria um pacote com somente a seção 2.1 e seus recursos, ajusta metadados/navegação para o recorte e mantém o XHTML original intacto. A tradução usa o mesmo `run_job` da interface. Reutiliza blocos válidos ao retomar; se mudar as instruções, use outra pasta de trabalho. Novas execuções podem produzir traduções diferentes.

Para regenerar os screenshots, instale opcionalmente Node.js e Playwright fora das dependências do app:

```powershell
npm install --prefix tmp/captura playwright
$env:PLAYWRIGHT_MODULE = (Resolve-Path tmp/captura/node_modules/playwright).Path
node examples/significant-statistics/capturar.cjs
```

Chrome é usado no caminho padrão do Windows; `CHROME_PATH` permite apontar outro executável compatível.

O livro completo, o recorte EPUB, fontes tipográficas e logs ficam somente em `tmp/significant-statistics`, ignorado pelo Git. O repositório publica **os dois comparativos, o relatório e os scripts**, não uma cópia do livro inteiro.
