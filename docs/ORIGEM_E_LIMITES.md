# Origem e próximos passos

## De onde veio

O ponto de partida foi o [translate-book](https://github.com/deusyu/translate-book): dividir textos, usar glossário, traduzir em blocos e validar. Ele recebe crédito explícito no README e no NOTICE.

Este repositório publica a aplicação local criada a partir das necessidades do fluxo de estudo, não uma cópia do repositório original com outro nome. A atribuição não depende de chamar a ideia de inédita.

O trabalho específico está na interface, na organização dos projetos, no tratamento separado de EPUB, no recorte sem perda do restante do pacote, nos contratos de estrutura e no registro de custo. São decisões de engenharia de produto, não invenções científicas.

Desenvolvimento realizado com assistência de IA, incluindo implementação e documentação. A manutenção e a decisão de publicar são do autor do repositório.

## Projetos relacionados

- [translate-book](https://github.com/deusyu/translate-book): inspiração do fluxo por blocos e glossário.
- [PDFMathTranslate](https://github.com/Byaidu/PDFMathTranslate): tradução de PDF com foco em formato.
- [BabelDOC](https://github.com/funstory-ai/BabelDOC): processamento e tradução de documentos.
- [Docling](https://github.com/docling-project/docling): conversão estruturada de documentos.
- [EPUBCheck](https://github.com/w3c/epubcheck): validação do formato EPUB.

São referências, não dependências embutidas. Este projeto não demonstrou superioridade sobre elas e não apresenta benchmark comparativo.

## Próximos passos, não funcionalidades prontas

1. Corpus sintético e de domínio público com figuras, tabelas e notas variadas.
2. EPUBCheck e comparação de links/objetos antes e depois em todo o pacote.
3. Suporte a capítulos por fragmento no mesmo XHTML.
4. Auditoria semântica em lotes e revisão visual assistida.
5. Avaliar um motor PDF especializado, com revisão de licença, antes de prometer layout fiel.
6. Instalação e distribuição de executável com pacote de licenças e fontes correspondente.

O objetivo é traduzir sem perder a estrutura editorial. A beta já testa parte desse caminho; não promete resolvê-lo para todo livro.
