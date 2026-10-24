import { chromium } from 'playwright';
import { readFileSync } from 'fs';
const S = process.argv[2], OUT = process.argv[3];
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
const page = await (await browser.newContext({ viewport: { width: 1440, height: 900 } })).newPage();
page.setDefaultTimeout(180000);
page.on('pageerror', e => console.log('pageerror:', e.message));
await page.route('**/three.min.js', r => r.fulfill({ body: readFileSync(S + '/three/package/build/three.min.js'), contentType: 'text/javascript' }));
await page.route('**/OrbitControls.js', r => r.fulfill({ body: readFileSync(S + '/three/package/examples/js/controls/OrbitControls.js'), contentType: 'text/javascript' }));
await page.route('https://fonts.**', r => r.abort());
await page.goto('http://127.0.0.1:8765/anatomy-atlas.html');
await page.waitForFunction(() => getComputedStyle(document.getElementById('load')).opacity === '0');
await page.click('#modeSwitch [data-mode="bones"]'); await page.waitForTimeout(800);
for (const q of ['femur', 'scapula', 'hyoid', 'coccyx']) {
  await page.fill('#organSearch', q); await page.waitForTimeout(300);
  console.log(q, '->', await page.$$eval('#organList .ocard', b => b.map(x => x.innerText.replace(/\n/g, ' / '))), await page.$eval('#organList', e => e.innerText.includes('No bone region') ? 'none' : ''));
}
await page.fill('#organSearch', 'femur'); await page.waitForTimeout(300);
await page.click('#organList .ocard'); await page.waitForTimeout(2500);
await page.screenshot({ path: OUT + '/bones-search.png' });
await page.click('#modeSwitch [data-mode="organs"]'); await page.fill('#organSearch', ''); await page.waitForTimeout(500);
await page.click('.ocard[data-key="prostate"]'); await page.waitForTimeout(2500);
await page.screenshot({ path: OUT + '/body-prostate.png' });
await browser.close();
