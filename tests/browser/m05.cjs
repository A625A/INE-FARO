/**
 * Recorrido Chromium de la demo. Arrancar Streamlit antes de ejecutar.
 * BASE_URL y FARO_EVIDENCE son opcionales. Playwright se instala aparte.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { chromium } = require('playwright');

const base = new URL(process.env.BASE_URL || 'http://127.0.0.1:8516');
const output = process.env.FARO_EVIDENCE || 'docs/evidencia/M-05/final';
const soloDestacado = process.argv.includes('--destacado');
const results = [];
const blocked = new Set();
const errors = new Set();

async function configure(context) {
  await context.route('**/*', async route => {
    const url = new URL(route.request().url());
    if (['http:', 'https:'].includes(url.protocol) && url.origin !== base.origin) {
      blocked.add(url.origin);
      await route.abort('internetdisconnected');
    } else {
      await route.continue();
    }
  });
  await context.routeWebSocket('**/*', webSocket => {
    const url = new URL(webSocket.url());
    if (url.host === base.host) webSocket.connectToServer();
    else {
      blocked.add(url.origin);
      webSocket.close();
    }
  });
}

function watch(page) {
  page.on('pageerror', error => errors.add(error.message));
  page.on('console', message => {
    if (['error', 'warning'].includes(message.type())) errors.add(message.text());
  });
  page.on('response', response => {
    if (response.url().startsWith(base.origin) && response.status() >= 400) {
      errors.add(`${response.status()} ${response.url()}`);
    }
  });
}

async function heading(page, name, level = 1) {
  await page.getByRole('heading', { name, level, exact: true }).waitFor();
}

async function ready(page) {
  await page.locator('[data-testid="stApp"][data-test-script-state="notRunning"]').waitFor();
}

async function section(page, name) {
  await page.getByTestId('stRadio').getByText(name, { exact: true }).click();
  await heading(page, name);
  await ready(page);
}

function select(page, label) {
  return page.getByTestId('stSelectbox').filter({ has: page.getByText(label, { exact: true }) }).first();
}

async function choose(page, label, option) {
  await ready(page);
  const widget = select(page, label);
  const input = widget.getByRole('combobox');
  await input.scrollIntoViewIfNeeded();
  await input.click();
  await input.press('ControlOrMeta+A');
  await input.pressSequentially(option, { delay: 20 });
  await page.getByRole('option', { name: option, exact: true }).waitFor({ state: 'attached' });
  await input.press('ArrowDown');
  await input.press('Enter');
  await ready(page);
}

async function charts(page, count) {
  await page.waitForFunction(n =>
    document.querySelectorAll('[data-testid="stVegaLiteChart"] canvas, [data-testid="stVegaLiteChart"] svg.marks').length >= n,
  count);
  await page.evaluate(() => document.fonts.ready);
}

async function evidence(page, name) {
  await ready(page);
  await page.evaluate(() => {
    if (document.activeElement instanceof HTMLElement) document.activeElement.blur();
    document.querySelector('[data-testid="stMain"]')?.scrollTo(0, 0);
  });
  await page.screenshot({ path: path.join(output, `${name}.png`), animations: 'disabled' });
}

async function download(page, button) {
  const pending = page.waitForEvent('download');
  await page.getByRole('button', { name: button, exact: true }).click();
  const file = await pending;
  assert.equal(await file.failure(), null);
  return fs.readFile(await file.path(), 'utf8');
}

async function desktop(page) {
  await page.goto(base.href);
  await heading(page, 'Empleo e ingresos');
  await charts(page, 4);
  for (const value of ['7,944,838', '65.6 %', '5,214,094', 'Q 2,842', '94.28 % de cobertura ponderada']) {
    await page.getByText(value, { exact: !value.startsWith('94.28') }).first().waitFor();
  }
  assert.equal(await page.getByRole('img', { name: 'Instituto Nacional de Estadística' }).evaluate(img => img.naturalWidth > 0), true);
  assert.equal(await page.evaluate(() => Array.from(document.fonts).some(f => f.family.includes('Ubuntu Sans') && f.status === 'loaded')), true);
  await evidence(page, '01-empleo');
  results.push('ENEIC: inicio, cuatro gráficas, controles nacionales, tipo y logo locales.');

  await section(page, 'Territorio');
  await charts(page, 3);
  await choose(page, 'Indicador del mapa', 'Pobreza extrema');
  await page.getByText('N/D · precisión insuficiente', { exact: true }).first().waitFor();
  await page.locator('[data-testid="stVegaLiteChart"] path[aria-label*="Pobreza extrema"]').first().waitFor();
  await choose(page, 'Departamento', 'Alta Verapaz');
  await heading(page, 'Alta Verapaz', 3);
  await choose(page, 'Comparar con', 'Guatemala');
  await heading(page, 'Perfil productivo comparado', 3);
  await charts(page, 3);
  await evidence(page, '02-territorio');
  const mapa = page.getByTestId('stVegaLiteChart').first();
  const marcas = mapa.locator('path[aria-label*="Santa Rosa"]');
  await marcas.waitFor();
  await marcas.hover();
  await page.locator('#vg-tooltip-element').getByText('Santa Rosa', { exact: true }).waitFor();
  await marcas.click();
  await heading(page, 'Santa Rosa', 3);
  await page.getByText('Valores y calidad de los 22 departamentos', { exact: true }).click();
  const csv = await download(page, 'Descargar indicador del mapa');
  const lineas = csv.trimEnd().split('\n');
  assert.equal(lineas.length, 23);
  const header = lineas[0].split(',');
  const noPublicables = lineas.filter(line => line.includes('no_publicable'));
  assert.equal(noPublicables.length, 5);
  for (const linea of noPublicables) {
    const fields = linea.split(',');
    assert.equal(fields[header.indexOf('valor')], '');
    assert.equal(fields[header.indexOf('ic95_inf')], '');
    assert.equal(fields[header.indexOf('ic95_sup')], '');
  }
  results.push('Territorio: selector, indicador, tooltip, clics en mapa, comparación y CSV con cinco valores e intervalos suprimidos.');

  await section(page, 'Producción');
  await charts(page, 4);
  for (const value of ['Q 172,538.68', 'Q 762,881.36', '22.62 %', '38.55 %']) {
    await page.getByText(value, { exact: true }).waitFor();
  }
  await page.getByText(/En 2020 no se desagregó/).waitFor();
  await evidence(page, '03-produccion');
  await choose(page, 'Tipo de precio', 'Volúmenes encadenados · referencia 2013');
  await heading(page, 'Evolución en volumen encadenado', 3);
  const serie = await download(page, 'Descargar serie nacional visible');
  assert.equal(serie.trimEnd().split('\n').length, 12);
  assert.doesNotMatch(serie, /^2020,/m);
  assert.equal(await page.getByText('22.62 %', { exact: true }).count(), 0);
  results.push('Producción: controles 2023, cambio a cadena y CSV nacional sin 2020.');

  await section(page, 'Radar de inteligencia');
  await choose(page, 'Regla', 'R1');
  await heading(page, 'R1 · Chimaltenango y Alta Verapaz', 3);
  await page.getByText('Evidencia adicional requerida', { exact: true }).waitFor();
  await choose(page, 'Regla', 'R4');
  await choose(page, 'Departamento del radar', 'Alta Verapaz');
  await heading(page, 'R4 · Alta Verapaz · Agricultura', 3);
  await evidence(page, '04-radar');
  await choose(page, 'Regla', 'R2a');
  await page.getByText(/ningún departamento supera simultáneamente/).waitFor();
  assert.equal(JSON.parse(await download(page, 'Descargar selección (JSON)')).hallazgos.length, 0);
  await choose(page, 'Regla', 'R2b');
  await choose(page, 'Departamento del radar', 'Santa Rosa');
  await heading(page, 'R2b · Santa Rosa', 3);
  const hallazgos = JSON.parse(await download(page, 'Descargar selección (JSON)'));
  assert.deepEqual(hallazgos.hallazgos.map(f => f.id), ['R2b:2023:06']);
  await page.getByRole('button', { name: 'Abrir perfil de Santa Rosa' }).click();
  await heading(page, 'Territorio');
  await heading(page, 'Santa Rosa', 3);
  await page.getByRole('button', { name: /Consultar hallazgos relacionados/ }).click();
  await heading(page, 'Radar de inteligencia');
  await ready(page);
  assert.equal(await select(page, 'Departamento del radar').getByRole('combobox').inputValue(), 'Santa Rosa');
  assert.equal(await select(page, 'Regla').getByRole('combobox').inputValue(), 'Todas');
  results.push('Radar: R1, Santa Rosa R2b y enlace recíproco, Alta Verapaz R4, R2a vacío y descargas filtradas.');

  await section(page, 'Metodología y calidad');
  await heading(page, 'Calidad estadística', 2);
  await charts(page, 1);
  await evidence(page, '05-metodologia');
  await choose(page, 'Clasificación', 'No publicable');
  await page.waitForFunction(() => Array.from(document.querySelectorAll('[data-testid="stMetricValue"]'))
    .map(el => el.textContent.trim()).join(',') === '5,0,5');
  await ready(page);
  const quality = page.getByRole('heading', { name: 'Calidad estadística', level: 2 });
  await quality.evaluate(el => el.scrollIntoView({ block: 'start', behavior: 'instant' }));
  await page.screenshot({ path: path.join(output, '07-calidad.png'), animations: 'disabled' });
  results.push('Metodología: filtros de calidad y cinco diagnósticos restringidos.');
}

async function mobile(page) {
  await page.goto(base.href);
  await heading(page, 'Empleo e ingresos');
  await charts(page, 4);
  assert.equal(await page.evaluate(() => innerWidth), 390);
  await evidence(page, '06-movil');
  for (const name of ['Territorio', 'Producción', 'Radar de inteligencia', 'Metodología y calidad']) {
    await section(page, name);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth ||
      document.querySelector('[data-testid="stMain"]').scrollWidth > innerWidth);
    assert.equal(overflow, false, name);
  }
  results.push('Móvil 390×844: cinco secciones accesibles y sin desbordamiento horizontal.');
}

async function destacado(page, movil = false) {
  await page.goto(base.href);
  await heading(page, 'Empleo e ingresos');
  await page.getByRole('button', { name: 'Ver contraste Chimaltenango–Alta Verapaz' }).click();
  await heading(page, 'R1 · Chimaltenango y Alta Verapaz', 3);
  await heading(page, '¿Qué investigar ahora?', 4);
  await ready(page);
  const contraste = page.locator('.st-key-contraste-destacado');
  for (const texto of ['42.55 pp', '0.98 pp', '1.50 ×', 'Pregunta de investigación', 'Evidencia adicional requerida']) {
    await contraste.getByText(texto, { exact: true }).waitFor();
  }
  await contraste.getByText(/7 de 7 escenarios/).waitFor();
  await contraste.getByText(/^Limitación/).waitFor();
  const tabla = contraste.getByTestId('stTable');
  for (const texto of ['Chimaltenango', 'Alta Verapaz', '47.75 %', '90.30 %']) {
    await tabla.getByText(texto, { exact: true }).waitFor();
  }
  const evidencias = contraste.locator('details[open]').filter({ hasText: 'Evidencias estadísticas' });
  await evidencias.getByTestId('stDataFrame').waitFor();
  if (movil) {
    assert.equal(await page.evaluate(() => document.querySelector('[data-testid="stMain"]').scrollWidth), 390);
  }
  if (movil) {
    await contraste.getByRole('heading', { level: 3 }).evaluate(el => el.scrollIntoView({ block: 'start' }));
    await page.screenshot({ path: path.join(output, '09-contraste-movil.png'), animations: 'disabled' });
  } else {
    await evidence(page, '08-contraste-r1');
    await contraste.getByRole('heading', { name: '¿Qué investigar ahora?' })
      .evaluate(el => el.scrollIntoView({ block: 'start' }));
    await page.screenshot({ path: path.join(output, '10-que-investigar.png'), animations: 'disabled' });
  }
  await contraste.getByRole('button', { name: 'Abrir comparación en Territorio' }).click();
  await heading(page, 'Territorio');
  await heading(page, 'Perfil productivo comparado', 3);
  await ready(page);
  assert.equal(await select(page, 'Departamento').getByRole('combobox').inputValue(), 'Chimaltenango');
  assert.equal(await select(page, 'Comparar con').getByRole('combobox').inputValue(), 'Alta Verapaz');
  results.push(`${movil ? 'Móvil' : 'Escritorio'}: R1 en un clic con comparación, evidencia abierta y ficha de investigación. Comparación territorial preseleccionada en el segundo clic.`);
}


(async () => {
  await fs.mkdir(output, { recursive: true });
  const options = {
    executablePath: process.env.FARO_CHROME,
    args: ['--proxy-server=http://127.0.0.1:9', '--proxy-bypass-list=127.0.0.1;localhost'],
  };
  const browser = await chromium.launch(options);
  try {
    const desktopContext = await browser.newContext({ viewport: { width: 1440, height: 1000 }, acceptDownloads: true, serviceWorkers: 'block' });
    await configure(desktopContext);
    const desktopPage = await desktopContext.newPage();
    desktopPage.setDefaultTimeout(12000);
    watch(desktopPage);
    if (!soloDestacado) await desktop(desktopPage);
    await destacado(desktopPage);
    await desktopContext.close();
    const mobileContext = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, serviceWorkers: 'block' });
    await configure(mobileContext);
    const mobilePage = await mobileContext.newPage();
    mobilePage.setDefaultTimeout(12000);
    watch(mobilePage);
    if (!soloDestacado) await mobile(mobilePage);
    await destacado(mobilePage, true);
    await mobileContext.close();
    assert.deepEqual([...errors], [], 'Consola, errores de JavaScript o respuestas HTTP inválidas');
    assert.deepEqual([...blocked], [], 'Intentos de acceso a red externa');
    await fs.writeFile(path.join(output, soloDestacado ? 'chromium-destacado.txt' : 'chromium.txt'),
      `Chromium ${browser.version()} · Red externa bloqueada (HTTP, HTTPS y WebSocket)\n` +
      results.map(line => `✓ ${line}`).join('\n') + '\n0 errores de consola o JavaScript. 0 solicitudes externas.\n');
    console.log(results.join('\n'));
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error, { results, errors: [...errors], blocked: [...blocked] });
  process.exitCode = 1;
});
