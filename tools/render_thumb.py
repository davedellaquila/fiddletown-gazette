#!/usr/bin/env python3
"""Render an edition-archive thumbnail (480x360) in the paper's house style.

Usage: render_thumb.py editions/YYYY-MM-DD-<slot>.html editions/thumbs/<same>.jpg

Why this exists: the sandbox's headless Chromium is policy-blocked (Hatch WebGL
domain policy), so edition runs kept shipping text-only archive entries. This
renderer draws the edition's actual top — topbar, masthead + fiddle watermark,
dateline, weather bug, ticker line, lead headline, and the five-day outlook —
from the snapshot's OWN HTML and the paper's real CSS values, at the same
960-wide composition as the browser captures it replaces, downscaled to 480x360.
The watermark is the paper's real masthead photo; the forecast icons are simple
drawn glyphs (sun / partly / cloud / rain) mapped from the panel's condition text.
"""
import re, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF   = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_I = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
SANS_B  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS    = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

BG=(247,241,227); PAPER=(255,253,246); TEXT=(28,25,23); MUTED=(107,98,89)
BORDER=(216,205,180); GOLD=(184,134,11); ACCENT=(138,31,31); BLUE=(74,127,165)

def F(path, size): return ImageFont.truetype(path, size)
def clean(s): return re.sub(r'\s+',' ', re.sub(r'<!--.*?-->','', s, flags=re.S)).strip()
def strip(s): return clean(re.sub(r'<[^>]+>',' ', s))
def wrap(dr, text, font, maxw):
    words=text.split(); lines=[]; cur=''
    for wd in words:
        t=(cur+' '+wd).strip()
        if dr.textlength(t, font=font)<=maxw: cur=t
        else:
            if cur: lines.append(cur)
            cur=wd
    if cur: lines.append(cur)
    return lines

def sun(dr, cx, cy, r, color=(232,164,32)):
    import math
    for a in range(0,360,45):
        x1=cx+math.cos(math.radians(a))*(r+3); y1=cy+math.sin(math.radians(a))*(r+3)
        x2=cx+math.cos(math.radians(a))*(r+8); y2=cy+math.sin(math.radians(a))*(r+8)
        dr.line([x1,y1,x2,y2], fill=color, width=3)
    dr.ellipse([cx-r,cy-r,cx+r,cy+r], fill=(250,197,66), outline=color, width=2)
def cloud(dr, cx, cy, s=1.0, color=(150,150,150)):
    dr.ellipse([cx-16*s,cy-4*s,cx+2*s,cy+10*s], fill=(235,235,235), outline=color)
    dr.ellipse([cx-6*s,cy-11*s,cx+14*s,cy+8*s], fill=(240,240,240), outline=color)
    dr.rectangle([cx-16*s,cy+2*s,cx+14*s,cy+10*s], fill=(238,238,238))
def icon(dr, kind, cx, cy):
    if kind=='sun': sun(dr,cx,cy,10)
    elif kind=='partly': sun(dr,cx-6,cy-5,7); cloud(dr,cx+4,cy+6,0.85)
    elif kind=='rain':
        cloud(dr,cx,cy-4,1.0)
        for dx in (-9,0,9): dr.line([cx+dx,cy+10,cx+dx-3,cy+17], fill=BLUE, width=2)
    else: cloud(dr,cx,cy,1.05)

def main(src, out):
    t=open(src, encoding='utf-8').read()
    dateline=strip(re.search(r'class="dateline">(.*?)</p>', t, re.S).group(1))
    bug=strip(re.search(r'<!-- WEATHER:BUG -->(.*?)<!-- /WEATHER:BUG -->', t, re.S).group(1))
    headline=strip(re.search(r'<!-- LEAD:HEADLINE -->(.*?)<!-- /LEAD:HEADLINE -->', t, re.S).group(1))
    toc=re.search(r'id="toc-list">(.*?)</div>', t, re.S).group(1)
    items=[strip(x) for x in re.findall(r'<a[^>]*>(.*?)</a>', toc)][:6]
    i=t.find('The Outlook'); seg=t[i:i+5200]
    seg=re.sub(r'<!--.*?-->','',seg,flags=re.S); seg=re.sub(r'<svg.*?</svg>',' @ ',seg,flags=re.S)
    parts=[p.strip() for p in re.sub(r'<[^>]+>','|',seg).split('|')]
    parts=[p for p in parts if p]
    src_line=parts[1] if len(parts)>1 else ''
    days=[]; j=2
    DAYNAMES=('Today','Fri','Sat','Sun','Mon','Tue','Wed','Thu')
    while j < len(parts) and len(days)<5:
        if parts[j] in DAYNAMES:
            k=j+1; cond=''; nums=[]; pop=''
            while k < len(parts) and parts[k] not in DAYNAMES:
                p=parts[k]
                if p=='@': pass
                elif re.fullmatch(r'\d+°', p): nums.append(p)
                elif p=='/': pass
                elif p=='Dry' or p.startswith('Precip'): pop=p
                elif not cond: cond=p
                k+=1
            days.append((parts[j],cond,nums,pop)); j=k
        else: j+=1
    img=Image.new('RGB',(960,720),BG); dr=ImageDraw.Draw(img)
    # masthead watermark: the paper's real photo, faint, behind the masthead band
    try:
        wm=Image.open('media/giant-fiddle-closeup-masthead.jpg').convert('RGB')
        wm=wm.resize((960,300))
        wm=ImageEnhance.Color(wm).enhance(0.55)
        base=Image.new('RGB',(960,300),BG)
        img.paste(Image.blend(base, wm, 0.10), (0,44))
    except Exception: pass
    dr=ImageDraw.Draw(img)
    # topbar
    dr.text((14,14),'🗞',font=F(SANS,20),fill=TEXT)
    dr.text((44,16),'The Fiddletown Gazette',font=F(SANS_B,17),fill=TEXT)
    nav='Front Page    Editions Archive    About'
    dr.text((960-14-dr.textlength(nav,font=F(SANS,15)),16),nav,font=F(SANS,15),fill=TEXT)
    for cx,col in [(742,GOLD),(768,GOLD),(794,GOLD),(820,(200,200,200)),(846,(200,200,200))]:
        dr.ellipse([cx-6,14,cx+6,26],fill=col)
    dr.rounded_rectangle([872,6,946,34],radius=14,fill=(90,140,220))
    dr.text((884,13),'Tip Jar',font=F(SANS_B,13),fill=(255,255,255))
    dr.line([0,45,960,45],fill=TEXT,width=2); dr.line([0,49,960,49],fill=TEXT,width=1)
    # masthead
    kick='FIDDLETOWN & THE SHENANDOAH VALLEY · UPDATED ALL DAY'
    kf=F(SANS_B,13); dr.text(((960-dr.textlength(kick,font=kf))/2,74),kick,font=kf,fill=GOLD)
    tf=F(SERIF_B,58); dr.text(((960-dr.textlength('The Fiddletown Gazette',font=tf))/2,98),'The Fiddletown Gazette',font=tf,fill=TEXT)
    df=F(SERIF_I,17); dr.text(((960-dr.textlength(dateline,font=df))/2,172),dateline,font=df,fill=MUTED)
    bf=F(SANS,14)
    bw=dr.textlength(bug,font=bf)+34
    dr.rounded_rectangle([(960-bw)/2,204,(960+bw)/2,238],radius=17,fill=PAPER,outline=BORDER,width=1)
    dr.text(((960-dr.textlength(bug,font=bf))/2,213),bug,font=bf,fill=TEXT)
    dr.line([8,262,952,262],fill=TEXT,width=2); dr.line([8,267,952,267],fill=TEXT,width=1)
    # ticker
    dr.line([0,300,960,300],fill=TEXT,width=1)
    dr.text((12,278),'IN THIS EDITION',font=F(SANS_B,11),fill=GOLD)
    tf2=F(SANS_B,14); x=140; ty=276
    for it in items:
        dr.text((x,ty),it,font=tf2,fill=TEXT); x+=dr.textlength(it,font=tf2)+8
        dr.text((x,ty),'•',font=tf2,fill=GOLD); x+=22
        if x>900: break
    dr.line([0,302,960,302],fill=BORDER,width=1)
    # the lead
    dr.text((16,318),'THE LEAD',font=F(SANS,13),fill=MUTED)
    hf=F(SERIF_B,35)
    y=342
    for ln in wrap(dr, headline, hf, 928)[:3]:
        dr.text((16,y),ln,font=hf,fill=TEXT); y+=44
    # outlook panel
    py=y+14
    dr.line([8,py,952,py],fill=TEXT,width=2); dr.line([8,py+3,952,py+3],fill=TEXT,width=1)
    dr.text((10,py+12),'THE OUTLOOK — FIVE DAYS',font=F(SERIF_B,15),fill=TEXT)
    sf=F(SANS,11); dr.text((950-dr.textlength(src_line,font=sf),py+14),src_line,font=sf,fill=MUTED)
    colw=944/5
    for k,(name,cond,nums,pop) in enumerate(days):
        cx=8+colw*k+colw/2
        if k: dr.line([8+colw*k,py+44,8+colw*k,py+168],fill=BORDER,width=1)
        nf=F(SANS_B,13); dr.text((cx-dr.textlength(name.upper(),font=nf)/2,py+46),name.upper(),font=nf,fill=TEXT)
        kind='sun' if 'Sunny' in cond and 'Mostly' not in cond and 'Partly' not in cond else ('partly' if ('Mostly' in cond or 'Partly' in cond) else ('rain' if 'Rain' in cond or 'Shower' in cond else 'cloud'))
        icon(dr,kind,cx,py+84)
        cf=F(SERIF,12)
        for li,cln in enumerate(wrap(dr,cond,cf,150)[:2]):
            dr.text((cx-dr.textlength(cln,font=cf)/2,py+104+li*15),cln,font=cf,fill=TEXT)
        if len(nums)>=2:
            tt=f"{nums[0]} / {nums[1]}"
            ttf=F(SERIF,17); dr.text((cx-dr.textlength(tt,font=ttf)/2,py+136),tt,font=ttf,fill=TEXT)
        pf=F(SANS,11); pl=pop if pop else ''
        if pl: dr.text((cx-dr.textlength(pl,font=pf)/2,py+162),pl,font=pf,fill=BLUE if 'Precip' in pl else MUTED)
    dr.line([8,py+176,952,py+176],fill=BORDER,width=1)
    img.resize((480,360), Image.LANCZOS).save(out, quality=88)
    print('wrote', out)

if __name__=='__main__': main(sys.argv[1], sys.argv[2])
