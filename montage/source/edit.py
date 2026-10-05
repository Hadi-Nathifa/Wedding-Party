import cv2, numpy as np, glob, os, subprocess, sys, json
W,H,FPS=1080,1920,30
CAP='../cap'
def eio(t): t=min(max(t,0),1); return 4*t**3 if t<.5 else 1-(-2*t+2)**3/2
def eout(t): t=min(max(t,0),1); return 1-(1-t)**4
cache={}
def frame(shot,i):
    fs=SHOTS[shot]['files']; i=int(min(max(i,0),len(fs)-1)); k=(shot,i)
    if k not in cache:
        if len(cache)>40: cache.pop(next(iter(cache)))
        cache[k]=cv2.imread(fs[i]).astype(np.float32)
    return cache[k]
SHOTS={}
for s in ['intro','hero','tapmenu','hot','chips','search','stamps','dark','visit','book','outro']:
    fs=sorted(glob.glob(f'{CAP}/{s}/*.jpg')); SHOTS[s]={'files':fs}
    im=cv2.imread(fs[0]); SHOTS[s]['dpr']=im.shape[1]/360
# scroll schedules (css px) for motion blur: (f0,f1,y0,y1), sticky css height
SCROLL={'tapmenu':([(30,52,350,1469)],64),'hot':([(6,34,1469,1660),(70,165,1660,2550)],184),'visit':([(70,100,3187,3640)],64),'book':([(40,70,4006,4293)],64)}
def scroll_vel(shot,f):
    if shot not in SCROLL: return 0,0
    v=0
    for f0,f1,y0,y1 in SCROLL[shot][0]:
        if f0<=f<=f1:
            d=1e-3; t=(f-f0)/(f1-f0); v=(eio(t+d)-eio(t-d))/(2*d)*(y1-y0)/(f1-f0)
    return v,SCROLL[shot][1]
def mblur_v(img,L,top):
    L=int(abs(L))
    if L<3: return img
    k=np.zeros((L,1),np.float32); k[:]=1/L
    out=img.copy(); out[top:]=cv2.filter2D(img,-1,k)[top:]; return out
# segments: name,start,end,shot,offset,camkeys[(lf,s,cx,cy)]
P=lambda s,cx=.5,cy=.5:(s,cx,cy)
SEG=[
 dict(n='intro',a=0,b=72,shot='intro',off=0,cam=[(0,2.5,.5,.3625),(8,2.3,.5,.37),(68,1.0,.5,.5)],ease=eio),
 dict(n='hero',a=72,b=144,shot='hero',off=0,cam=[(0,1.22,.5,.45),(9,1.03,.5,.48),(72,1.0,.5,.5)],ease=eout),
 dict(n='tapmenu',a=144,b=216,shot='tapmenu',off=4,cam=[(0,1.0,.5,.5),(16,1.16,.7875,.4977),(22,1.16,.7875,.4977),(30,1.0,.5,.5)]),
 dict(n='hot',a=216,b=360,shot='hot',off=20,cam=[(0,1.14,.5,.42),(12,1.02,.5,.5),(144,1.0,.5,.5)],ease=eout),
 dict(n='chips',a=360,b=576,shot='chips',off=8,cam=[(0,1.0,.5,.5),(216,1.06,.5,.45)],bumps=[18+36*k for k in range(6)]),
 dict(n='search',a=576,b=648,shot='search',off=0,cam=[(0,1.12,.5,.45),(8,1.02,.5,.48),(72,1.08,.5,.45)],ease=eout),
 dict(n='stamps',a=648,b=792,shot='stamps',off=-2,cam=[(0,1.0,.5,.5),(144,1.07,.5,.5)],bumps=[18,36,54,72,90]),
 dict(n='dark',a=792,b=864,shot='dark',off=4,cam=[(0,1.0,.5,.5),(72,1.07,.5,.46)],bumps=[18]),
 dict(n='visit',a=864,b=1008,shot='visit',off=0,cam=[(0,2.0,.611,.43),(10,1.9,.611,.43),(58,1.0,.5,.5),(144,1.03,.5,.5)]),
 dict(n='book',a=1008,b=1080,shot='book',off=34,cam=[(0,1.0,.5,.5),(48,1.03,.5,.5),(54,1.14,.5,.8),(72,1.16,.5,.8)]),
 dict(n='outro',a=1080,b=1224,shot='outro',off=0,cam=[(0,1.0,.5,.5),(144,1.3,.5,.4)]),
]
TRANS={72:('zoom',6),144:('whip',(-1,0),6),216:('zoom',6),360:('whip',(0,-1),6),576:('flash',0),648:('whip',(1,0),6),792:('zoom',6),864:('whip',(0,-1),6),1008:('whip',(-1,0),6),1080:('light',9)}
def interp(keys,lf,ease):
    if lf<=keys[0][0]: return keys[0][1:]
    for (f0,*a),(f1,*b) in zip(keys,keys[1:]):
        if f0<=lf<=f1:
            t=ease((lf-f0)/(f1-f0)); return tuple(x+(y-x)*t for x,y in zip(a,b))
    return keys[-1][1:]
def seg_render(seg,tf,extra_s=1.0,dx=0,dy=0,rot=0):
    lf=tf-seg['a']; sh=seg['shot']; src_i=seg['off']+lf
    img=frame(sh,round(src_i))
    dpr=SHOTS[sh]['dpr']; h,w=img.shape[:2]
    v,sticky=scroll_vel(sh,round(src_i))
    if v: img=mblur_v(img,v*dpr*0.5,int(sticky*dpr))
    s,cx,cy=interp(seg['cam'],lf,seg.get('ease',eio))
    for bf in seg.get('bumps',[]):
        d=lf-bf
        if 0<=d<10: s*=1+0.035*np.exp(-d/2.5)*(1 if d>0 else 0.5)
    s*=extra_s
    cx=min(max(cx,0.5/max(s,1)),1-0.5/max(s,1)) if extra_s==1 else cx
    cy=min(max(cy,0.5/max(s,1)),1-0.5/max(s,1)) if extra_s==1 else cy
    k=W/w*s
    M=cv2.getRotationMatrix2D((cx*w,cy*h),rot,k)
    M[0,2]+=W/2-cx*w+dx; M[1,2]+=H/2-cy*h+dy
    return cv2.warpAffine(img,M,(W,H),flags=cv2.INTER_CUBIC if k>1.05 else cv2.INTER_AREA,borderMode=cv2.BORDER_REFLECT)
def seg_at(tf):
    for s in SEG:
        if s['a']<=tf<s['b']: return s
    return SEG[-1]
def segs_by_cut(c): return [s for s in SEG if s['b']==c][0],[s for s in SEG if s['a']==c][0]
LEAK=None
def light_leak(p,seed=0):
    yy,xx=np.mgrid[0:H:8,0:W:8].astype(np.float32)
    g=np.zeros((H//8,W//8,3),np.float32)
    for (bx,by,r,col) in [(0.2+0.6*p,0.3,500,(60,150,255)),(0.9-0.5*p,0.7,650,(40,110,240)),(0.5,0.1+0.6*p,420,(150,210,255))]:
        d=((xx-bx*W)**2+(yy-by*H)**2)/(r*r); g+=np.exp(-d)[...,None]*np.array(col,np.float32)
    return cv2.resize(g,(W,H),interpolation=cv2.INTER_LINEAR)
def render(tf):
    if tf>=NEON0: return neon(tf)
    # transitions
    for c,tr in TRANS.items():
        L=tr[-1] if tr[0]!='whip' else tr[2]
        if tr[0]=='flash' or not (c-L<=tf<c+L): continue
        A,B=segs_by_cut(c); K=7; acc=np.zeros((H,W,3),np.float32)
        for k in range(K):
            t=tf+(k/(K-1)-0.5)*0.9
            p=(t-(c-L))/(2*L)
            if tr[0]=='zoom':
                if t<c: q=min(max((t-(c-L))/L,0),1); img=seg_render(A,min(t,c-0.01),extra_s=1+0.9*q**2.2)
                else: q=min(max((t-c)/L,0),1); img=seg_render(B,t,extra_s=1+0.9*(1-q)**2.2)
            elif tr[0]=='whip':
                ddx,ddy=tr[1]; u=eio(p); span=W if ddx else H
                a=seg_render(A,min(t,c-0.01),dx=ddx*u*span,dy=ddy*u*span)
                b=seg_render(B,max(t,c),dx=ddx*(u-1)*span,dy=ddy*(u-1)*span)
                # composite: A occupies region before boundary
                if ddx: bnd=int(W/2+ddx*(u*span-span/2)) ; mask=np.zeros((H,W,1),np.float32); 
                if ddx>0: mask[:,:max(0,min(W,int(u*W)))]=1  # B enters from left
                elif ddx<0: mask[:,max(0,min(W,W-int(u*W))):]=1
                elif ddy<0: mask=np.zeros((H,W,1),np.float32); mask[max(0,min(H,H-int(u*H))):]=1
                else: mask=np.zeros((H,W,1),np.float32); mask[:max(0,min(H,int(u*H)))]=1
                img=a*(1-mask)+b*mask
            elif tr[0]=='light':
                q=eio(p); img=seg_render(A,min(t,c-0.01))*(1-q)+seg_render(B,max(t,c))*q
            acc+=img
        img=acc/K
        if tr[0]=='light':
            q=1-abs(p*2-1); img=img+light_leak(p)*q*1.2; img=img*(1+0.35*q)
        if tr[0]=='zoom':
            q=max(0,1-abs(tf-c)/3); img=img+255*0.55*q
        return img
    s=seg_at(tf); img=seg_render(s,tf)
    # flash cut punch
    for c,tr in TRANS.items():
        if tr[0]=='flash' and 0<=tf-c<7:
            q=np.exp(-(tf-c)/1.8); img=seg_render(s,tf,extra_s=1+0.12*q); img=img+(255-img)*0.85*q
    return img
# ---------- overlays ----------
def loadpng(n):
    im=cv2.imread(f'cap/{n}.png',cv2.IMREAD_UNCHANGED).astype(np.float32); return im
OV={n:loadpng(n) for n in [os.path.basename(f)[:-4] for f in glob.glob('cap/*.png')]}
CAPS=[('cap_menu',396,470,1700),('cap_search',584,646,1700),('cap_stamp1',668,734,330),('cap_stamp2',738,790,330),
      ('cap_dark',818,862,1720),('cap_visit',880,936,1700),('cap_hours',966,1006,1700),('cap_book',1012,1056,300)]
def paste(img,ov,cx,cy,scale=1.0,alpha=1.0):
    if alpha<=0.01: return img
    o=ov if abs(scale-1)<1e-3 else cv2.resize(ov,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC)
    h,w=o.shape[:2]; x0=int(cx-w/2); y0=int(cy-h/2)
    xa,ya=max(0,x0),max(0,y0); xb,yb=min(W,x0+w),min(H,y0+h)
    if xb<=xa or yb<=ya: return img
    sub=o[ya-y0:yb-y0,xa-x0:xb-x0]; a=sub[...,3:4]/255*alpha
    img[ya:yb,xa:xb]=img[ya:yb,xa:xb]*(1-a)+sub[...,:3]*a; return img
def caption_anim(tf,a,b):
    if tf<a or tf>=b: return None
    li=tf-a; lo=b-tf
    if li<9: t=li/9; s=0.82+0.22*eout(t)-0.04*max(0,t-0.6)/0.4; al=min(1,li/4); dy=60*(1-eout(t))
    else: s=1.0; al=1; dy=0
    if lo<6: q=lo/6; al*=q; s*=0.94+0.06*q; dy=-20*(1-q)
    return s,al,dy
VIGN=None
def finish(img,tf):
    global VIGN
    if VIGN is None:
        yy,xx=np.mgrid[0:H,0:W].astype(np.float32); d=((xx-W/2)/(W*0.75))**2+((yy-H/2)/(H*0.75))**2
        VIGN=(1-0.22*np.clip(d,0,1.5)**1.4)[...,None]
    if tf>=NEON0: CAPS_=[]
    else: CAPS_=CAPS
    for n,a,b,y in CAPS_:
        r=caption_anim(tf,a,b)
        if r: s,al,dy=r; img=paste(img,OV[n],W/2,y+dy,s,al)
    # outro end card
    if NEON0>tf>=1086:
        q=eout((tf-1086)/22)
        bl=cv2.GaussianBlur(img,(0,0),2+22*q); img=bl*(1-0.78*q)+np.array([16,28,58],np.float32)*0.78*q
        for n,st,y,sc in [('out_logo',1098,700,0.92),('out_title',1116,1170,1.0),('out_sub',1134,1305,1.0),('out_info',1152,1430,1.0),('out_phone',1170,1530,1.0)]:
            if tf>=st:
                li=tf-st; t=eout(li/12); s=sc*(0.7+0.3*t if n=='out_logo' else 0.92+0.08*t); al=min(1,li/6)
                if n=='out_logo': s*=1+0.015*np.sin((tf-st)/12)
                img=paste(img,OV[n],W/2,y+(0 if n=='out_logo' else 40*(1-t)),s,al)
    if tf<10: img=img*(tf/10)
    if 1200<tf<NEON0: img=img*max(0,(NEON0-tf)/24)**1.3
    if tf>END-22: img=img*max(0,(END-tf)/22)
    img=img*VIGN
    # warm grade + grain
    img=img*np.array([0.97,1.0,1.03],np.float32)
    g=np.random.default_rng(tf).standard_normal((H//2,W//2,1)).astype(np.float32)*3.2
    img=img+cv2.resize(g,(W,H))[...,None]
    return np.clip(img,0,255).astype(np.uint8)

NEON0=1224; END=1392
MAG=np.array([203,61,255],np.float32); CYA=np.array([255,232,57],np.float32)  # BGR
GL={}
def glowlayer(n,col):
    if n in GL: return GL[n]
    o=cv2.copyMakeBorder(OV[n],140,140,140,140,cv2.BORDER_CONSTANT,value=0); OV[n+'_p']=o; a=o[...,3]/255.0
    g1=cv2.GaussianBlur(a,(0,0),10); g2=cv2.GaussianBlur(a,(0,0),34)
    GL[n]=(g1,g2,col); return GL[n]
def add_neon(img,n,cx,cy,inten,scale=1.0,col=CYA):
    if inten<=0.01: return img
    g1,g2,c=glowlayer(n,col)
    o=OV[n+'_p']
    if scale!=1.0:
        o=cv2.resize(o,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC); g1=cv2.resize(g1,(o.shape[1],o.shape[0])); g2=cv2.resize(g2,(o.shape[1],o.shape[0]))
    h,w=o.shape[:2]; x0=int(cx-w/2); y0=int(cy-h/2)
    xa,ya=max(0,x0),max(0,y0); xb,yb=min(W,x0+w),min(H,y0+h)
    o=o[ya-y0:yb-y0,xa-x0:xb-x0]; g1=g1[ya-y0:yb-y0,xa-x0:xb-x0]; g2=g2[ya-y0:yb-y0,xa-x0:xb-x0]
    sub=img[ya:yb,xa:xb]
    glow=(g1[...,None]*1.25+g2[...,None]*0.9)*c[None,None,:]*inten
    sub+=glow
    a=o[...,3:4]/255*min(1,inten)
    core=o[...,:3]*0.55+c*0.45
    sub[:]=sub*(1-a)+np.maximum(core,sub)*a
    return img
def flick(tf,t0,seq='0100110111'):
    d=tf-t0
    if d<0: return 0.0
    if d<len(seq): return float(seq[d])*(0.7+0.3*(d/len(seq)))
    return 0.93+0.07*np.sin(tf*1.7)*np.sin(tf*0.37)
BG=None
def neon_bg(tf):
    global BG
    if BG is None:
        yy,xx=np.mgrid[0:H//4,0:W//4].astype(np.float32)*4; BG=(yy,xx)
    yy,xx=BG; t=(tf-NEON0)/30
    img=np.zeros((H//4,W//4,3),np.float32)+np.array([14,8,7],np.float32)
    for bx,by,r,col,amp in [(0.15+0.05*np.sin(t*.6),0.25,620,MAG,0.16),(0.85-0.05*np.sin(t*.5),0.78,700,CYA,0.14),(0.5,0.5,520,np.array([255,120,140],np.float32),0.06)]:
        d=((xx-bx*W)**2+(yy-by*H)**2)/(r*r); img+=np.exp(-d)[...,None]*col*amp
    # perspective grid floor
    img=cv2.resize(img,(W,H))
    hor=1580; 
    for k in range(1,14):
        y=int(hor+(H-hor)*(k/13)**2.2+((t*40)%((H-hor)/13)) * (k/13))
        if y<H: cv2.line(img,(0,y),(W,y),(CYA*0.10).tolist(),2)
    for k in range(-12,13):
        cv2.line(img,(int(W/2+k*40),hor),(int(W/2+k*260),H),(MAG*0.08).tolist(),2)
    fade=np.clip((np.arange(H)-hor)/(H-hor),0,1)[:,None,None]
    img[hor:]=img[hor:]*0+img[hor:]  # keep
    mask=np.ones((H,1,1),np.float32); mask[:hor]=1
    return img
def neon(tf):
    img=neon_bg(tf)
    if tf<NEON0+8: img*= (tf-NEON0)/8
    def ein(st,dur=12): return eout((tf-st)/dur) if tf>=st else 0.0
    q=ein(1228,14); img=paste(img,OV['n_kick'],W/2,560+30*(1-q),1.0,q)
    fn=flick(tf,1236); fd=flick(tf,1246,'1001011011')
    sc=0.88; wn=(OV['n_logo_neon'].shape[1]-80)*sc; wd=(OV['n_logo_digital'].shape[1]-80)*sc; gap=34; tot=wn+wd+gap
    x_neon=W/2-tot/2+wn/2; x_dig=W/2+tot/2-wd/2
    img=add_neon(img,'n_logo_neon',x_neon,690,fn,sc,MAG)
    img=add_neon(img,'n_logo_digital',x_dig,690,fd,sc,CYA)
    q=ein(1266,14)
    if q>0:
        o=OV['n_tag']; bl=max(0,(1-q)*14)
        if bl>0.5:
            o=o.copy(); o=cv2.GaussianBlur(o,(0,0),bl)
        img=paste(img,o,W/2,920+50*(1-q),0.94+0.06*q,q)
    q=ein(1280,12); img=paste(img,OV['n_sub'],W/2,1045+30*(1-q),1.0,q*0.95)
    # divider line drawing
    if tf>=1292:
        p=eout((tf-1292)/14); half=int(300*p)
        line=np.zeros((40,W,3),np.float32); 
        for x in range(W//2-half,W//2+half):
            u=(x-(W/2-300))/600; col=MAG*(1-u)+CYA*u; line[18:22,x]=col
        g=cv2.GaussianBlur(line,(0,0),6)
        img[1125:1165]+=line*1.0+g*2.2
    q=ein(1306,12); img=paste(img,OV['n_cta'],W/2,1230+30*(1-q),1.0,q)
    if tf>=1318:
        d=tf-1318; q=eout(d/10); s=0.7+0.3*q+0.05*np.exp(-max(0,d-6)/3)*(d>6)
        img=add_neon(img,'n_ig',W/2,1370,min(1,q)*(0.85+0.15*np.sin(tf*0.25)),s,CYA)
    return img

if __name__=='__main__':
    a,b=int(sys.argv[1]),int(sys.argv[2]); out=sys.argv[3]
    if out.endswith('.mp4') or out.endswith('.mov'):
        p=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
        for tf in range(a,b): p.stdin.write(finish(render(tf),tf).tobytes())
        p.stdin.close(); p.wait()
    else:
        os.makedirs(out,exist_ok=True)
        for tf in range(a,b): cv2.imwrite(f'{out}/{tf:04d}.jpg',finish(render(tf),tf))
