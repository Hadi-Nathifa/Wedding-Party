const {shoot}=require('./capture');
const S={
 intro:{frames:100,dpr:4,init:async H=>H.scrollTo(0)},
 hero:{frames:100,dpr:3,init:async H=>H.scrollTo(300),scroll:[[0,99,300,350]]},
 tapmenu:{frames:80,dpr:3,init:async H=>H.scrollTo(350),at:{22:async H=>H.tap('.hero-actions .btn.solid',false)},scroll:[[30,52,350,1469]]},
 hot:{frames:180,dpr:3,init:async H=>H.scrollTo(1469),scroll:[[6,34,1469,1660],[70,165,1660,2550]]},
 chips:{frames:250,dpr:3,init:async H=>H.scrollTo(1660),
   every:async(H,f)=>{const k=Math.floor((f+10)/36), ph=(f+10)%36; const c=[1,2,3,5,6,7][k]; if(c===undefined||ph>9)return;
     await H.page.evaluate(([c,t])=>{const row=document.getElementById('chips'),ch=row.querySelector('.chip[data-i="'+c+'"]');const r=ch.getBoundingClientRect(),pr=row.getBoundingClientRect();
       const want=(r.left+r.width/2)-(pr.left+pr.width/2); row.scrollLeft+=want*t;},[c,ph===9?1:0.35]);},
   at:Object.fromEntries([1,2,3,5,6,7].map((c,k)=>[26+36*k,async H=>H.tap(`#chips .chip[data-i="${c}"]`,'direct')]))},
 search:{frames:90,dpr:3,init:async H=>H.scrollTo(1660),at:{8:async H=>{await H.tap('#q',false);},16:H=>H.type('#q','ل'),22:H=>H.type('#q','و'),28:H=>H.type('#q','ت'),34:H=>H.type('#q','س')}},
 stamps:{frames:140,dpr:4,init:async H=>{await H.scrollTo(1100);await H.page.evaluate(()=>document.querySelectorAll('.stamp:not(.gift)').forEach(s=>s.classList.add('pre')));},
   at:Object.assign(Object.fromEntries([0,1,2,3].map(k=>[16+18*k,H=>H.page.evaluate(k=>{const s=document.querySelectorAll('.stamp:not(.gift)')[k];s.classList.remove('pre');s.classList.add('pop')},k)])),{88:H=>H.page.evaluate(()=>document.querySelector('.stamp.gift').classList.add('glow'))})},
 dark:{frames:80,dpr:3,init:async H=>H.scrollTo(1660),at:{22:async H=>H.tap('#themeBtn','direct')}},
 visit:{frames:160,dpr:4,init:async H=>H.scrollTo(3187),scroll:[[70,100,3187,3640]]},
 book:{frames:120,dpr:3,init:async H=>H.scrollTo(4006),at:{6:async H=>H.tap('#fName',false),12:H=>H.type('#fName','ع'),16:H=>H.type('#fName','ل'),20:H=>H.type('#fName','ي'),88:async H=>H.tap('#book button[type=submit]',false)},scroll:[[40,70,4006,4293]]},
 outro:{frames:130,dpr:4,init:async H=>H.scrollTo(0)},
};
(async()=>{const names=process.argv.slice(2);for(const n of names) await shoot({name:n,...S[n]});})();
