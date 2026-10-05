import numpy as np, soundfile as sf
exec(open('audio.py').read().split('# ---------------- MUSIC')[0])
src=open('audio.py').read(); exec(src[src.index('# ---------------- SFX'):])
F=lambda f:f/30.0
DUR=1392/30+0.4
bus=np.zeros((int(DUR*SR),2))
music,_=sf.read('music.wav'); n=min(len(music),len(bus)); 
m=music[:n].copy()
fo=int(40.3*SR); fe=int(41.6*SR); m[fo:fe]*=np.linspace(1,0,fe-fo)[:,None]**1.5; m[fe:]=0
bus[:n]+=m*0.62
ev=[]
def at(fr,x,g=1.0,pan=0.0,lead=0.0): place(bus,x,F(fr)-lead,g,pan)
# intro riser -> impact at drop
at(72,riser(2.3),0.55,lead=2.3)
at(72,impact(),0.55)
at(6,shimmer(0.8,7,84,1.4),0.35)
# transition whooshes (peak at cut)
for c,kind in [(144,'whip'),(216,'zoom'),(360,'whip'),(648,'whip'),(792,'zoom'),(864,'whip'),(1008,'whip')]:
    d=0.7; x=whoosh(d,0.6,250 if kind=='zoom' else 350,3200 if kind=='zoom' else 4200,500,1.1)
    at(c,x,0.55,lead=0.6*d)
at(576,whoosh(0.5,0.6,600,6000,1500,1.4),0.4,lead=0.3); at(576,impact(0.5),0.35)   # flash cut into break
# taps
for fr in [162]+[378+36*k for k in range(6)]+[584,810,1062]: at(fr,tap(),0.55,pan=0.1)
# chip slide swishes (out 220ms + in)
for k in range(6): at(378+36*k+4,swish(),0.32,pan=-0.2)
# typing
for fr in [592,598,604,610]: at(fr,key(),0.45,pan=0.05)
# scroll whooshes
at(170,scrollwhoosh(0.8),0.45); at(266,scrollwhoosh(1.6),0.18); at(934,scrollwhoosh(1.0),0.35)
# stamps
for i,fr in enumerate([666,684,702,720]): at(fr,stamp(),0.75,pan=-0.3+0.2*i)
at(738,shimmer(1,9,86,1.2),0.5)
# dark mode toggle
at(810,toggle(),0.6)
# map pings
for fr in [866,932,998]: at(fr,ping(),0.18 if fr!=866 else 0.25,pan=0.15)
# caption pops
for fr in [396,584,668,738,818,880,966,1012]: at(fr,pop(),0.22)
# outro
at(1080,shimmer(1,10,84,1.8),0.45); at(1080,whoosh(1.2,0.6,200,2500,300,0.8),0.5,lead=0.6)
at(1098,impact(0.8),0.6)
for fr in [1116,1134,1152,1170]: at(fr,pop(0.8),0.16)

# ---------- NEON DIGITAL end card ----------
def saw(f,t): return 2*((f*t)%1)-1
def pad(ms,d):
    t=t_(d); x=np.zeros(len(t))
    for m in ms:
        for det in (-0.12,0.0,0.11): x+=saw(mtof(m+det),t)
    x=lp(x,1400,2)/len(ms)/3
    env=np.minimum(1,t/1.2)*np.minimum(1,(d-t)/1.5)
    return reverb(x*env,3.0,0.45,seed=21)
def hum(d):
    t=t_(d); x=sum(np.sin(2*np.pi*120*k*t)/k**1.2 for k in range(1,9))
    return hp(x,90)*0.15
def zap(v=1):
    t=t_(0.07); n=rng.standard_normal(len(t))
    x=(hp(n,1500)*0.6+np.sign(np.sin(2*np.pi*120*t))*0.5)*np.exp(-t*45)
    return x*v
def arp_note(m,v=1):
    t=t_(0.9); f=mtof(m); x=(saw(f,t)*0.5+np.sin(2*np.pi*f*t))*np.exp(-t*6)
    x=lp(x,3000,2); a=int(0.003*SR); x[:a]*=np.linspace(0,1,a); return x*v
N0=1224
at(N0,pad([57,60,64,67,71],5.9),0.30)
at(N0,pad([45],5.9),0.2)
# flicker zaps synced with the visual sequences
for t0,seq in [(1236,'0100110111'),(1246,'1001011011')]:
    for d,ch in enumerate(seq):
        if ch=='1' and (d==0 or seq[d-1]=='0'): at(t0+d,zap(),0.45,pan=-0.3 if t0==1236 else 0.3)
h=hum((1372-1236)/30)*np.linspace(1,1,int((1372-1236)/30*SR))
at(1236,h,0.10)
at(1236,impact(0.7),0.45); at(1246,impact(0.4),0.25)
at(1266,shimmer(1,8,88,1.0),0.38); at(1266,whoosh(0.6,0.6,400,5000,900,1.2),0.35,lead=0.36)
at(1292,swish(),0.3)
at(1306,pop(0.9),0.2)
at(1318,pop(1),0.3); at(1318,shimmer(1,6,93,0.6),0.3)
# soft digital arpeggio
seq=[69,72,76,79,81,79,76,72]
fr=1266
k=0
while fr<1372:
    at(fr,arp_note(seq[k%8],0.5),0.10,pan=(-0.4 if k%2 else 0.4)); fr+=9; k+=1
# final fade
fe=int(1372/30*SR); bus[fe:]*=np.linspace(1,0,len(bus)-fe)[:,None]**1.6
bus=np.tanh(bus*1.1)/np.tanh(1.1)
sf.write('mix.wav',bus/np.abs(bus).max()*0.95,SR,subtype='PCM_24')
print('ok',len(bus)/SR)
