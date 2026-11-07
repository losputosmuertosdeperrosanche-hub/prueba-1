// Renderiza el vídeo de TikTok de NexusLead fotograma a fotograma (1080x1920, 30 fps).
// Uso: PW=<playwright> node render.js <carpeta app> <node_modules libs> <node_modules fuentes> <stage.html> <carpeta salida>
const { chromium } = require(process.env.PW);
const fs = require('fs'), path = require('path');
const [,, APP, NM, FONTS, STAGE, OUT] = process.argv;
const FPS = 30, DURATION = 38.0, HOTEL = 'osm:N305609481';
const ONLY = process.env.ONLY ? process.env.ONLY.split(',').map(Number) : null;   // tiempos sueltos para pruebas

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
// capa que entra en a y sale en b
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
      const html = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>[hidden]{display:none!important}</style></head><body style="margin:0">' + fs.readFileSync(path.join(APP, 'index.html'), 'utf8') + '</body></html>';
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
  await app.waitForFunction(() => typeof DATA !== 'undefined' && DATA.length >= 45543 && typeof map !== 'undefined', null, {timeout: 180000});
  await page.waitForFunction(() => window.S && S.ready() && S.loadPoints(), null, {timeout: 60000});

  // Ajustes de la app para grabar: sin animaciones internas (cada fotograma lo controla este guion)
  const K = await app.evaluate((hotelId) => {
    map.options.zoomSnap = 0; map._fadeAnimated = false; cluster.options.animate = false;
    const st = document.createElement('style');
    st.textContent = '#loading{display:none!important} .contact .v{filter:blur(5px)} .leaflet-tooltip{display:none!important}';
    document.head.appendChild(st);
    const DEB = L.latLngBounds([47.2, 5.8], [55.1, 15.1]);
    const h = byId.get(hotelId);
    const zH = 17.3, mh = map.getSize().y;
    // el hotel queda en la parte alta del mapa, para que la ficha no lo tape
    const cH = map.unproject(map.project([h.y, h.x], zH).add([0, mh * .2]), zH);
    return {
      de: {c: [DEB.getCenter().lat, DEB.getCenter().lng], z: map.getBoundsZoom(DEB) - .05},
      muc: {c: [48.1395, 11.5760], z: 11.0},          // casco antiguo de München
      hotel: {c: [cH.lat, cH.lng], z: zH, ll: [h.y, h.x], name: h.n},
    };
  }, HOTEL);
  console.log('cámaras', JSON.stringify(K));

  const idle = () => app.evaluate(() => new Promise(res => {
    let n = 0;
    const chk = () => {
      let loading = false;
      // teselas realmente pendientes (isLoading() de Leaflet se queda en true si se supera el zoom máximo de la capa)
      map.eachLayer(l => { if (l._tiles && Object.values(l._tiles).some(t => t.current && !t.loaded)) loading = true; });
      if (n === 401) { const info = []; map.eachLayer(l => { if (l.isLoading && l.isLoading()) info.push([l.options.minZoom, l.options.maxZoom, Object.values(l._tiles || {}).filter(t => !t.loaded).map(t => t.coords && [t.coords.z, t.coords.x, t.coords.y, !!t.current]).slice(0, 3)]); }); console.warn('IDLE-TIMEOUT', map.getZoom(), pending, JSON.stringify(info)); }
      if ((!loading && pending <= 0) || n++ > 400) requestAnimationFrame(() => requestAnimationFrame(res));
      else setTimeout(chk, 15);
    };
    chk();
  }));
  const setView = (c, z) => app.evaluate(([c, z]) => { map.setView(c, z, {animate: false}); }, [c, z]);
  const appDo = (fn, arg) => app.evaluate(fn, arg);

  // Precarga: zonas y bloques de detalle de München, y el modo satélite
  for (const v of [K.hotel, {c: K.hotel.c, z: 16}, K.muc, K.de]) { await setView(v.c, v.z); await idle(); }
  await appDo(() => document.querySelector('.modes button[data-mode="sat"]').click()); await idle();
  await setView(K.hotel.c, K.hotel.z); await idle();
  await appDo(() => document.querySelector('.modes button[data-mode="map"]').click()); await idle();
  await setView(K.de.c, K.de.z); await idle();

  // ---------- guion ----------
  const camera = t => {
    const fly = (a, b, x, centerFirst) => {
      const xc = centerFirst ? eOut(x) : eInOut(x), xz = eInOut(x);
      return {c: [lerp(a.c[0], b.c[0], xc), lerp(a.c[1], b.c[1], xc)], z: lerp(a.z, b.z, xz)};
    };
    const deDrift = {c: K.de.c, z: K.de.z + .06};
    const mucEnd = {c: K.muc.c, z: K.muc.z + .18};
    const hotelOut = {c: K.hotel.c, z: 16.0};
    if (t < 6.8) return {c: K.de.c, z: K.de.z + .06 * seg(t, 5, 6.8)};
    if (t < 9.0) return fly(deDrift, K.muc, seg(t, 6.8, 9.0), true);
    if (t < 16.0) return {c: K.muc.c, z: K.muc.z + .18 * seg(t, 9.0, 16.0)};
    if (t < 18.3) return fly(mucEnd, K.hotel, seg(t, 16.0, 18.3), true);
    if (t < 24.4) return {c: K.hotel.c, z: K.hotel.z};
    if (t < 27.3) return fly(K.hotel, hotelOut, seg(t, 24.4, 27.3));
    if (t < 29.2) return hotelOut;
    if (t < 30.9) return fly(hotelOut, mucEnd, seg(t, 29.2, 30.9));
    return mucEnd;
  };
  const events = [
    [6.55, () => appDo(() => { $('city').value = 'München'; refresh(false); })],
    [12.20, () => appDo(() => { $('sector').value = 'osm-hosteleria'; fillCities(); $('city').value = 'München'; refresh(false); })],
    [13.70, () => appDo(() => { $('sector').value = 'osm-salud'; fillCities(); $('city').value = 'München'; refresh(false); })],
    [15.20, () => appDo(() => { $('sector').value = 'osm-hosteleria'; fillCities(); $('city').value = 'München'; refresh(false); })],
    [18.75, () => appDo((id) => { openDetail(byId.get(id)); $('sheet').style.transform = 'translateY(100%)'; }, HOTEL)],
    [23.36, () => appDo(() => { $('sheet').hidden = true; $('sheet').style.transform = ''; })],
    [24.25, () => appDo(() => document.querySelector('.modes button[data-mode="sat"]').click())],
    ...['p', 'pi', 'piz', 'pizz', 'pizza'].map((s, i) => [27.95 + i * .2, () => appDo((s) => { $('q').value = s; refresh(false); }, s)]),
  ];
  const ripples = [[6.30, {sel: '#city'}], [11.95, {sel: '#sector'}], [13.45, {sel: '#sector'}], [14.95, {sel: '#sector'}],
                   [18.45, {ll: K.hotel.ll}], [21.15, {sel: '.sheet .contact a.mini'}], [24.00, {sel: '.modes button[data-mode="sat"]'}],
                   [27.55, {sel: '#q'}]];
  let zoomOrigin = null, pizzaCount = null, lastCam = null, nextEvent = 0;

  const N = Math.round(DURATION * FPS);
  const frames = ONLY ? ONLY.map(t => Math.round(t * FPS)) : [...Array(N).keys()];
  const t0 = Date.now();
  for (const f of frames) {
    const t = f / FPS;
    let dirty = false;
    // eventos de la app (en orden; en modo prueba se ejecutan todos los anteriores)
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
    if (t >= 28.9 && pizzaCount == null) pizzaCount = await appDo(() => current.length);

    // ---------- escenario ----------
    const L = {};
    L.hook1 = (() => { const w = win(t, .12, 2.85); return {...w, s: lerp(.88, 1, eOut(seg(t, .12, .45)))}; })();
    L.num = win(t, 1.0, 2.85); L.numLabel = win(t, 1.3, 2.85); L.numSmall = win(t, 1.6, 2.85);
    L.brand = (() => { const w = win(t, 3.0, 5.1, .4); return {...w, s: lerp(.92, 1, eOut(seg(t, 3.0, 3.4))), blur: 6 * (1 - seg(t, 3.0, 3.35))}; })();
    L.tag = win(t, 3.35, 5.1);
    let caption = null, pill = null;
    const caps = [[5.35, 11.45, ['PASO 1', 'Elige la ciudad', '8 grandes ciudades de Alemania']],
                  [11.6, 16.05, ['PASO 2', 'Filtra por sector', '']],
                  [16.2, 23.45, ['PASO 3', 'Toca la empresa', 'Teléfono, email y web al instante']],
                  [23.6, 27.45, ['MAPA REAL', 'Calles y satélite', 'Edificios y calles reales de cada ciudad']],
                  [27.6, 31.45, ['BUSCADOR', 'Busca lo que quieras', t >= 29.0 && pizzaCount ? `«pizza» en Múnich: ${pizzaCount} resultados` : '']]];
    L.cap = {o: 0};
    for (const [a, b, c] of caps) if (t >= a && t <= b) { L.cap = win(t, a, b); caption = c; }
    L.pills = win(t, 11.75, 16.05);
    if (t >= 12.2) pill = t < 13.7 ? 'osm-hosteleria' : t < 15.2 ? 'osm-salud' : 'osm-hosteleria';
    L.stats = win(t, 32.0, 35.25, .2, .25, 0);
    L.ctaBrand = win(t, 35.35, 38.5); L.ctaQ = win(t, 35.5, 38.5); L.ctaSmall = win(t, 36.0, 38.5);
    L.ctaPill = (() => { const w = win(t, 35.75, 38.5); return {...w, s: lerp(.8, 1, eOut(seg(t, 35.75, 36.05)))}; })();

    // móvil: entra, zoom sobre el contacto y sale
    let ph = {o: 0, y: 60};
    if (t >= 5.0 && t <= 32.1) {
      const i = eOut(seg(t, 5.0, 5.7)), o = eInOut(seg(t, 31.5, 32.1));
      ph = {o: Math.min(i, 1 - o), y: (1 - i) * 70 + o * 50};
      const z = eInOut(seg(t, 19.5, 20.3)) - eInOut(seg(t, 22.2, 22.9));
      if (z > 0 && zoomOrigin) Object.assign(ph, {s: 1 + .33 * z, ox: zoomOrigin[0], oy: zoomOrigin[1]});
    }
    let ripple = null;
    for (const [a, r] of ripples) if (t >= a && t <= a + .55) ripple = {...r, p: seg(t, a, a + .55)};

    const bg = {
      zoom: 1 + .12 * eInOut(seg(t, 0, 5.2)) - .07 * eInOut(seg(t, 31.5, 33)),
      reveal: eOut(seg(t, .15, 2.6)),
      dim: t < 2.9 ? .3 : t < 5.4 ? lerp(.3, .72, seg(t, 2.9, 5.4)) : .72,
    };
    await page.evaluate(st => S.apply(st), {bg, layers: L, caption, pill, num: 20483 * eOut(seg(t, 1.0, 2.2)), phone: ph, ripple, stats: t >= 32.0 ? t - 32.0 : null});
    await page.screenshot({path: path.join(OUT, `f${String(f).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 93});
    if (f % 60 === 0 || process.env.TIMING) console.log(`fotograma ${f}/${N} (${((Date.now() - t0) / 1000).toFixed(1)} s)`);
  }
  console.log('hotel:', K.hotel.name, '| pizza:', pizzaCount, '| errores:', errs);
  await browser.close();
})();
