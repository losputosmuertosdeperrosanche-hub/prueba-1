// Renderiza el anuncio de la actualización (sector Logística) fotograma a fotograma (1080x1920, 30 fps).
// Uso: PW=<playwright> APP_INDEX=index-de.html node render_anuncio.js <carpeta app> <node_modules libs> <node_modules fuentes> <stage_anuncio.html> <carpeta salida>
const { chromium } = require(process.env.PW);
const fs = require('fs'), path = require('path');
const [,, APP, NM, FONTS, STAGE, OUT] = process.argv;
const FPS = 30, DURATION = 42.5;
const FIRMA = 'osm:W179131759';               // Grohmann Logistik GmbH, Berlin: tiene teléfono y web
const TOTAL = 45715;                          // empresas en la app con el sector Logística
const APP_INDEX = process.env.APP_INDEX || 'index-de.html';
const T = {
  stage: {hook1: 'Neu: Logistik!', numLabel: 'Logistikbetriebe in Deutschland', numSmall: 'Spedition · Kurier · Lager · Transport',
          tag: 'Die neue Branche in NexusLead', ctaQ: 'Willst du es testen?', ctaPill: 'Kommentiere »LOGISTIK«',
          ctaSmall: 'und wir zeigen dir, wie es funktioniert',
          stats: ['Logistikbetriebe, neu dabei', 'davon mit Telefon oder E-Mail', 'Arten von Logistikbetrieben', 'große deutsche Städte']},
  pills: {'osm-logistica': 'Logistik'},
  caps: {s1: ['SCHRITT 1', 'Wähle die Stadt', 'Hier: Berlin'], s2: ['SCHRITT 2', 'Wähle die Branche', 'Neu: Logistik'],
         s3: ['SCHRITT 3', 'Tippe auf einen Betrieb', 'Adresse und Kontakt sofort'],
         s4: ['NUR MIT KONTAKT', 'Filter „Mit Kontakt“', 'Nur Betriebe mit Telefon oder E-Mail'],
         s5: ['QUELLE', 'OpenStreetMap', 'Die Daten aktualisieren wir laufend']},
};
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

// ---------- utilidades de tiempo ----------
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eOut = x => 1 - Math.pow(1 - x, 3);
const eInOut = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
const lerp = (a, b, x) => a + (b - a) * x;
function win(t, a, b, fi = .3, fo = .22, dy = 10){
  if (t < a || t > b) return {o: 0};
  const i = eOut(seg(t, a, a + fi)), o = 1 - seg(t, b - fo, b);
  return {o: Math.min(i, o), y: (1 - i) * dy - (1 - o) * 6};
}

(async () => {
  fs.mkdirSync(OUT, {recursive: true});
  const browser = await chromium.launch({executablePath: '/opt/pw-browsers/chromium'});
  const ctx = await browser.newContext({viewport: {width: 360, height: 640}, deviceScaleFactor: 3, colorScheme: 'light'});
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  page.on('console', m => { if (m.text().startsWith('IDLE-TIMEOUT')) console.log(m.text()); });
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
  await app.waitForFunction(({n, id}) => typeof DATA !== 'undefined' && DATA.length >= n && typeof map !== 'undefined' && byId.has(id),
                            {n: TOTAL, id: FIRMA}, {timeout: 180000});
  await page.waitForFunction(() => window.S && S.ready() && S.loadPoints(), null, {timeout: 60000});
  await page.evaluate(TX => S.setTexts(TX), {...T.stage, pills: T.pills});

  // Ajustes de la app para grabar: sin animaciones internas (cada fotograma lo controla este guion)
  const K = await app.evaluate((firmaId) => {
    map.options.zoomSnap = 0; map._fadeAnimated = false; cluster.options.animate = false;
    const st = document.createElement('style');
    st.textContent = '#loading{display:none!important} .contact .v{filter:blur(5px)} .leaflet-tooltip{display:none!important}';
    document.head.appendChild(st);
    const DEB = L.latLngBounds([47.2, 5.8], [55.1, 15.1]);
    const f = byId.get(firmaId);
    const zF = 17.3, mh = map.getSize().y;
    // la empresa queda en la parte alta del mapa, para que la ficha no la tape
    const cF = map.unproject(map.project([f.y, f.x], zF).add([0, mh * .2]), zF);
    return {
      de: {c: [DEB.getCenter().lat, DEB.getCenter().lng], z: map.getBoundsZoom(DEB) - .05},
      ber: {c: [52.5105, 13.4143], z: 11.2},          // Berlín, donde están las 44 empresas de logística
      firma: {c: [cF.lat, cF.lng], z: zF, ll: [f.y, f.x], name: f.n},
    };
  }, FIRMA);
  console.log('cámaras', JSON.stringify(K));

  const idle = () => app.evaluate(() => new Promise(res => {
    let n = 0;
    const chk = () => {
      let loading = false;
      // teselas realmente pendientes (isLoading() de Leaflet se queda en true si se supera el zoom máximo de la capa)
      map.eachLayer(l => { if (l._tiles && Object.values(l._tiles).some(t => t.current && !t.loaded)) loading = true; });
      if ((!loading) || n++ > 400) requestAnimationFrame(() => requestAnimationFrame(res));
      else setTimeout(chk, 15);
    };
    chk();
  }));
  const setView = (c, z) => app.evaluate(([c, z]) => { map.setView(c, z, {animate: false}); }, [c, z]);
  const appDo = (fn, arg) => app.evaluate(fn, arg);

  // Precarga de las vistas que se van a usar
  for (const v of [K.firma, {c: K.firma.c, z: 16}, K.ber, K.de]) { await setView(v.c, v.z); await idle(); }
  await setView(K.de.c, K.de.z); await idle();

  // ---------- guion ----------
  const camera = t => {
    const fly = (a, b, x, centerFirst) => {
      const xc = centerFirst ? eOut(x) : eInOut(x), xz = eInOut(x);
      return {c: [lerp(a.c[0], b.c[0], xc), lerp(a.c[1], b.c[1], xc)], z: lerp(a.z, b.z, xz)};
    };
    const berEnd = {c: K.ber.c, z: K.ber.z + .18};
    if (t < 6.8) return {c: K.de.c, z: K.de.z + .06 * seg(t, 5, 6.8)};
    if (t < 9.0) return fly({c: K.de.c, z: K.de.z + .06}, K.ber, seg(t, 6.8, 9.0), true);
    if (t < 16.0) return {c: K.ber.c, z: K.ber.z + .18 * seg(t, 9.0, 16.0)};
    if (t < 18.3) return fly(berEnd, K.firma, seg(t, 16.0, 18.3), true);
    if (t < 24.4) return {c: K.firma.c, z: K.firma.z};
    if (t < 27.3) return fly(K.firma, berEnd, seg(t, 24.4, 27.3));
    return berEnd;
  };
  const events = [
    [6.55, () => appDo(() => { $('city').value = 'Berlin'; refresh(false); })],
    [12.20, () => appDo(() => { $('sector').value = 'osm-logistica'; fillCities(); $('city').value = 'Berlin'; refresh(false); })],
    [18.75, () => appDo((id) => { openDetail(byId.get(id)); $('sheet').style.transform = 'translateY(100%)'; }, FIRMA)],
    [23.36, () => appDo(() => { $('sheet').hidden = true; $('sheet').style.transform = ''; })],
    [24.25, () => appDo(() => { $('onlyContact').checked = true; refresh(false); })],
  ];
  const ripples = [[6.30, {sel: '#city'}], [11.95, {sel: '#sector'}], [18.45, {ll: K.firma.ll}],
                   [21.15, {sel: '.sheet .contact a.mini'}], [24.00, {sel: '.toggle'}]];
  let zoomOrigin = null, lastCam = null, nextEvent = 0;

  const N = Math.round(DURATION * FPS);
  const t0 = Date.now();
  for (let f = 0; f < N; f++) {
    const t = f / FPS;
    let dirty = false;
    while (nextEvent < events.length && events[nextEvent][0] <= t) { await events[nextEvent][1](); nextEvent++; dirty = true; }
    // ficha: entrada y salida deslizando
    if (t >= 18.75 && t <= 23.36) {
      const p = t < 23.0 ? eOut(seg(t, 18.75, 19.2)) : 1 - eInOut(seg(t, 23.0, 23.35));
      await appDo(p => { $('sheet').style.transform = `translateY(${(1 - p) * 100}%)`; }, p);
      dirty = true;
    }
    const cam = camera(t);
    if (!lastCam || Math.abs(cam.z - lastCam.z) > 1e-6 || Math.abs(cam.c[0] - lastCam.c[0]) > 1e-9 || Math.abs(cam.c[1] - lastCam.c[1]) > 1e-9) {
      await setView(cam.c, cam.z); lastCam = cam; dirty = true;
    }
    if (dirty) await idle();
    if (t >= 19.2 && !zoomOrigin) zoomOrigin = await page.evaluate(() => S.phoneLocal('.sheet .contact'));

    // ---------- escenario ----------
    const L = {};
    L.hook1 = (() => { const w = win(t, .12, 2.85); return {...w, s: lerp(.88, 1, eOut(seg(t, .12, .45)))}; })();
    L.num = win(t, 1.0, 2.85); L.numLabel = win(t, 1.3, 2.85); L.numSmall = win(t, 1.6, 2.85);
    L.brand = (() => { const w = win(t, 3.0, 5.1, .4); return {...w, s: lerp(.92, 1, eOut(seg(t, 3.0, 3.4))), blur: 6 * (1 - seg(t, 3.0, 3.35))}; })();
    L.tag = win(t, 3.35, 5.1);
    let caption = null, pill = null;
    const C = T.caps;
    const caps = [[5.35, 11.45, [...C.s1]], [11.6, 16.05, [...C.s2]], [16.2, 23.45, [...C.s3]],
                  [23.6, 29.2, [...C.s4]], [29.4, 34.6, [...C.s5]]];
    L.cap = {o: 0};
    for (const [a, b, c] of caps) if (t >= a && t <= b) { L.cap = win(t, a, b); caption = c; }
    L.pills = win(t, 11.75, 16.05);
    if (t >= 12.2 && t < 34.6) pill = 'osm-logistica';
    L.ctaBrand = win(t, 38.7, DURATION); L.ctaQ = win(t, 38.9, DURATION); L.ctaSmall = win(t, 39.3, DURATION);
    L.ctaPill = (() => { const w = win(t, 39.1, DURATION); return {...w, s: lerp(.8, 1, eOut(seg(t, 39.1, 39.4)))}; })();

    // móvil: entra, zoom sobre el contacto y sale
    let ph = {o: 0, y: 60};
    if (t >= 5.0 && t <= 34.9) {
      const i = eOut(seg(t, 5.0, 5.7)), o = eInOut(seg(t, 34.2, 34.9));
      ph = {o: Math.min(i, 1 - o), y: (1 - i) * 70 + o * 50};
      const z = eInOut(seg(t, 19.5, 20.3)) - eInOut(seg(t, 22.2, 22.9));
      if (z > 0 && zoomOrigin) Object.assign(ph, {s: 1 + .33 * z, ox: zoomOrigin[0], oy: zoomOrigin[1]});
    }
    let ripple = null;
    for (const [a, r] of ripples) if (t >= a && t <= a + .55) ripple = {...r, p: seg(t, a, a + .55)};

    const bg = {
      zoom: 1 + .12 * eInOut(seg(t, 0, 5.2)) - .07 * eInOut(seg(t, 34.6, 36)),
      reveal: eOut(seg(t, .15, 2.6)),
      dim: t < 2.9 ? .3 : t < 5.4 ? lerp(.3, .72, seg(t, 2.9, 5.4)) : .72,
    };
    const stats = (t >= 35.2 && t < 38.6) ? t - 35.2 : null;   // las cifras se ocultan antes del cierre
    await page.evaluate(st => S.apply(st), {bg, layers: L, caption, pill, num: 172 * eOut(seg(t, 1.0, 2.2)), phone: ph, ripple, stats});
    await page.screenshot({path: path.join(OUT, `f${String(f).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 93});
    if (f % 60 === 0) console.log(`fotograma ${f}/${N} (${((Date.now() - t0) / 1000).toFixed(1)} s)`);
  }
  console.log('anuncio: fotogramas', N, '| total empresas', TOTAL, '| errores:', errs);
  await browser.close();
})();
