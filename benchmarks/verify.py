"""Verifica que os dados privados ainda correspondem ao benchmark versionado."""
import hashlib
import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: python benchmarks/verify.py CAMINHO_DOS_DADOS")
        return 2
    root = Path(sys.argv[1])
    manifest = json.loads(Path(__file__).with_name("impact-evaluation-ch1-3.v1.json").read_text(encoding="utf-8"))
    for name, expected in manifest["files"].items():
        path = root / name
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "ausente"
        if actual != expected:
            print(f"FALHA {name}: {actual}")
            return 1
    sources = json.loads((root / "fontes.json").read_text(encoding="utf-8"))
    summary = json.loads((root / "resumo_avaliacao.json").read_text(encoding="utf-8"))
    if len(sources) != manifest["items"] or summary["resultado"] != {"empate": 55, "sol": 55, "luna": 30}:
        print("FALHA: contagem ou resultado agregado divergente")
        return 1
    print(f"Benchmark v{manifest['benchmark_version']} íntegro: {len(sources)} itens.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
