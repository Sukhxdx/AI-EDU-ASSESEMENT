#!/usr/bin/env node
const puppeteer = require("/tmp/node_modules/puppeteer-core");
const path = require("path");

const dir = path.resolve(__dirname);
const html = "file://" + path.join(dir, "poster.html");
const pdfPath = path.join(dir, "Sukhada_Dhingra_CA2_Concept_to_Application_MindMap.pdf");
const pngPath = path.join(dir, "Sukhada_Dhingra_CA2_Concept_to_Application_MindMap.png");

(async () => {
  const browser = await puppeteer.launch({
    executablePath: "/usr/local/bin/google-chrome",
    headless: true,
    args: ["--no-sandbox", "--disable-gpu", "--allow-file-access-from-files", "--font-render-hinting=none"],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 2245, height: 1588, deviceScaleFactor: 2 });
  await page.goto(html, { waitUntil: "networkidle0", timeout: 60000 });
  await page.pdf({
    path: pdfPath,
    width: "594mm",
    height: "420mm",
    printBackground: true,
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  });
  await page.screenshot({ path: pngPath, fullPage: false, type: "png" });
  await browser.close();
  console.log("wrote", pdfPath);
  console.log("wrote", pngPath);
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
