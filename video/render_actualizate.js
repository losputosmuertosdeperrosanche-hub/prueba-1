// Renderiza el anuncio de actualizate IA fotograma a fotograma (1080x1920, 30 fps).
// Uso: PW=<playwright> node render_actualizate.js <de|ro> <carpeta salida> <node_modules fuentes> <stage_actualizate.html> <actualizate_tiempos.json>
// Opcional: FRAMES=0-10,300 para renderizar solo algunos fotogramas (pruebas).
const { chromium } = require(process.env.PW);
const fs = require('fs'), path = require('path');
const [,, LANG, OUT, FONTS, STAGE, TIEMPOS] = process.argv;
const FPS = 30;
const tiempos = JSON.parse(fs.readFileSync(TIEMPOS, 'utf8'));
const FV = FONTS + '/@fontsource-variable';
const fontFiles = {
  'archivo.woff2': FV + '/archivo/files/archivo-latin-standard-normal.woff2',
  'archivo-ext.woff2': FV + '/archivo/files/archivo-latin-ext-wdth-normal.woff2',
  'sourcesans3.woff2': FV + '/source-sans-3/files/source-sans-3-latin-wght-normal.woff2',
  'sourcesans3-ext.woff2': FV + '/source-sans-3/files/source-sans-3-latin-ext-wght-normal.woff2',
  'jetbrainsmono.woff2': FV + '/jetbrains-mono/files/jetbrains-mono-latin-wght-normal.woff2',
  'jetbrainsmono-ext.woff2': FV + '/jetbrains-mono/files/jetbrains-mono-latin-ext-wght-normal.woff2',
};

(async () => {
  fs.mkdirSync(OUT, {recursive: true});
  const browser = await chromium.launch({executablePath: '/opt/pw-browsers/chromium'});
  const ctx = await browser.newContext({viewport: {width: 360, height: 640}, deviceScaleFactor: 3, colorScheme: 'light'});
  await ctx.addInitScript(d => { window.LANG = d.lang; window.TIEMPOS = d.tiempos; }, {lang: LANG, tiempos});
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  await ctx.route(/^http:\/\/local\.test\//, r => {
    const rel = decodeURIComponent(new URL(r.request().url()).pathname.slice(1));
    if (rel === '' || rel === 'stage.html') return r.fulfill({body: fs.readFileSync(STAGE), contentType: 'text/html'});
    if (rel.startsWith('fonts/') && fontFiles[rel.slice(6)]) return r.fulfill({body: fs.readFileSync(fontFiles[rel.slice(6)]), contentType: 'font/woff2'});
    r.fulfill({status: 404, body: 'no'});
  });
  await page.goto('http://local.test/stage.html');
  await page.evaluate(() => document.fonts.ready);
  const N = Math.round(tiempos.duracion * FPS);
  const rango = process.env.FRAMES ? process.env.FRAMES.split(',').map(s => s.split('-').map(Number)) : null;
  console.log(`idioma ${LANG}: ${N} fotogramas`);
  const t0 = Date.now();
  for (let f = 0; f < N; f++) {
    if (rango && !rango.some(([a, b]) => f >= a && f <= (b ?? a))) continue;
    await page.evaluate(t => window.S.frame(t), f / FPS);
    await page.screenshot({path: path.join(OUT, `f${String(f).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 93});
    if (f % 150 === 0) console.log(`fotograma ${f}/${N} (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
  }
  console.log('listo; errores de página:', errs);
  await browser.close();
})();
