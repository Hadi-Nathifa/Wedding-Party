const path=require('path');const fs=require('fs');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const SP=__dirname;
async function open(dpr=4,opts={}){
  const browser=await chromium.launch();
  const ctx=await browser.newContext({viewport:{width:360,height:640},deviceScaleFactor:dpr,isMobile:true,hasTouch:true,locale:'ar-IQ',colorScheme:'light'});
  const page=await ctx.newPage();
  await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({path:path.join(SP,'gf/fonts.css'),contentType:'text/css'}));
  await page.route('https://fonts.gstatic.com/LOCAL/**',r=>r.fulfill({path:path.join(SP,'gf',r.request().url().split('/LOCAL/')[1])}));
  await page.clock.install({time:new Date('2026-10-05T18:30:00+03:00')});
  await page.goto('file://'+SP+'/aroma.html',{waitUntil:'load'});
  await page.evaluate(()=>document.fonts.ready);
  await page.waitForTimeout(500);
  return {browser,page};
}
module.exports={open,SP};
