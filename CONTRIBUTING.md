# Contribuir

Comece pelo [README](README.md) e pela [arquitetura](docs/ARQUITETURA.md). Uma correção pequena com teste reproduzível vale mais que outra camada de abstração.

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Ao abrir uma issue, informe formato, tipo de recorte, Python/Windows/Codex CLI, erro e resultado esperado. Remova caminhos pessoais, dados de conta e texto de obras protegidas. Prefira um EPUB sintético mínimo.

Não envie livros, traduções de terceiros, chaves, cookies, executáveis ou capturas contendo material sem autorização de redistribuição. Fixtures devem ser sintéticas ou ter licença explícita.

PRs devem explicar o problema, o contrato alterado e como verificar. Mudanças no fluxo de tradução devem conservar os testes de texto fora do recorte, notas, imagens e fórmulas.

Contribuições ficam sob a licença AGPL-3.0 do projeto. Preserve avisos de terceiros e registre novas dependências no NOTICE.
