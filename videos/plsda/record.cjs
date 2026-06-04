// Playwright 錄製（FTIR PLS-DA）· 總片長 292 秒，錄 292.8 秒
const { chromium } = require('playwright');
const path = require('path');
const DIR = __dirname;
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required','--mute-audio','--no-sandbox','--disable-setuid-sandbox'] });
  const context = await browser.newContext({ viewport:{width:1920,height:1080}, deviceScaleFactor:1, recordVideo:{ dir: path.join(DIR,'renders'), size:{width:1920,height:1080} } });
  const page = await context.newPage();
  page.on('console', m=>console.log('PAGE LOG:', m.text())); page.on('pageerror', e=>console.error('PAGE ERROR:', e.stack||e.message));
  await page.goto('file:///'+path.join(DIR,'index.html').replace(/\\/g,'/')+'?render=true');
  console.log('Recording 292.8 seconds...'); await page.waitForTimeout(292800);
  await context.close(); await browser.close(); console.log('Recording completed.');
})();
