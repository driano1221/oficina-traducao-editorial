# Auditoria da beta pública

Data: 12/09/2026.

## Escopo

Preparação de uma cópia pública separada do ambiente pessoal. Livros, traduções, imagens das obras, caches, credenciais e executáveis antigos não fazem parte do repositório.

As correções literais para obras específicas foram retiradas do motor público. Os exemplos usados nos testes foram escritos para o projeto.

## Evidência reproduzível

```powershell
python -m unittest discover -s tests -v
python tradutor.py self-test
python -m py_compile tradutor.py app.py
```

20 testes locais passaram em Python 3.11. O workflow do GitHub repete a suíte no Windows com Python 3.11 e 3.12.

| Contrato | Cobertura |
| --- | --- |
| Escopo | Intervalos, capítulos, marcadores, recorte dentro de parágrafo e capítulos compartilhando XHTML |
| EPUB parcial | Texto posterior mantido, segundo documento intacto, sumário/CSS/imagem intactos |
| Objetos | Imagens e matemática protegidas, tabela e legenda conservadas, link de nota preservado |
| Resposta do modelo | Chaves e estrutura, atributo alterado recusado, placeholder ausente recusado |
| Custos | Cache de entrada, modelos distintos, preço desconhecido, uso ausente |
| Biblioteca | Projetos separados por configuração, identidade bloqueada, cópia do original e ativos |

A suíte usa tradutor, auditor e impressor PDF simulados. Portanto ela **não valida tradução real nem renderização visual do PDF**.

Houve também um teste manual real, curto, com Codex CLI e GPT-5.6 Luna: duas frases sintéticas, uma contendo um link HTML. O processo retornou código 0, tradução em pt-BR, atributo preservado e registro de uso. O teste não envia nem publica livros. Não constitui benchmark de qualidade.

## Ajustes feitos antes de publicar

- Remoção de remendos e conteúdo ligados a obras particulares.
- Reempacotamento por nós traduzidos, preservando o restante de uma seção recortada.
- Proteção de imagens e matemática e validação de atributos/links.
- Recusa de cortes ambíguos, em vez de perder texto.
- Separação de configurações para evitar reaproveitar arquivos incompatíveis.
- Cópia dos ativos das páginas originais na entrega HTML.
- Captura dos campos da interface antes da thread e correção da apresentação de erros.
- Custo por modelo e estado indisponível quando falta telemetria.

## O que não está certificado

Fidelidade visual universal, EPUBCheck, tradução literária, suporte a qualquer estrutura EPUB, OCR, notas de todos os estilos, custo exato da conta e redistribuição de qualquer obra. O histórico pessoal com três livros não foi publicado nem convertido em prova de cobertura geral.

Antes de promover a estável: acrescentar corpus aberto, revisão humana cega, validação com EPUBCheck, comparação visual em leitores reais e testes do instalador em Windows limpo.
