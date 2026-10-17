import math, random
random.seed(7)

# ---------- EDIT YOUR DATA HERE ----------
PLAYER = "ZIYANI MOUAD"
LEVEL, EXP, EXP_MAX = 23, 300, 800
SKILLS = [("Backend", 90), ("Frontend", 90), ("Mobile", 80), ("Styling", 100), ("Database", 85)]
HP, MP = 100, 90
STREAK_DAYS, STREAK_PCT = 12, 65
HABITS = [  # 4 weeks x 7 days (1 = done)
    [1,1,1,0,1,1,0],
    [1,1,1,1,1,0,1],
    [1,0,1,1,1,1,1],
    [1,1,1,1,0,0,0],
]
# -----------------------------------------

P1, P2, P3 = "#c084fc", "#a855f7", "#e9d5ff"
o = []
a = o.append
a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1440" width="720" height="1440" font-family="Georgia, \'Times New Roman\', serif">')
a('''<defs>
<radialGradient id="bg" cx="50%" cy="30%" r="80%"><stop offset="0" stop-color="#1a1230"/><stop offset="1" stop-color="#07040f"/></radialGradient>
<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="#a855f7"/><stop offset="1" stop-color="#d8b4fe"/></linearGradient>
<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="smoke"><feGaussianBlur stdDeviation="40"/></filter>
</defs>
<rect width="720" height="1440" fill="url(#bg)"/>''')

# smoke
for (x,y,rx,ry,op) in [(60,80,160,90,.35),(660,120,130,100,.3),(40,1330,170,110,.45),(680,1360,170,100,.45),(360,720,140,60,.12)]:
    a(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#6d3fc0" opacity="{op}" filter="url(#smoke)"/>')

# stars
for i in range(26):
    x, y = random.randint(40,680), random.randint(40,360)
    d = random.uniform(2,5)
    a(f'<circle cx="{x}" cy="{y}" r="{random.choice([1,1.5,2])}" fill="{P3}"><animate attributeName="opacity" values="0.1;1;0.1" dur="{d:.1f}s" repeatCount="indefinite"/></circle>')

# frame
a(f'<rect x="14" y="14" width="692" height="1412" rx="6" fill="none" stroke="#7c4dcc" stroke-width="2.5"/>')
a(f'<rect x="24" y="24" width="672" height="1392" rx="4" fill="none" stroke="#4c3380" stroke-width="1"/>')
for (x,y) in [(14,14),(706,14),(14,1426),(706,1426)]:
    a(f'<circle cx="{x}" cy="{y}" r="7" fill="#130924" stroke="{P2}" stroke-width="2"/>')

# title
a(f'<g filter="url(#glow)" text-anchor="middle" font-weight="bold" fill="{P3}">')
a('<text x="360" y="175" font-size="104" letter-spacing="2">LEVEL UP</text>')
a('<text x="360" y="285" font-size="104" letter-spacing="2">TRACKER</text></g>')
a(f'<text x="360" y="340" text-anchor="middle" font-size="22" letter-spacing="5" fill="#d9c8f5">PROGRESS MONITOR</text>')
a(f'<text x="360" y="362" text-anchor="middle" font-size="12" letter-spacing="3" fill="{P1}">PLAYER: {PLAYER}</text>')

def panel(x,y,w,h,title,head=44):
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#1a1228" stroke="#5b3fa0" stroke-width="1.5" opacity=".95"/>')
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{head}" rx="8" fill="#241a38" stroke="#6d4cc0" stroke-width="1.5"/>')
    a(f'<text x="{x+w/2}" y="{y+head/2+7}" text-anchor="middle" font-size="22" fill="#e2d4fa">{title}</text>')

def bar(x,y,w,pct,label=None,right=None):
    if label: a(f'<text x="{x}" y="{y-8}" font-size="13" fill="#cdb8f0">{label}</text>')
    if right: a(f'<text x="{x+w}" y="{y-8}" font-size="13" text-anchor="end" fill="{P1}">{right}</text>')
    a(f'<rect x="{x}" y="{y}" width="{w}" height="12" rx="6" fill="#0d0816" stroke="#3d2c66"/>')
    a(f'<rect x="{x}" y="{y}" width="{w*pct/100:.1f}" height="12" rx="6" fill="url(#bar)"/>')

# ---- SKILLS panel (left)
panel(60,380,390,400,"Skills")
cx, cy = 150, 610
oct_pts = " ".join(f"{cx+85*math.cos(math.radians(22.5+45*k)):.1f},{cy+85*math.sin(math.radians(22.5+45*k)):.1f}" for k in range(8))
a(f'<polygon points="{oct_pts}" fill="#1e1633" stroke="#6d5aa8" stroke-width="3"/>')
a(f'<g transform="translate({cx},{cy+5}) scale(.85)" filter="url(#glow)">'
  '<path d="M0,-70 C-28,-70 -42,-45 -42,-20 C-42,-5 -50,5 -70,20 L-80,70 L80,70 L70,20 C50,5 42,-5 42,-20 C42,-45 28,-70 0,-70 Z" fill="#8b78d0" opacity=".85"/>'
  '<ellipse cx="0" cy="-18" rx="22" ry="30" fill="#1a1228"/></g>')
a(f'<text x="{cx}" y="{cy+112}" text-anchor="middle" font-size="14" fill="#e2d4fa" letter-spacing="1">[ Lv. {LEVEL} ARCHITECT ]</text>')

rx0, ry0, R = 340, 610, 72
def pt(k, f): 
    ang = math.radians(-90 + 72*k)
    return rx0 + R*f*math.cos(ang), ry0 + R*f*math.sin(ang)
for f in (1, .75, .5, .25):
    a('<polygon points="' + " ".join("%.1f,%.1f" % pt(k,f) for k in range(5)) + '" fill="none" stroke="#4a3a78" stroke-width="1"/>')
for k in range(5):
    x,y = pt(k,1); a(f'<line x1="{rx0}" y1="{ry0}" x2="{x:.1f}" y2="{y:.1f}" stroke="#4a3a78"/>')
a('<polygon points="' + " ".join("%.1f,%.1f" % pt(k,SKILLS[k][1]/100) for k in range(5)) + f'" fill="{P2}" fill-opacity=".35" stroke="{P1}" stroke-width="2" filter="url(#glow)"/>')
for k,(n,v) in enumerate(SKILLS):
    x,y = pt(k,1.0); lx,ly = pt(k,1.28)
    a(f'<circle cx="{pt(k,v/100)[0]:.1f}" cy="{pt(k,v/100)[1]:.1f}" r="3.5" fill="{P3}"/>')
    a(f'<text x="{lx:.1f}" y="{ly+4:.1f}" text-anchor="middle" font-size="12" fill="#d9c8f5">{n}</text>')

# ---- STATS panel (right)
panel(470,380,200,235,"Stats")
a(f'<text x="490" y="450" font-size="13" fill="#cdb8f0">Experience</text>')
a(f'<text x="490" y="482" font-size="30" fill="#f1e8ff">{EXP}/{EXP_MAX}</text>')
bar(490,520,160,EXP/EXP_MAX*100,"Experience bar")
a(f'<text x="490" y="565" font-size="13" fill="{P1}">Lv {LEVEL}</text><text x="650" y="565" font-size="13" text-anchor="end" fill="{P1}">Lv {LEVEL+1}</text>')
a(f'<text x="490" y="595" font-size="11" fill="#9d86c9">Guild: YouCode (UM6P)</text>')

# ---- MASTERY panel
panel(470,635,200,235,"Mastery")
for i,(n,v) in enumerate(SKILLS):
    bar(490,704+i*32,160,v,n,f"{v}%")

# ---- VITALS panel
panel(470,890,200,175,"Vitals")
bar(490,970,160,HP,"HP (Energy)",f"{HP}%")
bar(490,1022,160,MP,"MP (Coffee)",f"{MP}%")
a(f'<text x="490" y="1054" font-size="11" fill="#9d86c9">Focus: Full-Stack &amp; Mobile</text>')

# ---- Quest log (left small panels)
panel(60,800,185,180,"Quest")
for i,t in enumerate(["Class: Shadow Architect","Active quest:","Building high-scale","systems"]):
    a(f'<text x="75" y="{868+i*24}" font-size="13" fill="{"#e2d4fa" if i<2 else "#b9a2e6"}">{t}</text>')
panel(265,800,185,180,"Arsenal")
for i,t in enumerate(["Java • Spring Boot","PHP • Laravel","React • React Native","Tailwind • MySQL"]):
    a(f'<text x="280" y="{868+i*24}" font-size="13" fill="#e2d4fa">{t}</text>')

# ---- Weekly habit
panel(60,1005,390,335,"Weekly Habit")
days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
for j,d in enumerate(days):
    a(f'<text x="{140+j*44}" y="1078" font-size="12" text-anchor="middle" fill="#bfa8ea">{d}</text>')
for i,row in enumerate(HABITS):
    y = 1120 + i*58
    a(f'<text x="76" y="{y+4}" font-size="13" fill="#bfa8ea">W{i+1}</text>')
    a(f'<line x1="70" y1="{y+28}" x2="440" y2="{y+28}" stroke="#2c2146"/>')
    for j,v in enumerate(row):
        x = 140 + j*44
        if v: a(f'<circle cx="{x}" cy="{y}" r="10" fill="{P1}" filter="url(#glow)"/>')
        else: a(f'<circle cx="{x}" cy="{y}" r="4" fill="#3d2c66"/>')
a(f'<text x="255" y="1325" font-size="11" text-anchor="middle" fill="#8f78bd">● quest completed</text>')

# ---- Streak gauge
panel(470,1085,200,255,f"{STREAK_DAYS} Day Streak")
gx, gy, gr = 570, 1250, 65
arc = f"M{gx-gr},{gy} A{gr},{gr} 0 0 1 {gx+gr},{gy}"
a(f'<path d="{arc}" fill="none" stroke="#2a1f45" stroke-width="22"/>')
a(f'<path d="{arc}" fill="none" stroke="{P1}" stroke-width="22" stroke-dasharray="{math.pi*gr*STREAK_PCT/100:.1f} {math.pi*gr:.1f}" filter="url(#glow)"/>')
a(f'<text x="{gx}" y="{gy-8}" text-anchor="middle" font-size="30" fill="#f1e8ff">{STREAK_DAYS}</text>')
a(f'<text x="{gx}" y="{gy+28}" text-anchor="middle" font-size="22" fill="{P3}">{STREAK_PCT}%</text>')
a(f'<text x="{gx}" y="{gy+55}" text-anchor="middle" font-size="11" fill="#8f78bd">of monthly goal</text>')

a('</svg>')
open("/mnt/user-data/outputs/assets/level-up-tracker.svg","w").write("\n".join(o))
print("ok")
