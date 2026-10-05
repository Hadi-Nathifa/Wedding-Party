const {open,SP}=require('./common');const fs=require('fs');
const FPS=30, DT=1000/FPS;
const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
const INJECT=`
html{scroll-behavior:auto!important}
.tap-fx{position:fixed;z-index:9999;pointer-events:none;width:46px;height:46px;margin:-23px 0 0 -23px;border-radius:50%;
 background:rgba(255,255,255,.55);border:2px solid rgba(255,255,255,.95);box-shadow:0 0 0 1px rgba(0,0,0,.15),0 4px 14px rgba(0,0,0,.25);
 animation:tapfx .55s cubic-bezier(.2,.8,.2,1) forwards}
@keyframes tapfx{0%{transform:scale(.4);opacity:0}18%{transform:scale(.8);opacity:1}100%{transform:scale(1.9);opacity:0}}
.stamp.pre{opacity:0;transform:scale(2.2) rotate(-25deg)}
.stamp.pop{animation:stamp .42s cubic-bezier(.3,1.6,.5,1) forwards}
@keyframes stamp{0%{opacity:0;transform:scale(2.2) rotate(-25deg)}60%{opacity:1;transform:scale(.88) rotate(4deg)}100%{opacity:1;transform:scale(1) rotate(0)}}
.stamp.gift.glow{animation:glow 1.2s ease-in-out infinite alternate}
@keyframes glow{from{box-shadow:0 0 0 0 rgba(217,181,104,0)}to{box-shadow:0 0 22px 6px rgba(217,181,104,.55);background:rgba(217,181,104,.15)}}
`;
async function stepAnims(page){
  await page.evaluate((dt)=>{
    window.__vt=window.__vt||new WeakMap();
    for(const a of document.getAnimations()){
      let v=window.__vt.get(a); if(v===undefined){v=0;}
      v+=dt; window.__vt.set(a,v);
      try{const end=a.effect&&a.effect.getComputedTiming().endTime;if(a.playState==='finished')continue;if(isFinite(end)&&v>=end){a.finish();}else{a.pause();a.currentTime=v;}}catch(e){}
    }
  },DT);
}
async function setup(page){
  await page.addStyleTag({content:INJECT});
  await page.evaluate(()=>{
    window.__scrollTarget=null;
    const orig=window.scrollTo.bind(window);
    window.__origScrollTo=orig;
    window.scrollTo=function(o,y){ if(typeof o==='object'&&o.behavior==='smooth'){window.__scrollTarget=o.top;return;} return orig(o,y); };
    Element.prototype.scrollBy=function(o){ if(o&&o.left!==undefined) this.scrollLeft+=o.left; };
    window.__tap=(x,y)=>{const d=document.createElement('div');d.className='tap-fx';d.style.left=x+'px';d.style.top=y+'px';document.body.appendChild(d);setTimeout(()=>d.remove(),900);};
  });
}
// a shot = {name, frames, dpr, init(page,H), at: {frameIndex: async fn}, scroll: [ [f0,f1,y0,y1] ] }
async function shoot(shot){
  const dir=`${SP}/cap/${shot.name}`; fs.rmSync(dir,{recursive:true,force:true}); fs.mkdirSync(dir,{recursive:true});
  const {browser,page}=await open(shot.dpr||3);
  await setup(page);
  const H={page,
    scrollTo:async y=>page.evaluate(y=>window.__origScrollTo(0,y),y),
    box:async sel=>page.locator(sel).first().boundingBox(),
    tap:async(sel,click=true)=>{if(click==='direct'){const b=await page.locator(sel).first().boundingBox();await page.evaluate(([x,y])=>window.__tap(x,y),[b.x+b.width/2,b.y+b.height/2]);await page.evaluate(s=>document.querySelector(s).click(),sel);return;}const b=await page.locator(sel).first().boundingBox();const x=b.x+b.width/2,y=b.y+b.height/2;
      await page.evaluate(([x,y])=>window.__tap(x,y),[x,y]); if(click) await page.evaluate(([x,y])=>{let e=document.elementFromPoint(x,y);e=e&&(e.closest("button,a,input")||e);e&&e.dispatchEvent(new MouseEvent("click",{bubbles:true,clientX:x,clientY:y}))},[x,y]); return [x,y];},
    type:async(sel,ch)=>page.evaluate(([s,c])=>{const i=document.querySelector(s);i.value+=c;i.dispatchEvent(new Event('input',{bubbles:true}))},[sel,ch]),
  };
  if(shot.init) await shot.init(H);
  const scrollAnim={};
  const log=[];
  for(let f=0;f<shot.frames;f++){
    if(shot.every) await shot.every(H,f);
    if(shot.at&&shot.at[f]){const r=await shot.at[f](H); if(r) log.push([f,r]);}
    // site-triggered smooth scroll
    const tgt=await page.evaluate(()=>{const t=window.__scrollTarget;window.__scrollTarget=null;return t});
    if(tgt!==null){scrollAnim.y0=await page.evaluate(()=>scrollY);scrollAnim.y1=tgt;scrollAnim.f0=f;scrollAnim.f1=f+(shot.scrollFrames||22);}
    for(const s of (shot.scroll||[])){ if(f>=s[0]&&f<=s[1]){const t=ease((f-s[0])/(s[1]-s[0]));await H.scrollTo(s[2]+(s[3]-s[2])*t);} }
    if(scrollAnim.f1!==undefined&&f>=scrollAnim.f0&&f<=scrollAnim.f1){const t=ease((f-scrollAnim.f0)/(scrollAnim.f1-scrollAnim.f0));await H.scrollTo(scrollAnim.y0+(scrollAnim.y1-scrollAnim.y0)*t);}
    await page.clock.runFor(DT);
    await stepAnims(page);
    await page.screenshot({path:`${dir}/${String(f).padStart(4,'0')}.jpg`,type:'jpeg',quality:93});
  }
  fs.writeFileSync(`${dir}/log.json`,JSON.stringify(log));
  await browser.close();
  console.log('done',shot.name,shot.frames);
}
module.exports={shoot};
