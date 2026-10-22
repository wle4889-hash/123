// Render an SVG/HTML scene to PNG with Playwright Chromium.
// Usage: node src/render.js <input.html> <output.png> [width] [height]
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const [input, output, w = '1080', h = '1920'] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(input));
  await page.waitForTimeout(300);
  await page.screenshot({ path: output, clip: { x: 0, y: 0, width: +w, height: +h } });
  await browser.close();
})();
