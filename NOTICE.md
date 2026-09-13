# Créditos e licenças

Copyright (c) 2026 driano1221. Código deste projeto: GNU Affero General Public License, versão 3 (AGPL-3.0). Consulte LICENSE.

## Inspiração

[translate-book](https://github.com/deusyu/translate-book), de Rainman: inspiração do fluxo de tradução em blocos com glossário. Não há cópia de seus scripts no pacote de execução desta aplicação. O aviso MIT é mantido abaixo por atribuição e transparência.

> MIT License
>
> Copyright (c) 2025 Rainman
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.

## Componentes

| Componente | Uso | Licença / origem |
| --- | --- | --- |
| PyMuPDF / MuPDF | Extração e inspeção PDF | [AGPL-3.0 ou comercial](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright); aqui, opção AGPL |
| ReportLab | Composição do PDF de estudo | [BSD](https://hg.reportlab.com/hg-public/reportlab/file/tip/LICENSE.txt) |
| BeautifulSoup | Leitura e transformação de HTML | [MIT](https://www.crummy.com/software/BeautifulSoup/) |
| Python e Tkinter/Tcl/Tk | Execução e interface | [Licenças da distribuição Python](https://docs.python.org/3/license.html) |
| PyInstaller | Build opcional | [GPL com exceção de empacotamento](https://pyinstaller.org/en/stable/license.html) |
| KaTeX | Fórmulas no HTML, via CDN | [MIT](https://github.com/KaTeX/KaTeX/blob/main/LICENSE) |
| Codex CLI | Serviço externo de tradução | [Projeto e licença](https://github.com/openai/codex); não incluído no executável |

As dependências são instaladas separadamente. Os avisos delas permanecem aplicáveis. Para binários, leia docs/BUILD_E_DISTRIBUICAO.md e inventarie também as dependências transitivas.

Não distribuímos livros privados, traduções privadas, fontes extraídas de obras ou credenciais. Os únicos trechos de terceiros publicados são os comparativos licenciados descritos abaixo. A licença do código não concede direitos sobre documentos processados.

Exceção autoral de demonstração: texto, dados fictícios, CSS e diagrama em `examples/minilivro/fonte`, bem como os dois EPUBs e comparativos derivados dessa amostra, são dedicados sob [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). Foram criados com assistência de IA especificamente para este projeto, sem conteúdo do livro Patterns. Scripts continuam sob AGPL-3.0. O screenshot da interface documenta o aplicativo e não muda a licença do código.

## Exemplo de livro aberto

`docs/images/statistics-tabela.png` e `docs/images/statistics-figura.png` reproduzem trechos da seção 2.1 de *Significant Statistics: An Introduction to Statistics*, copyright © 2025 John Morgan Russell, Virginia Tech, [DOI](https://doi.org/10.21061/significantstatistics). A obra e estes comparativos/adaptações são licenciados sob [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), salvo indicação em contrário. A fotografia da Figura 2.1, de William Greeson / U.S. Marine Corps (2009), é identificada como domínio público na fonte.

Recorte, tradução automática para pt-BR e montagem: driano1221, com assistência de IA. Sem endosso dos autores ou da universidade. Consulte os [créditos completos, obras-base, fonte e alterações](examples/significant-statistics/README.md#créditos-e-licença-dos-comparativos). Não redistribuímos o EPUB completo nem os arquivos de fontes tipográficas desta obra. Scripts continuam sob AGPL-3.0.

OpenAI, Codex e nomes dos projetos relacionados pertencem aos seus respectivos titulares. Não há afiliação oficial.
