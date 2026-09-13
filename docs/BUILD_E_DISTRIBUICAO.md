# Executável e distribuição

## Build local no Windows

```powershell
.\setup.ps1
.\build_exe.ps1
```

O script instala PyInstaller, roda a suíte e produz `dist/OficinaTraducao.exe`. Não precisa de Python instalado na máquina onde o executável será usado. Codex CLI autenticado e navegador continuam sendo dependências externas.

A versão gerada é portátil, sem instalador e sem assinatura digital. O Windows pode exibir avisos de reputação. Não desative mecanismos de segurança automaticamente; valide a origem do arquivo.

## Estado desta publicação

A beta pública distribui o código-fonte. O script de build está disponível, mas não há executável hospedado no GitHub nesta primeira release. Builds pessoais anteriores não foram publicados porque continham ajustes ligados a livros específicos.

## Antes de hospedar um binário

O projeto usa PyMuPDF sob a opção AGPL-3.0. Empacotar o programa não elimina obrigações das licenças das dependências.

Antes de redistribuir um executável, prepare os avisos e textos das licenças dos componentes realmente incluídos, o código-fonte correspondente exigido e as instruções exatas de build. Um link genérico para o repositório não deve ser tratado como auditoria suficiente de um pacote binário inteiro.

Revise também MuPDF, Python/Tcl/Tk, ReportLab, BeautifulSoup, Pillow, PyInstaller e componentes transitivos presentes no pacote. Fontes do Windows não devem ser copiadas para o repositório ou redistribuídas indiscriminadamente.

A [licença do PyMuPDF](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright) oferece AGPL ou opção comercial. Este projeto não adquiriu licença comercial e não afirma que ela seja necessária para todo uso; a publicação adota AGPL. Isso não é parecer jurídico.

## Checklist de release

- Testes e instalação em ambiente limpo.
- Conteúdo sintético ou explicitamente redistribuível.
- Sem livros, traduções privadas, segredos, caminhos pessoais ou logs.
- Dependências e licenças inventariadas.
- Fonte correspondente e instruções compatíveis com o binário.
- Hash SHA-256 do artefato e nota clara sobre assinatura.
