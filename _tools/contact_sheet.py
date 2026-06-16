#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全立ち絵(透過)を市松+暗背景に並べたコンタクトシートと、全CGの一覧を出力。keying全数の目視確認用。"""
import os, glob
from PIL import Image

APP = os.path.expanduser('~/guanyu-vn')
SPR = os.path.join(APP, 'assets/sprites'); CG = os.path.join(APP, 'assets/cg'); OUT = os.path.join(APP, '_tools')

def checker(w, h, s=24):
    im = Image.new('RGB', (w, h), (70, 74, 70))
    d = Image.new('RGB', (s, s), (52, 56, 52))
    for y in range(0, h, s):
        for x in range(0, w, s):
            if ((x // s) + (y // s)) % 2 == 0:
                im.paste(d, (x, y))
    return im

# 立ち絵コンタクト
files = sorted(glob.glob(os.path.join(SPR, '*.png')))
cw, ch, cols = 300, 430, 5
rows = (len(files) + cols - 1) // cols
sheet = checker(cw * cols, ch * rows)
from PIL import ImageDraw
dr = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    sp = Image.open(f).convert('RGBA'); w, h = sp.size
    th = ch - 34; tw = round(w * th / h)
    if tw > cw - 10:
        tw = cw - 10; th = round(h * tw / w)
    sp = sp.resize((tw, th), Image.LANCZOS)
    cx, cy = (i % cols) * cw, (i // cols) * ch
    sheet.paste(sp, (cx + (cw - tw) // 2, cy + ch - th - 4), sp)
    dr.text((cx + 6, cy + 6), os.path.basename(f)[:-4], fill=(255, 230, 150))
sheet.save(os.path.join(OUT, 'contact_sprites.jpg'), 'JPEG', quality=86)
print('contact_sprites.jpg', len(files), 'sprites')

# CGコンタクト
cgs = sorted(glob.glob(os.path.join(CG, '*.jpg')))
gw = 360; gh = 540
gsheet = Image.new('RGB', (gw * len(cgs), gh), (10, 10, 10))
gd = ImageDraw.Draw(gsheet)
for i, f in enumerate(cgs):
    im = Image.open(f).convert('RGB'); w, h = im.size
    s = min(gw / w, (gh - 22) / h); im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    gsheet.paste(im, (i * gw + (gw - im.size[0]) // 2, 22))
    gd.text((i * gw + 6, 4), os.path.basename(f)[:-4], fill=(255, 230, 150))
gsheet.save(os.path.join(OUT, 'contact_cg.jpg'), 'JPEG', quality=86)
print('contact_cg.jpg', len(cgs), 'CGs')
