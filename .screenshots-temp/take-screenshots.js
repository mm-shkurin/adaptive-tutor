const fs = require("fs");
const path = require("path");
const puppeteer = require("puppeteer-core");

const chrome = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const root = path.resolve(__dirname, "..");

function walk(dir, acc = []) {
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name);
    if (name === "node_modules" || name === "screenshots" || name === "screenshots-live") continue;
    const stat = fs.statSync(full);
    if (stat.isDirectory()) walk(full, acc);
    else if (name.endsWith(".html")) acc.push(full);
  }
  return acc;
}

function targets(arg) {
  const given = arg ? path.resolve(root, arg) : path.join(root, "ProductSpecification", "stories");
  if (!fs.existsSync(given)) throw new Error("not found: " + given);
  if (fs.statSync(given).isDirectory()) return walk(given);
  return [given];
}

(async () => {
  const files = targets(process.argv[2]);
  const browser = await puppeteer.launch({
    executablePath: chrome,
    headless: true,
    args: ["--font-render-hinting=none"],
  });
  let ok = 0;
  for (const file of files) {
    const mobile = path.basename(path.dirname(file)) === "mobile";
    const page = await browser.newPage();
    await page.setViewport(mobile ? { width: 390, height: 844 } : { width: 1400, height: 900 });
    await page.goto("file:///" + file.replace(/\\/g, "/"), { waitUntil: "networkidle0" });
    const outDir = path.join(path.dirname(file), "screenshots");
    fs.mkdirSync(outDir, { recursive: true });
    const out = path.join(outDir, path.basename(file, ".html") + ".png");
    const card = await page.$(".mockup-card");
    if (card) await card.screenshot({ path: out });
    else await page.screenshot({ path: out, fullPage: true });
    await page.close();
    ok += 1;
    console.log(out);
  }
  await browser.close();
  console.log("shots " + ok);
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
