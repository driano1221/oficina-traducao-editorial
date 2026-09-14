from __future__ import annotations

import hashlib
import json
import os
import posixpath
import re
import shutil
import subprocess
import threading
import time
import tkinter as tk
import urllib.parse
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import pymupdf as fitz
from bs4 import BeautifulSoup

from tradutor import (
    APP_ROOT,
    DEFAULT_INSTRUCTIONS,
    MODEL_PRICING_USD_PER_MILLION,
    JobConfig,
    epub_chapter_starts,
    fingerprint,
    parse_pages,
    run_job,
)


NAVY = "#173a50"
BLUE = "#55798e"
LINE = "#c7d8e3"
GREEN = "#62b426"
BG = "#f4f7f9"
INK = "#20343f"
WHITE = "#ffffff"


def safe_slug(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9áàâãéêíóôõúç]+", "_", value, flags=re.I)
    value = value.strip("_")[:70]
    return value or "livro"


def epub_inventory(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        container = ET.fromstring(archive.read("META-INF/container.xml"))
        rootfile = container.find(".//{*}rootfile")
        if rootfile is None or not rootfile.get("full-path"):
            raise ValueError("EPUB sem package.opf.")
        opf_name = rootfile.attrib["full-path"]
        opf = ET.fromstring(archive.read(opf_name))
        manifest = {node.attrib["id"]: dict(node.attrib) for node in opf.findall(".//{*}manifest/{*}item")}
        spine = [node.get("idref") for node in opf.findall(".//{*}spine/{*}itemref")]
        title = " — ".join(
            "".join(node.itertext()).strip() for node in opf.findall(".//{*}metadata/{*}title")
            if "".join(node.itertext()).strip()
        ) or path.stem
        docs = [
            posixpath.normpath(posixpath.join(posixpath.dirname(opf_name), manifest[item]["href"]))
            for item in spine if item in manifest and manifest[item].get("media-type") in {"application/xhtml+xml", "text/html"}
        ]
        pages: list[int] = []
        total_chars = 0
        for name in docs:
            raw = archive.read(name)
            pages.extend(int(n) for n in re.findall(rb'id=["\']pg_(\d+)["\']', raw))
            total_chars += len(BeautifulSoup(raw, "html.parser").get_text(" ", strip=True))
        chapters = [{"title": label, "document": name} for name, label in epub_chapter_starts(archive, opf_name, manifest)]
        return {
            "type": "EPUB", "title": title, "chapters": chapters, "printed_pages": max(pages) if pages else 0,
            "documents": len(docs), "characters": total_chars,
        }


def inspect_book(path: Path) -> dict:
    if path.suffix.lower() == ".epub":
        return epub_inventory(path)
    with fitz.open(path) as document:
        sample_chars = sum(len(page.get_text()) for page in document)
        return {"type": "PDF", "title": path.stem, "pages": document.page_count, "characters": sample_chars}


def estimate_tokens(path: Path, info: dict, scope: str, value: str) -> dict:
    chars = info["characters"]
    if info["type"] == "PDF" and scope == "Intervalo de páginas":
        pages = parse_pages(value, info["pages"])
        with fitz.open(path) as document:
            chars = sum(len(document[p - 1].get_text()) for p in pages)
    elif info["type"] == "EPUB" and scope == "Primeiros capítulos" and info["chapters"]:
        ratio = min(int(value), len(info["chapters"])) / len(info["chapters"])
        chars = max(1, int(chars * ratio))
    elif info["type"] == "EPUB" and scope == "Páginas impressas" and info["printed_pages"]:
        pages = parse_pages(value, info["printed_pages"])
        chars = max(1, int(chars * len(pages) / info["printed_pages"]))
    cjk = bool(re.search(r"[\u3400-\u9fff]", info.get("title", "") + path.name))
    source_tokens = int(chars / (1.6 if cjk else 4.0))
    return {"source": source_tokens, "input": source_tokens * 3, "output": int(source_tokens * 1.15)}


def estimate_cost(model: str, tokens: dict, usd_brl: float) -> tuple[float, float]:
    if model not in MODEL_PRICING_USD_PER_MILLION:
        raise ValueError("Modelo sem tabela de preço de referência.")
    rates = MODEL_PRICING_USD_PER_MILLION[model]
    usd = (tokens["input"] * rates["input"] + tokens["output"] * rates["output"]) / 1_000_000
    return usd, usd * usd_brl


def choose_project(source: Path, base: Path, scope_key: str = "") -> Path:
    digest = hashlib.sha256((fingerprint(source) + scope_key).encode()).hexdigest()[:12]
    return base / f"{safe_slug(source.stem)}_{digest}"


def publish_project(project: Path, original_source: Path, config: JobConfig, qa: dict, scope_label: str) -> None:
    original_dir = project / "01_original"
    work_dir = project / "02_trabalho"
    delivery_dir = project / "03_entrega_atual"
    reports_dir = project / "04_relatorios"
    for folder in (original_dir, work_dir, delivery_dir, reports_dir):
        folder.mkdir(parents=True, exist_ok=True)
    source_copy = original_dir / f"livro_original{original_source.suffix.lower()}"
    if not source_copy.exists() or fingerprint(source_copy) != fingerprint(original_source):
        shutil.copy2(original_source, source_copy)
    for name in ("livro_ptbr.pdf", "livro_ptbr.epub", "livro_ptbr.html", "traducao.md"):
        source = work_dir / name
        if source.exists():
            shutil.copy2(source, delivery_dir / name)
    for name in ("ativos", "paginas_originais"):
        assets = work_dir / name
        if assets.exists():
            shutil.copytree(assets, delivery_dir / name, dirs_exist_ok=True)
    for name in ("relatorio_qa.json", "validacao_local.json", "auditoria_traducao.json", "manifesto.json", "custo.json", "RELATORIO_VALIDACAO.md"):
        source = work_dir / name
        if source.exists():
            shutil.copy2(source, reports_dir / name)
    project_data = {
        "nome_original": original_source.name,
        "caminho_original": str(original_source),
        "sha256_origem": fingerprint(original_source),
        "escopo": scope_label,
        "modelo": config.model,
        "status": qa.get("status"),
        "atualizado_em": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "custo": qa.get("custo"),
    }
    (project / "projeto.json").write_text(json.dumps(project_data, ensure_ascii=False, indent=2), encoding="utf-8")
    (project / "LEIA-ME.md").write_text(
        f"# {original_source.stem}\n\nStatus atual: **{qa.get('status', 'não informado')}**  \nEscopo: **{scope_label}**\n\n"
        "- `01_original`: cópia imutável do arquivo recebido.\n"
        "- `02_trabalho`: cache e arquivos intermediários; permite retomar sem pagar tudo de novo.\n"
        "- `03_entrega_atual`: PDF/EPUB/HTML/Markdown prontos para leitura.\n"
        "- `04_relatorios`: QA estrutural, auditoria semântica, manifesto e custo.\n\n"
        "Em EPUBs parciais, os capítulos fora do escopo permanecem no idioma original.\n",
        encoding="utf-8",
    )


class TranslatorApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Oficina de Tradução Editorial")
        self.geometry("1180x790")
        self.minsize(1040, 700)
        self.configure(bg=BG)
        self.info: dict | None = None
        self.analyzed_path: Path | None = None
        self.last_project: Path | None = None
        self.source = tk.StringVar()
        self.library = tk.StringVar(value=str(APP_ROOT / "resultados"))
        self.scope = tk.StringVar(value="Intervalo de páginas")
        self.amount = tk.StringVar(value="1-40")
        self.model = tk.StringVar(value="gpt-5.6-sol")
        self.concurrency = tk.IntVar(value=2)
        self.usd_brl = tk.StringVar(value="5.13")
        self.urls = tk.StringVar()
        self.status = tk.StringVar(value="Selecione um PDF ou EPUB para começar.")
        self.estimate = tk.StringVar(value="Estimativa disponível após analisar o livro.")
        self._style()
        self._build()

    def _style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=WHITE, borderwidth=1, relief="solid")
        style.configure("TLabel", background=BG, foreground=INK, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=WHITE, foreground=INK, font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background=WHITE, foreground=NAVY, font=("Georgia", 15, "bold"))
        style.configure("Meta.TLabel", background=WHITE, foreground=BLUE, font=("Consolas", 9))
        style.configure("Primary.TButton", background=GREEN, foreground=WHITE, font=("Segoe UI Semibold", 11), padding=(18, 11), borderwidth=0)
        style.map("Primary.TButton", background=[("active", "#559d21"), ("disabled", "#adc99a")])
        style.configure("Secondary.TButton", background=WHITE, foreground=NAVY, padding=(12, 8))
        style.configure("TEntry", fieldbackground=WHITE, bordercolor=LINE, padding=7)
        style.configure("TCombobox", fieldbackground=WHITE, bordercolor=LINE, padding=6)
        style.configure("Horizontal.TProgressbar", background=GREEN, troughcolor="#dfe8ed")

    def _card(self, parent: tk.Widget, title: str, row: int, column: int, columnspan: int = 1) -> ttk.Frame:
        card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        card.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=6, pady=6)
        ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w", pady=(0, 12))
        return card

    def _field(self, parent: tk.Widget, label: str, variable: tk.Variable, browse=None) -> ttk.Entry:
        ttk.Label(parent, text=label.upper(), style="Meta.TLabel").pack(anchor="w", pady=(5, 3))
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill="x")
        entry = ttk.Entry(row, textvariable=variable)
        entry.pack(side="left", fill="x", expand=True)
        if browse:
            ttk.Button(row, text="Escolher", command=browse, style="Secondary.TButton").pack(side="left", padx=(8, 0))
        return entry

    def _build(self) -> None:
        header = tk.Frame(self, bg=NAVY, height=108)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="OFICINA EDITORIAL", bg=NAVY, fg="#bcd2df", font=("Consolas", 10, "bold")).pack(anchor="w", padx=36, pady=(20, 1))
        tk.Label(header, text="Tradução revisável de livros", bg=NAVY, fg=WHITE, font=("Georgia", 25, "bold")).pack(anchor="w", padx=34)
        tk.Label(header, text="EPUB estruturado · PDF de estudo · verificações e estimativa de custo.", bg=NAVY, fg="#dce8ef", font=("Segoe UI", 10)).pack(anchor="w", padx=36, pady=(2, 0))

        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        content = ttk.Frame(canvas, padding=20)
        window = canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        content.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window, width=e.width))
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)

        source_card = self._card(content, "1. Livro e biblioteca", 0, 0)
        self._field(source_card, "Arquivo original", self.source, self.choose_source).bind("<FocusOut>", lambda _: self.analyze() if self.source.get() and Path(self.source.get()).resolve() != self.analyzed_path else None)
        self._field(source_card, "Pasta da biblioteca", self.library, self.choose_library)
        ttk.Label(source_card, textvariable=self.status, style="Card.TLabel", wraplength=610, justify="left").pack(anchor="w", pady=(12, 0))

        scope_card = self._card(content, "2. Escopo", 0, 1)
        ttk.Label(scope_card, text="TIPO DE RECORTE", style="Meta.TLabel").pack(anchor="w", pady=(4, 3))
        self.scope_box = ttk.Combobox(scope_card, textvariable=self.scope, state="readonly")
        self.scope_box["values"] = ("Intervalo de páginas", "Livro inteiro")
        self.scope_box.pack(fill="x")
        self.scope_box.bind("<<ComboboxSelected>>", lambda _: self.refresh_estimate())
        self._field(scope_card, "Páginas ou quantidade", self.amount).bind("<KeyRelease>", lambda _: self.refresh_estimate())
        ttk.Label(scope_card, text="Exemplos: 1-40 · 1-42,45 · 4 capítulos", style="Meta.TLabel").pack(anchor="w", pady=(7, 0))

        settings = self._card(content, "3. Qualidade e custo", 1, 0)
        row = ttk.Frame(settings, style="Card.TFrame")
        row.pack(fill="x")
        left = ttk.Frame(row, style="Card.TFrame")
        right = ttk.Frame(row, style="Card.TFrame")
        left.pack(side="left", fill="x", expand=True, padx=(0, 8))
        right.pack(side="left", fill="x", expand=True)
        ttk.Label(left, text="MODELO", style="Meta.TLabel").pack(anchor="w")
        model = ttk.Combobox(left, textvariable=self.model, values=tuple(MODEL_PRICING_USD_PER_MILLION))
        model.pack(fill="x", pady=(3, 0)); model.bind("<<ComboboxSelected>>", lambda _: self.refresh_estimate())
        ttk.Label(right, text="TAREFAS EM PARALELO", style="Meta.TLabel").pack(anchor="w")
        ttk.Spinbox(right, from_=1, to=4, textvariable=self.concurrency).pack(fill="x", pady=(3, 0))
        self._field(settings, "Câmbio USD/BRL (somente estimativa)", self.usd_brl).bind("<KeyRelease>", lambda _: self.refresh_estimate())
        self._field(settings, "Fontes HTML oficiais, separadas por vírgula (opcional)", self.urls)
        ttk.Label(settings, textvariable=self.estimate, style="Card.TLabel", wraplength=640, justify="left").pack(anchor="w", pady=(12, 0))

        qa_card = self._card(content, "Diagnóstico de fidelidade", 1, 1)
        self.diagnostic = tk.Text(qa_card, height=11, wrap="word", relief="flat", bg=WHITE, fg=INK, font=("Segoe UI", 10), state="disabled")
        self.diagnostic.pack(fill="both", expand=True)

        notes = self._card(content, "Instruções editoriais adicionais", 2, 0, 2)
        self.instructions = tk.Text(notes, height=4, wrap="word", relief="solid", borderwidth=1, highlightthickness=0, font=("Segoe UI", 10))
        self.instructions.insert("1.0", "Mantenha terminologia técnica consistente e use português brasileiro natural. Não traduza nomes de métodos quando a forma em inglês for a convenção da área.")
        self.instructions.pack(fill="x")

        run_card = self._card(content, "Execução", 3, 0, 2)
        self.progress = ttk.Progressbar(run_card, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 10))
        self.log = tk.Text(run_card, height=8, wrap="word", bg="#eef3f6", fg=INK, relief="flat", font=("Consolas", 9), state="disabled")
        self.log.pack(fill="both", expand=True)
        actions = ttk.Frame(run_card, style="Card.TFrame")
        actions.pack(fill="x", pady=(12, 0))
        self.run_button = ttk.Button(actions, text="Traduzir e gerar entrega", style="Primary.TButton", command=self.start)
        self.run_button.pack(side="left")
        ttk.Button(actions, text="Abrir entrega", style="Secondary.TButton", command=self.open_delivery).pack(side="left", padx=10)

    def choose_source(self) -> None:
        selected = filedialog.askopenfilename(filetypes=[("Livros", "*.pdf *.epub"), ("PDF", "*.pdf"), ("EPUB", "*.epub")])
        if selected:
            self.source.set(selected)
            self.analyze()

    def choose_library(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.library.get())
        if selected:
            self.library.set(selected)

    def analyze(self) -> None:
        try:
            path = Path(self.source.get())
            self.info = inspect_book(path)
            self.analyzed_path = path.resolve()
            if self.info["type"] == "PDF":
                self.scope_box["values"] = ("Intervalo de páginas", "Livro inteiro")
                self.scope.set("Intervalo de páginas")
                self.amount.set(f"1-{min(40, self.info['pages'])}")
                description = (
                    f"PDF · {self.info['pages']} páginas · {self.info['characters']:,} caracteres extraíveis\n\n"
                    "Estratégia: página original como imagem e texto traduzido em A4. Não reconstrói tabelas, não faz OCR nem traduz texto dentro de figuras. "
                    "A diagramação não replica a do PDF original."
                )
            else:
                if self.info["chapters"]:
                    choices = ["Primeiros capítulos", "Todos os capítulos"]
                    if self.info["printed_pages"]:
                        choices.insert(1, "Páginas impressas")
                    self.scope_box["values"] = tuple(choices)
                    self.scope.set("Primeiros capítulos")
                    self.amount.set(str(min(4, len(self.info["chapters"]))))
                elif self.info["printed_pages"]:
                    self.scope_box["values"] = ("Páginas impressas",)
                    self.scope.set("Páginas impressas")
                    self.amount.set(f"1-{min(40, self.info['printed_pages'])}")
                else:
                    raise ValueError("Este EPUB não oferece capítulos nem marcadores de páginas reconhecíveis.")
                chapter_text = "\n".join(f"  {i + 1}. {item['title']}" for i, item in enumerate(self.info["chapters"][:8]))
                description = (
                    f"EPUB · {len(self.info['chapters'])} capítulos detectados · {self.info['documents']} seções · "
                    f"página impressa máxima {self.info['printed_pages'] or 'não disponível'}\n\n"
                    "Estratégia: traduzir dentro do pacote XHTML original. CSS, imagens, links e navegação são preservados. "
                    "Em recortes parciais, o restante do EPUB continua no idioma original.\n" + chapter_text
                )
            self.status.set(f"Analisado: {self.info['title']}")
            self.diagnostic.configure(state="normal"); self.diagnostic.delete("1.0", "end"); self.diagnostic.insert("1.0", description); self.diagnostic.configure(state="disabled")
            self.refresh_estimate()
        except Exception as exc:
            self.info = None
            messagebox.showerror("Não foi possível analisar", str(exc))

    def refresh_estimate(self) -> None:
        if not self.info:
            return
        try:
            path = Path(self.source.get())
            scope = self.scope.get()
            value = self.amount.get().strip()
            if scope == "Livro inteiro":
                value = f"1-{self.info['pages']}"
            elif scope == "Todos os capítulos":
                value = str(len(self.info["chapters"]))
                self.amount.set(value)
            tokens = estimate_tokens(path, self.info, scope, value)
            usd, brl = estimate_cost(self.model.get(), tokens, float(self.usd_brl.get().replace(",", ".")))
            self.estimate.set(
                f"Estimativa prévia: ~{tokens['source']:,} tokens de conteúdo; equivalente API ≈ US$ {usd:.2f} / R$ {brl:.2f}. "
                "Com login ChatGPT, normalmente consome a franquia do Codex e não gera cobrança adicional de API. O relatório final usa os tokens realmente informados pelo Codex CLI."
            )
        except Exception:
            self.estimate.set("Informe um escopo válido para calcular a estimativa.")

    def append_log(self, value: str) -> None:
        def update() -> None:
            self.log.configure(state="normal"); self.log.insert("end", value.rstrip() + "\n"); self.log.see("end"); self.log.configure(state="disabled")
        self.after(0, update)

    def start(self) -> None:
        if not self.info or Path(self.source.get()).resolve() != self.analyzed_path:
            self.analyze()
        if not self.info:
            return
        try:
            source = Path(self.source.get()).resolve()
            scope = self.scope.get()
            if self.info["type"] == "PDF":
                spec = f"1-{self.info['pages']}" if scope == "Livro inteiro" else self.amount.get()
                pages = parse_pages(spec, self.info["pages"])
                chapters = 0
                scope_label = f"páginas {spec}"
            elif scope in {"Primeiros capítulos", "Todos os capítulos"}:
                chapters = len(self.info["chapters"]) if scope == "Todos os capítulos" else int(self.amount.get())
                if chapters < 1 or chapters > len(self.info["chapters"]):
                    raise ValueError(f"Escolha de 1 a {len(self.info['chapters'])} capítulos.")
                pages = []
                scope_label = f"primeiros {chapters} capítulos" if scope == "Primeiros capítulos" else f"todos os {chapters} capítulos detectados"
            else:
                pages = parse_pages(self.amount.get(), self.info["printed_pages"])
                chapters = 0
                if pages != list(range(1, pages[-1] + 1)):
                    raise ValueError("O recorte de páginas de EPUB precisa começar em 1 e ser contínuo.")
                scope_label = f"páginas impressas 1-{pages[-1]}"
            instructions = DEFAULT_INSTRUCTIONS + " " + self.instructions.get("1.0", "end").strip()
            scope_key = json.dumps([scope_label, self.model.get(), instructions, self.urls.get()], ensure_ascii=False)
            project = choose_project(source, Path(self.library.get()).resolve(), scope_key)
            work = project / "02_trabalho"
            config = JobConfig(
                pdf=source, output=work, pages=pages, chapters=chapters, model=self.model.get(),
                concurrency=max(1, min(4, self.concurrency.get())), instructions=instructions,
                source_urls=tuple(item.strip() for item in self.urls.get().split(",") if item.strip()),
                usd_brl=float(self.usd_brl.get().replace(",", ".")),
            )
        except Exception as exc:
            messagebox.showerror("Configuração inválida", str(exc))
            return
        self.run_button.configure(state="disabled")
        self.progress.start(12)
        threading.Thread(target=self._run, args=(source, project, config, scope_label), daemon=True).start()

    def _run(self, source: Path, project: Path, config: JobConfig, scope_label: str) -> None:
        try:
            self.append_log(f"Projeto: {project}")
            qa = run_job(config, self.append_log)
            publish_project(project, source, config, qa, scope_label)
            self.last_project = project
            cost = qa.get("custo", {})
            equivalent = cost.get("custo_equivalente_api_usd")
            cost_label = f"US$ {equivalent:.2f}" if equivalent is not None else "indisponível"
            final = f"Concluído · QA: {qa.get('status')} · equivalente API: {cost_label}"
            self.append_log(final)
            self.after(0, lambda: messagebox.showinfo("Tradução concluída", final + f"\n\nEntrega: {project / '03_entrega_atual'}"))
        except Exception as exc:
            self.append_log(f"ERRO: {exc}")
            self.after(0, lambda error=str(exc): messagebox.showerror("Falha na tradução", error))
        finally:
            self.after(0, self._finish)

    def _finish(self) -> None:
        self.progress.stop()
        self.run_button.configure(state="normal")

    def open_delivery(self) -> None:
        target = (self.last_project / "03_entrega_atual") if self.last_project else Path(self.library.get())
        target.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            os.startfile(target)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", str(target)])


def main() -> None:
    TranslatorApp().mainloop()


if __name__ == "__main__":
    main()
