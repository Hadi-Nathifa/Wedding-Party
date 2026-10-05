import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve
SR=44100; FPS=30; BEAT=0.6; BAR=4*BEAT
rng=np.random.default_rng(7)
def t_(d): return np.arange(int(d*SR))/SR
def place(buf,x,t,gain=1.0,pan=0.0):
    i=int(round(t*SR));
    if x.ndim==1:
        l=np.cos((pan+1)*np.pi/4); r=np.sin((pan+1)*np.pi/4); x=np.stack([x*l*1.414,x*r*1.414],1)
    n=min(len(x),len(buf)-i)
    if n>0 and i>=0: buf[i:i+n]+=x[:n]*gain
def lp(x,f,o=2): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x,axis=0)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x,axis=0)
def bp(x,lo,hi,o=2): return sosfilt(butter(o,[lo,hi],'band',fs=SR,output='sos'),x,axis=0)
def svf_sweep(x,fc,q=0.7):
    # time-varying state-variable bandpass; fc array per sample
    y=np.zeros_like(x); low=band=0.0
    f=2*np.sin(np.pi*np.clip(fc,20,SR/4)/SR); damp=1/q
    for i in range(len(x)):
        high=x[i]-low-damp*band; band+=f[i]*high; low+=f[i]*band; y[i]=band
    return y
def reverb(x,dur=1.8,mix=0.25,damp=4000,seed=1):
    r=np.random.default_rng(seed); n=int(dur*SR); tt=np.arange(n)/SR
    ir=np.stack([r.standard_normal(n),r.standard_normal(n)],1)*np.exp(-tt*6.9/dur)[:,None]
    ir=lp(ir,damp); ir[:int(0.012*SR)]*=np.linspace(0,1,int(0.012*SR))[:,None]; ir/=np.sqrt((ir**2).sum(0))
    if x.ndim==1: x=np.stack([x,x],1)
    wet=np.stack([fftconvolve(x[:,c],ir[:,c])[:len(x)] for c in range(2)],1)
    return x*(1-mix)+wet*mix*1.6
def mtof(m): return 440*2**((m-69)/12)

# ---------------- MUSIC ----------------
def kick(v=1):
    t=t_(0.5); f=45+95*np.exp(-t*28); ph=2*np.pi*np.cumsum(f)/SR
    x=np.sin(ph)*np.exp(-t*7)+0.25*np.exp(-t*300)*rng.standard_normal(len(t))*0.4
    return np.tanh(x*1.6)*v
def snare(v=1):
    t=t_(0.45); n=rng.standard_normal(len(t))
    body=np.sin(2*np.pi*185*t)*np.exp(-t*22)*0.55
    noise=bp(n,900,7000)*np.exp(-t*13)
    return (body+noise*0.9)*v
def hat(v=1,open_=False):
    t=t_(0.35 if open_ else 0.07); n=hp(rng.standard_normal(len(t)),7000,4)
    return n*np.exp(-t*(9 if open_ else 70))*v*0.5
def shaker(v=1):
    t=t_(0.09); n=bp(rng.standard_normal(len(t)),5000,12000)
    return n*np.sin(np.pi*np.clip(t/0.09,0,1))**2*v*0.25
def rhodes(m,d,v=1):
    t=t_(d+1.2); f=mtof(m)
    idx=1.6*np.exp(-t*5)+0.25
    mod=np.sin(2*np.pi*f*t)*idx
    x=np.sin(2*np.pi*f*t+mod)*np.exp(-t*1.1)
    x+=0.12*np.sin(2*np.pi*f*7*t)*np.exp(-t*14)  # tine bell
    rel=np.ones_like(t); k=int(d*SR); rel[k:]=np.exp(-(t[k:]-d)*6)
    x*=rel*(1+0.12*np.sin(2*np.pi*4.5*t))
    a=int(0.004*SR); x[:a]*=np.linspace(0,1,a)
    return x*v
def bass(m,d,v=1):
    t=t_(d+0.15); f=mtof(m)
    x=np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t)*np.exp(-t*3)
    env=np.minimum(1,t/0.01)*np.where(t<d,1,np.exp(-(t-d)*30))
    return np.tanh(x*1.3)*env*v
def pluck(m,v=1):
    t=t_(1.4); f=mtof(m)
    x=(np.sin(2*np.pi*f*t)+0.4*np.sin(4*np.pi*f*t)*np.exp(-t*6)+0.15*np.sin(6*np.pi*f*t)*np.exp(-t*9))*np.exp(-t*3.2)
    a=int(0.003*SR); x[:a]*=np.linspace(0,1,a); return x*v

NBARS=18; TOTAL=43.2
drums=np.zeros((int(TOTAL*SR)+SR,2)); keys=drums.copy(); bas=drums.copy(); mel=drums.copy()
prog=[[53,57,60,64,67],[52,55,59,62,67],[57,60,64,67,71],[50,53,57,60,64]]  # Fmaj9 Em7 Am9 Dm9
roots=[41,40,45,38]
final=[48,52,55,59,62]  # Cmaj9
sw=lambda step: step*BEAT/4 + (0.045 if step%2 else 0)
for b in range(NBARS):
    T0=b*BAR; ch=prog[b%4] if b<16 else final; rt=roots[b%4] if b<16 else 36
    full = 1<=b<=15
    # keys: on 1 and the "and of 2"
    if b<17:
        for k,(st,d,v) in enumerate([(0,0.9,0.5),(6,1.3,0.38)] if b>=1 else [(0,2.3,0.5)]):
            for j,m in enumerate(ch): place(keys,rhodes(m,d,v*(0.9 if j else 1)),T0+sw(st)+j*0.012,0.16,pan=(j-2)*0.18)
    else:
        for j,m in enumerate(ch): place(keys,rhodes(m,3.5,0.5),T0+j*0.03,0.18,pan=(j-2)*0.18)
    if full:
        place(bas,bass(rt,0.5),T0,0.32); place(bas,bass(rt,0.25),T0+sw(7),0.22); place(bas,bass(rt+7 if b%2 else rt+12,0.3),T0+sw(10),0.24)
        breakbar = (b==8)   # search bar: half-time filter break
        for st in range(16):
            tt=T0+sw(st)
            if st in (0,10) or (st==7 and b%2): place(drums,kick(0.95 if st==0 else 0.75),tt,0.55 if not breakbar else 0.0)
            if st in (4,12) and not breakbar: place(drums,snare(),tt,0.30,pan=0.05)
            if st%2==0: place(drums,hat(0.7 if st%4==0 else 0.45),tt,0.32,pan=-0.25)
            if st==14: place(drums,hat(0.5,True),tt,0.25,pan=-0.25)
            if st%2==1: place(drums,shaker(0.6+0.3*rng.random()),tt,0.4,pan=0.35)
        if breakbar: place(drums,kick(0.9),T0,0.5)
    # melody pluck on some bars
    if b in (4,5,6,7,12,13,14,15):
        pat=[(0,72),(3,76),(6,79),(10,77),(13,76)] if b%2==0 else [(0,74),(4,72),(8,69),(11,72)]
        for st,m in pat: place(mel,pluck(m,0.5),T0+sw(st),0.09,pan=0.3)
# intro filter sweep (bar 0) and last bars
L=len(keys)
keys=reverb(keys,2.2,0.3); mel=reverb(mel,2.5,0.4,seed=3); drums=reverb(drums,0.9,0.12,seed=5)
music=keys+bas+mel+drums
# sidechain-ish: duck on kicks
env=np.ones(L)
for b in range(1,16):
    for st in (0,10):
        i=int((b*BAR+sw(st))*SR); n=int(0.22*SR); env[i:i+n]=np.minimum(env[i:i+n],1-0.25*np.exp(-np.arange(n)/SR*14))
music*=env[:,None]
# intro lowpass sweep 0-2.4s
n0=int(BAR*SR); seg=music[:n0+int(0.1*SR)].copy(); out=np.zeros_like(seg)
blk=1024
for i in range(0,len(seg),blk):
    fc=350*(1+ (i/len(seg))**2*40); fc=min(fc,16000)
    out[i:i+blk]=lp(seg[max(0,i-4096):i+blk],fc,2)[-len(seg[i:i+blk]):]
music[:len(seg)]=out
# vinyl crackle
cr=np.zeros(L); idx=rng.integers(0,L,int(TOTAL*14)); cr[idx]=rng.standard_normal(len(idx))*0.5
cr=hp(cr,1500)+lp(rng.standard_normal(L),900)*0.004
music+=np.stack([cr,np.roll(cr,113)],1)*0.05
sf.write('music.wav',music[:int(43.0*SR)]/np.abs(music).max()*0.9,SR)

# ---------------- SFX ----------------
def whoosh(d=0.7,peak=0.6,f0=300,f1=3500,f2=600,q=1.2,bright=1.0):
    t=t_(d); n=rng.standard_normal(len(t)); p=peak*d
    fc=np.where(t<p,f0+(f1-f0)*(t/p)**2,f1+(f2-f1)*((t-p)/(d-p))**0.7)
    x=svf_sweep(n,fc,q)
    env=np.where(t<p,(t/p)**2.2,np.exp(-(t-p)/(d-p)*4))
    rum=lp(rng.standard_normal(len(t)),180,2)*env*1.5
    x=x*env*bright+rum
    pan=np.clip((t/d)*2-1,-1,1)*0.8
    return np.stack([x*np.cos((pan+1)*np.pi/4),x*np.sin((pan+1)*np.pi/4)],1)*1.4
def click(f=3200,v=1):
    t=t_(0.05); x=np.sin(2*np.pi*f*t)*np.exp(-t*160)+0.5*hp(rng.standard_normal(len(t)),2000)*np.exp(-t*400)
    x+=0.5*np.sin(2*np.pi*900*t)*np.exp(-t*90)
    return x*v
def tap(v=1): return reverb(click(2600,v)+0.6*click(5200,v*0.5),0.4,0.15,seed=9)
def key(v=1):
    t=t_(0.06); f=1800+rng.random()*900
    x=np.sin(2*np.pi*f*t)*np.exp(-t*220)+0.6*bp(rng.standard_normal(len(t)),1500,6000)*np.exp(-t*260)
    x+=0.35*np.sin(2*np.pi*320*t)*np.exp(-t*80); return x*v
def stamp(v=1):
    t=t_(0.5); f=48+110*np.exp(-t*35)
    thump=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*12)
    slap=bp(rng.standard_normal(len(t)),300,3500)*np.exp(-t*55)*0.9
    ink=bp(rng.standard_normal(len(t)),2500,9000)*np.exp(-t*30)*0.25
    return reverb(np.tanh((thump*1.2+slap+ink)*1.3)*v,0.6,0.15,seed=4)
def impact(v=1):
    t=t_(2.5); f=32+70*np.exp(-t*9)
    sub=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*2.2)
    hit=lp(rng.standard_normal(len(t)),2500)*np.exp(-t*18)
    x=np.tanh((sub*1.3+hit*0.8)*1.2)
    return reverb(x,2.2,0.3,seed=11)*v
def riser(d=2.3,v=1):
    t=t_(d); n=rng.standard_normal(len(t))
    fc=200+6000*(t/d)**2.5
    x=svf_sweep(n,fc,2.5)*(t/d)**2
    tone=np.sin(2*np.pi*np.cumsum(180+700*(t/d)**2)/SR)*(t/d)**3*0.25
    x=x+tone; x[-int(0.02*SR):]*=np.linspace(1,0,int(0.02*SR))
    return reverb(x,1.2,0.25,seed=12)*v
def shimmer(v=1,n=9,base=84,d=1.6):
    out=np.zeros(int((d+2)*SR)); sc=[0,2,4,7,9,12,14,16,19]
    for k in range(n):
        m=base+sc[rng.integers(len(sc))]; tt=t_(1.6); f=mtof(m)
        x=(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*f*2.76*tt)*np.exp(-tt*8))*np.exp(-tt*3.5)*(0.5+0.5*rng.random())
        i=int(k*d/n*SR); out[i:i+len(x)]+=x
    return reverb(out*0.35*v,2.5,0.5,seed=13)
def ping(v=1):
    t=t_(1.2); x=np.sin(2*np.pi*1320*t)*np.exp(-t*5)+0.3*np.sin(2*np.pi*2640*t)*np.exp(-t*9)
    return reverb(x*v,2.0,0.45,seed=14)
def pop(v=1):
    t=t_(0.12); f=500+900*np.exp(-t*60); x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*35)
    return reverb(x*v,0.5,0.15,seed=15)
def toggle(v=1):
    a=click(1800,1)*0.8; b=np.zeros(int(0.08*SR)); b=np.concatenate([b,click(2400,0.7)])
    x=np.zeros(max(len(a),len(b))); x[:len(a)]+=a; x[:len(b)]+=b
    t=t_(0.9); sw_=np.sin(2*np.pi*np.cumsum(70+40*np.exp(-t*4))/SR)*np.sin(np.pi*np.clip(t/0.9,0,1))*0.6
    y=np.zeros(len(t)); y[:len(x)]+=x; y+=sw_
    return reverb(y*v,1.0,0.2,seed=16)
def swish(v=1): return whoosh(0.32,0.5,900,6500,2500,1.6)*v
def scrollwhoosh(d=0.75,v=1): return whoosh(d,0.5,250,2200,400,0.9)*v
np.save('sfxlib.npy',np.array([0]))
SFX=dict(whoosh=whoosh,click=click,tap=tap,key=key,stamp=stamp,impact=impact,riser=riser,shimmer=shimmer,ping=ping,pop=pop,toggle=toggle,swish=swish,scrollwhoosh=scrollwhoosh)
