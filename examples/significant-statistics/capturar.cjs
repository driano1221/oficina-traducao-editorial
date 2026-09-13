// Capturas reais do XHTML; não altera texto, CSS ou dimensões internas do livro.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const root = path.resolve(__dirname, '../..');
const preview = path.join(root, 'tmp/significant-statistics/preview');
const doc = 'EPUB/chapter-007-descriptive-statistics-and-frequency-distributions.xhtml';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
  try {
    const captures = {};
    for (const language of ['original', 'traduzido']) {
      const page = await browser.newPage({ viewport: { width: 520, height: 1100 }, deviceScaleFactor: 2 });
      await page.goto(pathToFileURL(path.join(preview, language, doc)).href);
      await page.evaluate(async () => {
        await document.fonts.ready;
        await Promise.all([...document.images].map(image => image.decode()));
      });
      for (const kind of ['tabela', 'figura']) {
        let bounds;
        if (kind === 'figura') {
          bounds = await page.locator('figure.wp-caption').boundingBox();
        } else {
          bounds = await page.evaluate(() => {
            const table = document.querySelector('#tablepress-4');
            const top = table.closest('.textbox--key-takeaways').getBoundingClientRect().top + scrollY;
            const bottom = document.querySelector('#tablepress-4-description').getBoundingClientRect().bottom + scrollY;
            return { x: 0, y: top, width: 520, height: Math.ceil(bottom - top + 3) };
          });
        }
        const name = `${kind}-${language}.png`;
        await page.screenshot({ path: path.join(preview, name), clip: bounds, fullPage: true });
        captures[`${kind}-${language}`] = { name, width: bounds.width, height: bounds.height };
      }
      await page.close();
    }
    for (const kind of ['tabela', 'figura']) {
      const title = kind === 'tabela' ? 'Outro idioma. Os mesmos dados.' : 'A imagem permanece. A legenda é traduzida.';
      const detail = kind === 'tabela' ? 'Tabela de frequências com fórmulas preservadas como imagens.' : 'Fotografia original, identificação e link para a descrição preservados.';
      const panels = ['original', 'traduzido'].map((language, index) => {
        const asset = captures[`${kind}-${language}`];
        return `<section><div class="label ${index ? 'pt' : ''}">${index ? '02 / PORTUGUÊS BRASILEIRO' : '01 / ORIGINAL EM INGLÊS'}</div><div class="paper"><img src="${asset.name}" style="width:${asset.width * 1.35}px" alt="Recorte ${language}"/></div></section>`;
      }).join('');
      const html = `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Significant Statistics • ${kind}</title><style>
*{box-sizing:border-box}body{margin:0;padding:32px 28px;background:#e8eeea;color:#183e43;font:16px Arial,sans-serif}.brand{font-size:11px;font-weight:bold;letter-spacing:2px;margin-bottom:12px}header{display:flex;align-items:end;justify-content:space-between;gap:20px;margin-bottom:24px}h1{font:normal 36px Georgia,serif;letter-spacing:-.6px;margin:0 0 8px}header p{margin:0;color:#526c68;font-size:15px}.pill{white-space:nowrap;border:1px solid #b5c9c1;border-radius:30px;padding:10px 14px;font-size:11px;font-weight:600;letter-spacing:1px}main{display:grid;grid-template-columns:1fr 1fr;gap:20px}section{background:white;box-shadow:0 3px 15px #163e4310;border:1px solid #cbd6cc;border-radius:8px;overflow:hidden}.label{padding:15px 22px;background:#f3f5ee;color:#4c6761;font-size:11px;font-weight:bold;letter-spacing:1.5px;border-bottom:1px solid #dae1d5}.pt{background:#174c4e;color:#e6f2e9}.paper{padding:${kind === 'figura' ? '28px' : '12px 0'};display:flex;justify-content:center;align-items:start}.paper img{display:block;max-width:100%;height:auto}footer{display:flex;justify-content:space-between;gap:24px;color:#536d65;font-size:12px;line-height:1.6;margin-top:20px}footer span{max-width:70%}
</style></head><body><header><div><div class="brand">OFICINA DE TRADUÇÃO EDITORIAL / LIVRO ABERTO EM INGLÊS</div><h1>${title}</h1><p>${detail}</p></div><div class="pill">EPUB → EPUB · SEÇÃO 2.1</div></header><main>${panels}</main><footer><span>Significant Statistics · John Morgan Russell (2025) · Virginia Tech<br>doi.org/10.21061/significantstatistics · CC BY-SA 4.0 · Adaptação não oficial: driano1221${kind === 'figura' ? '<br>Foto: William Greeson / U.S. Marine Corps (2009), domínio público; crédito da obra.' : '<br>O original identifica esta tabela como Figure 2.3; a tradução mantém Figura 2.3.'}</span><span>Recortes de leitura dos EPUBs<br>CSS original · Sem retoques na tradução</span></footer></body></html>`;
      const target = path.join(preview, `comparativo-${kind}.html`);
      await fs.writeFile(target, html);
      const page = await browser.newPage({ viewport: { width: 1500, height: 1000 }, deviceScaleFactor: 1 });
      await page.goto(pathToFileURL(target).href);
      await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode())); });
      await page.setViewportSize({ width: 1500, height: Math.ceil((await page.locator('body').boundingBox()).height) });
      await page.screenshot({ path: path.join(root, `docs/images/statistics-${kind}.png`), fullPage: true });
      console.log(kind, await page.locator('body').boundingBox());
      await page.close();
    }
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
