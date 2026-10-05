const {chromium}=require('/opt/node22/lib/node_modules/playwright');const fs=require('fs');const path=require('path');
const SP=__dirname;
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 await p.route('https://fonts.googleapis.com/**',r=>r.fulfill({path:path.join(SP,'gf/fonts.css'),contentType:'text/css'}));
 await p.route('https://fonts.gstatic.com/LOCAL/**',r=>r.fulfill({path:path.join(SP,'gf',r.request().url().split('/LOCAL/')[1])}));
 const ig='<svg width="46" height="46" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="#7DF3FF" stroke-width="2"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="#7DF3FF" stroke-width="2"/><circle cx="17.4" cy="6.6" r="1.3" fill="#7DF3FF"/></svg>';
 await p.setContent(`<html dir="rtl"><head><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Lalezar&display=swap">
 <style>body{margin:0;background:transparent}.item{display:inline-block;padding:40px}
 .kick{font:500 40px 'IBM Plex Sans Arabic';color:#AEB6CC;letter-spacing:2px}
 .logo{font:700 118px/1 'IBM Plex Sans Arabic';letter-spacing:16px;direction:ltr;white-space:nowrap}
 .logo .a{color:#FFE3F8}.logo .b{color:#E6FDFF}
 .tag{font:104px/1.2 Lalezar;color:#FFFFFF}
 .sub{font:500 44px/1.4 'IBM Plex Sans Arabic';color:#C9D0E2}
 .cta{font:600 46px 'IBM Plex Sans Arabic';color:#FFFFFF;letter-spacing:1px}
 .ig{display:inline-flex;align-items:center;gap:20px;padding:20px 44px;border-radius:999px;border:3px solid #39E8FF;background:rgba(57,232,255,.08);direction:ltr;
   font:700 54px 'IBM Plex Sans Arabic';color:#E6FDFF;letter-spacing:1px}
 </style></head><body><div id="z"></div></body></html>`);
 await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(800);
 const items={
  n_kick:`<div class="kick">تصميم وتنفيذ</div>`,
  n_logo_neon:`<div class="logo"><span class="a">NEON</span></div>`,
  n_logo_digital:`<div class="logo"><span class="b">DIGITAL</span></div>`,
  n_tag:`<div class="tag">نحوّل فكرتك إلى واقع</div>`,
  n_sub:`<div class="sub">مواقع إلكترونية بهوية تليق بمشروعك</div>`,
  n_cta:`<div class="cta">للطلب والتواصل</div>`,
  n_ig:`<div class="ig">${ig}<span>neon.digital.iq</span></div>`,
 };
 for(const [k,v] of Object.entries(items)){
  await p.evaluate(v=>{document.getElementById('z').innerHTML='<div class="item" id="it">'+v+'</div>'},v);
  await p.waitForTimeout(80);
  await p.locator('#it').screenshot({path:`${SP}/edit/cap/${k}.png`,omitBackground:true});
 }
 await b.close();console.log('ok');
})();
