// Renderiza el vídeo de los sectores (todas las branches de NexusLead) fotograma a fotograma (1080x1920, 30 fps).
// Uso: PW=<playwright> APP_INDEX=index-de.html node render_sektoren.js <carpeta app> <node_modules libs> <node_modules fuentes> <stage_sektoren.html> <carpeta salida>
const { chromium } = require(process.env.PW);
const fs = require('fs'), path = require('path');
const [,, APP, NM, FONTS, STAGE, OUT] = process.argv;
const FPS = 30, DURATION = 52.0;
const TOTAL = 101796;                 // empresas únicas que muestra la app con todos los sectores cargados
const APP_INDEX = process.env.APP_INDEX || 'index-de.html';
const G0 = 7.6, GLEN = 5.0;           // primer grupo a los 7,6 s; cada grupo dura 5 s
// Cifras de cada branch: las mismas que muestra la app (recuento por sector)
const GRUPOS = [
  {kick: 'Gruppe 1 von 6', title: 'Essen und Einkauf', rows: [['Gastronomie', 35935], ['Supermärkte', 5868], ['Bäckereien', 3708], ['Kioske', 2519], ['Eisdielen', 845], ['Getränkemärkte', 548], ['Metzgereien', 513]]},
  {kick: 'Gruppe 2 von 6', title: 'Gesundheit und Schönheit', rows: [['Gesundheit', 7744], ['Friseure und Kosmetik', 3044], ['Apotheken und Drogerien', 2849], ['Optiker', 1085], ['Massage und Wellness', 790]]},
  {kick: 'Gruppe 3 von 6', title: 'Mode und Handel', rows: [['Bekleidung', 5100], ['Möbel und Einrichtung', 1427], ['Blumenläden', 1390], ['Juweliere', 1384], ['Schuhe', 800], ['Handyshops', 794], ['Schneidereien', 739]]},
  {kick: 'Gruppe 4 von 6', title: 'Firmen und Dienstleistungen', rows: [['Unternehmen und Büros', 5055], ['Rechtsanwälte', 902], ['Versicherungen', 990], ['Banken und Sparkassen', 1319], ['Reisebüros', 805], ['Immobilien', 822], ['IT und Software', 725], ['Logistik', 172]]},
  {kick: 'Gruppe 5 von 6', title: 'Autos und Räder', rows: [['Autowerkstätten', 1498], ['Autohäuser', 1147], ['Fahrradgeschäfte', 1045], ['Tankstellen', 1043]]},
  {kick: 'Gruppe 6 von 6', title: 'Freizeit und Familie', rows: [['Sport und Fitness', 1929], ['Kitas', 6261], ['Sicherheitsdienste', 863], ['Veranstaltungen', 180]]},
];
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eOut = x => 1 - Math.pow(1 - x, 3);
const eInOut = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
// Opacidad de una capa entre a y b (con fundido de entrada fi y de salida fo)
function win(t, a, b, fi = .3, fo = .3){
  if (t < a || t > b) return 0;
  const i = eOut(seg(t, a, a + fi)), o = fo > 0 ? 1 - seg(t, b - fo, b) : 1;
  return Math.min(i, o);
}
// Estado completo de cada fotograma
function estado(t){
  const st = {
    bg: {zoom: 1 + .05 * eInOut(seg(t, 0, DURATION)), reveal: eOut(seg(t, .15, 2.8)), dim: t < 3 ? .35 : .6},
    hook: {o: win(t, .3, 3.6)}, hookNum: 100000 * eOut(seg(t, .4, 2.8)),
    branch: {o: win(t, 3.8, 7.4)}, branchNum: 35 * eOut(seg(t, 3.9, 5.2)),
    group: {o: 0, y: 0}, rows: [], grupo: -1,
    contact: {o: win(t, 37.6, 41.6)}, cNum: 39736 * eOut(seg(t, 37.9, 40.2)),
    steps: [0, 1, 2].map(i => win(t, 41.6 + 1.3 * i, 45.6)),
    src: {o: win(t, 45.6, 48.0)},
    ctaBrand: {o: win(t, 48.0, DURATION, .3, 0)}, ctaQ: {o: win(t, 48.3, DURATION, .3, 0)},
    ctaPill: {o: win(t, 48.8, DURATION, .3, 0)}, ctaSmall: {o: win(t, 49.2, DURATION, .3, 0)},
  };
  for (let k = 0; k < GRUPOS.length; k++) {
    const tg = t - (G0 + GLEN * k);
    if (tg < 0 || tg >= GLEN) continue;
    st.grupo = k;
    const fuera = 1 - clamp((tg - (GLEN - .5)) / .5);
    st.group = {o: clamp(tg / .35) * fuera, y: (1 - eOut(clamp(tg / .45))) * 10};
    st.rows = GRUPOS[k].rows.map(([, v], i) => {
      const rs = .5 + i * .18, u = clamp((tg - rs) / .35);
      return {o: u * fuera, y: (1 - eOut(clamp((tg - rs) / .4))) * 8, v: v * eOut(clamp((tg - rs) / .9))};
    });
    break;
  }
  return st;
}
const libs = {
  'https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js': NM + '/leaflet/dist/leaflet.js',
  'https://cdn.jsdelivr.net/npm/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js': NM + '/leaflet.markercluster/dist/leaflet.markercluster.js',
  'https://cdn.jsdelivr.net/npm/leaflet.vectorgrid@1.3.0/dist/Leaflet.VectorGrid.bundled.min.js': NM + '/leaflet.vectorgrid/dist/Leaflet.VectorGrid.bundled.min.js',
};
const FV = FONTS + '/@fontsource-variable';
const fontFiles = {
  'archivo.woff2': FV + '/archivo/files/archivo-latin-standard-normal.woff2',
  'sourcesans3.woff2': FV + '/source-sans-3/files/source-sans-3-latin-wght-normal.woff2',
  'jetbrainsmono.woff2': FV + '/jetbrains-mono/files/jetbrains-mono-latin-wght-normal.woff2',
};
const googleCss = `
@font-face{font-family:"Archivo";src:url(http://local.test/fonts/archivo.woff2) format("woff2-variations");font-weight:100 900;font-stretch:62% 125%}
@font-face{font-family:"Source Sans 3";src:url(http://local.test/fonts/sourcesans3.woff2) format("woff2-variations");font-weight:200 900}
@font-face{font-family:"JetBrains Mono";src:url(http://local.test/fonts/jetbrainsmono.woff2) format("woff2-variations");font-weight:100 800}`;

(async () => {
  fs.mkdirSync(OUT, {recursive: true});
  const browser = await chromium.launch({executablePath: '/opt/pw-browsers/chromium'});
  const ctx = await browser.newContext({viewport: {width: 360, height: 640}, deviceScaleFactor: 3, colorScheme: 'light'});
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  for (const [u, f] of Object.entries(libs)) await ctx.route(u, r => r.fulfill({body: fs.readFileSync(f), contentType: 'application/javascript'}));
  await ctx.route(/fonts\.googleapis\.com/, r => r.fulfill({body: googleCss, contentType: 'text/css'}));
  await ctx.route(/fonts\.gstatic\.com/, r => r.abort());
  await ctx.route(/^http:\/\/local\.test\//, r => {
    const rel = decodeURIComponent(new URL(r.request().url()).pathname.slice(1));
    if (rel === '') {
      const html = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>[hidden]{display:none!important}</style></head><body style="margin:0">' + fs.readFileSync(path.join(APP, APP_INDEX), 'utf8') + '</body></html>';
      return r.fulfill({body: html, contentType: 'text/html'});
    }
    if (rel === 'stage.html') return r.fulfill({body: fs.readFileSync(STAGE), contentType: 'text/html'});
    if (rel.startsWith('fonts/')) return r.fulfill({body: fs.readFileSync(fontFiles[rel.slice(6)]), contentType: 'font/woff2'});
    const f = path.join(APP, rel);
    if (!fs.existsSync(f)) return r.fulfill({status: 404, body: 'no'});
    r.fulfill({body: fs.readFileSync(f), contentType: rel.endsWith('.jpg') ? 'image/jpeg' : 'application/json'});
  });
  await page.goto('http://local.test/stage.html');
  const app = page.frames().find(f => f.url() === 'http://local.test/');
  await app.waitForFunction(n => typeof DATA !== 'undefined' && DATA.length >= n, TOTAL, {timeout: 240000});
  await page.waitForFunction(() => window.S && S.ready() && S.loadPoints(), null, {timeout: 120000});
  const N = Math.round(DURATION * FPS);
  console.log('datos listos; fotogramas', N);
  const rango = process.env.FRAMES ? process.env.FRAMES.split(',').map(s => s.split('-').map(Number)) : null;
  const t0 = Date.now();
  let grupoActual = -1;
  for (let f = 0; f < N; f++) {
    if (rango && !rango.some(([a, b]) => f >= a && f <= b)) continue;
    const t = f / FPS;
    const st = estado(t);
    if (st.grupo >= 0 && st.grupo !== grupoActual) { grupoActual = st.grupo; await page.evaluate(g => S.setGroup(g), GRUPOS[st.grupo]); }
    await page.evaluate(s => S.apply(s), st);
    await page.screenshot({path: path.join(OUT, `f${String(f).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 93});
    if (f % 60 === 0) console.log(`fotograma ${f}/${N} (${((Date.now() - t0) / 1000).toFixed(1)} s)`);
  }
  console.log('vídeo de sectores: fotogramas', N, '| errores:', errs);
  await browser.close();
})();
