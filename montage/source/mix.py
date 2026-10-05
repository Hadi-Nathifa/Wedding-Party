import numpy as np, soundfile as sf
exec(open('audio.py').read().split('# ---------------- MUSIC')[0])
src=open('audio.py').read(); exec(src[src.index('# ---------------- SFX'):])
F=lambda f:f/30.0
DUR=1262/30+0.6
bus=np.zeros((int(DUR*SR),2))
music,_=sf.read('music.wav'); n=min(len(music),len(bus)); 
m=music[:n].copy()
fo=int(41.0*SR); m[fo:]*=np.linspace(1,0,n-fo)[:,None]**1.5
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
bus=np.tanh(bus*1.1)/np.tanh(1.1)
sf.write('mix.wav',bus/np.abs(bus).max()*0.95,SR,subtype='PCM_24')
print('ok',len(bus)/SR)
