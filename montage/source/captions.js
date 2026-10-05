const {chromium}=require('/opt/node22/lib/node_modules/playwright');const fs=require('fs');const path=require('path');
const SP=__dirname;
(async()=>{
 const html=fs.readFileSync(SP+'/aroma.html','utf8');
 const logo=html.match(/class="emblem"><img src="([^"]+)"/)[1];
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 await p.route('https://fonts.googleapis.com/**',r=>r.fulfill({path:path.join(SP,'gf/fonts.css'),contentType:'text/css'}));
 await p.route('https://fonts.gstatic.com/LOCAL/**',r=>r.fulfill({path:path.join(SP,'gf',r.request().url().split('/LOCAL/')[1])}));
 const bean='<svg width="34" height="46" viewBox="0 0 18 24"><ellipse cx="9" cy="12" rx="8" ry="11" fill="#D9B568"/><path d="M9 2c-3 5 3 8 0 20" stroke="#3A1C10" stroke-width="1.6" fill="none"/></svg>';
 await p.setContent(`<html dir="rtl"><head><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Lalezar&display=swap">
 <style>body{margin:0;background:transparent}
 .pill{display:inline-flex;align-items:center;gap:22px;padding:22px 46px 26px;border-radius:999px;background:rgba(46,22,13,.93);border:3px solid rgba(217,181,104,.85);
  box-shadow:0 18px 50px rgba(0,0,0,.35);color:#F6EAD0;font:72px/1.15 Lalezar}
 .pill .acc{color:#E3BF72}
 .t1{font:140px/1.1 Lalezar;color:#F6EAD0;text-shadow:0 10px 40px rgba(0,0,0,.5)}
 .t2{font:600 52px/1.4 'IBM Plex Sans Arabic';color:#F1E2BC;letter-spacing:.5px}
 .t3{font:700 46px/1.3 'IBM Plex Sans Arabic';color:#E3BF72;direction:ltr}
 .logo{width:520px;height:520px;border-radius:50%;box-shadow:0 0 0 18px rgba(241,226,188,.10),0 0 0 40px rgba(241,226,188,.05),0 40px 90px rgba(0,0,0,.5)}
 .item{display:inline-block;padding:10px}
 </style></head><body><div id="z"></div></body></html>`);
 await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(800);
 const items={
  cap_menu:`<div class="pill">${bean}<span>منيو كامل <span class="acc">بالأسعار</span></span></div>`,
  cap_stamp1:`<div class="pill">${bean}<span>كل زيارة = <span class="acc">ختم</span></span></div>`,
  cap_stamp2:`<div class="pill">${bean}<span>الزيارة الخامسة <span class="acc">مجاناً</span></span></div>`,
  cap_dark:`<div class="pill">${bean}<span>الوضع <span class="acc">الداكن</span></span></div>`,
  cap_visit:`<div class="pill">${bean}<span>مفرق <span class="acc">سنوني</span></span></div>`,
  cap_hours:`<div class="pill">${bean}<span>كل الأيام <span class="acc">٩ص – ١١م</span></span></div>`,
  cap_book:`<div class="pill">${bean}<span>احجز طاولتك على <span class="acc">واتساب</span></span></div>`,
  cap_search:`<div class="pill">${bean}<span>ابحث عن <span class="acc">مشروبك</span></span></div>`,
  out_logo:`<img class="logo" src="${logo}">`,
  out_title:`<div class="t1">أروما كافيه ٢</div>`,
  out_sub:`<div class="t2">هنا تُحضَّر القهوة كما يليق بها</div>`,
  out_info:`<div class="t2">مفرق سنوني · كل الأيام ٩ص – ١١م</div>`,
  out_phone:`<div class="t3">0751 785 9683 · @aroma.cafe.2</div>`,
 };
 fs.mkdirSync(SP+'/edit/cap',{recursive:true});
 for(const [k,v] of Object.entries(items)){
  await p.evaluate(v=>{document.getElementById('z').innerHTML='<div class="item" id="it">'+v+'</div>'},v);
  await p.waitForTimeout(100);
  await p.locator('#it').screenshot({path:`${SP}/edit/cap/${k}.png`,omitBackground:true});
 }
 await b.close();console.log('ok');
})();
