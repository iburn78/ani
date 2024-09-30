const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const GIFEncoder = require('gif-encoder-2');
const { createCanvas, loadImage } = require('canvas');

// Utility function to pause execution
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Load the local HTML file
  const htmlFilePath = path.resolve('js_02.html');
  await page.goto(`file://${htmlFilePath}`);

  // Set viewport to cover the animated element
  await page.setViewport({ width: 800, height: 600 }); // Adjust size as necessary

  // Create directory for frames
  const framesDir = 'frames';
  if (!fs.existsSync(framesDir)) {
    fs.mkdirSync(framesDir);
  }

  const totalFrames = 100; // Adjust as necessary
  const interval = 100; // Milliseconds between frames

  console.log('Starting GIF capture of frames...');

  for (let i = 0; i < totalFrames; i++) {
    const screenshotPath = path.join(framesDir, `frame_${i.toString().padStart(3, '0')}.png`);
    await page.screenshot({ path: screenshotPath, clip: { x: 0, y: 0, width: 800, height: 600 } });
    console.log(`Captured frame ${i + 1}/${totalFrames}`);
    await delay(interval);
  }

  await browser.close();
  console.log('Frame capture completed.');

  // Create GIF from frames
  const gifPath = 'animation.gif';
  const encoder = new GIFEncoder(800, 600); // Adjust dimensions to match viewport
  encoder.createReadStream().pipe(fs.createWriteStream(gifPath));

  encoder.start();
  encoder.setRepeat(0); // 0 for repeat, -1 for no repeat
  encoder.setDelay(interval); // Frame delay in ms

  for (let i = 0; i < totalFrames; i++) {
    const framePath = path.join(framesDir, `frame_${i.toString().padStart(3, '0')}.png`);
    const image = await loadImage(framePath);
    const canvas = createCanvas(800, 600); // Adjust dimensions to match viewport
    const ctx = canvas.getContext('2d');
    ctx.drawImage(image, 0, 0);
    encoder.addFrame(ctx);
  }

  encoder.finish();
  console.log(`GIF created successfully: ${gifPath}`);
})();
