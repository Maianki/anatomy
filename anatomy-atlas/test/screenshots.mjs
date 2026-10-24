import { chromium } from 'playwright';
import { readFileSync } from 'fs';
const S = process.argv[2], OUT = process.argv[3], ORG = process.argv[4] || 'lungs', MODE = process.argv[5] || 'desk';
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
const W = MODE === 'phone' ? 400 : 1440, H = 860;
const page = await (await browser.newContext({ viewport: { width: W, height: H } })).newPage();
page.setDefaultTimeout(180000);
page.on('console', m => { if (m.type() === 'error' && !m.text().includes('404')) console.log('console:', m.text()); });
page.on('pageerror', e => console.log('pageerror:', e.message));
await page.route('**/three.min.js', r => r.fulfill({ body: readFileSync(S + '/three/package/build/three.min.js'), contentType: 'text/javascript' }));
await page.route('**/OrbitControls.js', r => r.fulfill({ body: readFileSync(S + '/three/package/examples/js/controls/OrbitControls.js'), contentType: 'text/javascript' }));
await page.route('https://fonts.**', r => r.abort());
await page.goto('http://127.0.0.1:8765/anatomy-atlas.html#' + ORG);
await page.waitForFunction(() => document.getElementById('hLoad').hidden && document.querySelectorAll('#partList .row').length > 0);
const wait = ms => page.waitForTimeout(ms);
const shot = async n => page.screenshot({ path: `${OUT}/${ORG}-${MODE}-${n}.png`, timeout: 180000 });
await wait(5000); await shot('1-overview'); console.log('OVERVIEW', await page.$eval('#hInfo', e => e.innerText.slice(0, 900)));
if (ORG === 'lungs') {
  await page.click('#partList .row:has-text("Right apical segmental bronchial tree")'); await wait(3500); await shot('2-segment');
  await page.click('#clearSel'); await page.click('[data-color="structure"]'); await wait(3000); await shot('3-structure');
  await page.click('[data-color="lobe"]'); await page.click('#tabFlow'); await page.click('#steps .step[data-i="2"]'); await wait(3500); await shot('4-tour');
  await page.click('#tabExplore'); await page.click('#partList .row:has-text("Right medial basal segmental bronchial tree")'); await wait(3000); await shot('5-gap'); console.log('GAPTEXT', await page.$eval('#hInfo', e => e.innerText.slice(0, 700)));
} else {
  await page.click('#partList .row[data-id]'); await wait(3000); await shot('2-part');
}
await page.click('#crumbBody'); await wait(2500); await page.click('#organList .row[data-key="right-lung"]'); await wait(3000); await shot('6-body');
await browser.close();
