const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const templates = ['classic', 'modern', 'minimal'];  // Match your template filenames
const outputDir = './static/thumbnails';

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  for (const template of templates) {
    const url = `http://localhost:5000/preview-resume?template=${template}`;

    await page.setViewport({ width: 800, height: 1000, deviceScaleFactor: 2 });
    await page.goto(url, { waitUntil: 'networkidle0' });

    const screenshotPath = path.join(outputDir, `${template}.png`);
    await page.screenshot({ path: screenshotPath });

    console.log(`Generated thumbnail for: ${template}`);
  }

  await browser.close();
})();
