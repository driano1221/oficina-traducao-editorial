# Histórico

## Não lançado — 2026-09-14

- Luna passa a ser o modelo padrão econômico; Terra e Sol continuam disponíveis.
- Memória SQLite reutiliza segmentos estruturalmente válidos entre projetos da biblioteca.
- Correção dirigida e até duas reauditorias enviam somente os IDs reprovados.
- Recortes de capítulo agora terminam no próximo item de sumário do mesmo nível ou superior, sem incorporar divisores de partes.
- Âncoras vazias de navegação do EPUB são protegidas durante a tradução.
- Validação numérica aceita números escritos em inglês convertidos corretamente em algarismos e mostra os valores divergentes.
- Reexecuções removem fontes e blocos obsoletos de escopos anteriores das pastas de trabalho.
- Suíte ampliada para 35 testes.
- Benchmark privado de 140 elementos congelado por hashes e resultados agregados, sem texto protegido no repositório.
- Triagem local de números, fórmulas, HTML e glossário antes da auditoria semântica.
- Auditoria seletiva com payload textual compacto e relatório `validacao_local.json`.
- Cinco regressões reais conhecidas cobertas; redução estimada de 20,4% no payload semântico do benchmark.
- Minilivro sintético de dois capítulos, original e tradução real em EPUB.
- Comparativos visuais de tabela/equação e figura/notas, mais screenshot da interface.
- Fonte reproduzível, verificações de integridade e custo sanitizado.
- Dois testes dos artefatos publicados; suíte com 22 testes.
- Limites da estimativa prévia e do PDF refluído documentados no exemplo.

## 0.1.0-beta — 2026-09-12

Primeira versão pública, em código-fonte.

- Interface Windows, motor PDF/EPUB e fluxo experimental de HTML editorial.
- Biblioteca com original, trabalho, entrega atual e relatórios.
- Recorte EPUB com preservação do restante da seção e dos arquivos não alterados.
- Proteção de objetos e validação de tags/atributos.
- Cache por configuração e equivalente de custo por chamada/modelo.
- 20 testes sintéticos, CI Windows e documentação de origem/limites.
- Build local do executável; sem binário hospedado nesta release.

Conteúdo e ajustes específicos de obras particulares foram excluídos da distribuição.
