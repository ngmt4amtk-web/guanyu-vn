#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageEnhance

APP = os.path.expanduser('~/guanyu-vn')
SPR = os.path.join(APP, 'assets/sprites')
BG  = os.path.join(APP, 'assets/bg')
TOOLS = os.path.join(APP, '_tools')
os.makedirs(TOOLS, exist_ok=True)

def cover(im, W, H):
    w, h = im.size
    s = max(W / w, H / h)
    im2 = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    x = (im2.size[0] - W) // 2; y = (im2.size[1] - H) // 2
    return im2.crop((x, y, x + W, y + H))

# --- 1) keying品質プレビュー: 主要立ち絵を実戦場bgに乗せる ---
bg = Image.open(os.path.join(BG, 'bg_hakuba_senjo_hiru.jpg')).convert('RGB')
print('bg_hakuba size', bg.size)
canvasW, canvasH = 1024, 1536
base = cover(bg, canvasW, canvasH)
names = ['guanyu_base', 'guanyu_armor', 'guanyu_late', 'caocao_base', 'liubei_base', 'yanliang_base']
strip_w = 360
strip = Image.new('RGB', (strip_w * len(names), 760), (40, 44, 40))
for i, nm in enumerate(names):
    sp = Image.open(os.path.join(SPR, nm + '.png')).convert('RGBA')
    w, h = sp.size
    th = 740; tw = round(w * th / h)
    sp = sp.resize((tw, th), Image.LANCZOS)
    cell = Image.new('RGBA', (strip_w, 760), (40, 44, 40, 255))
    cell.alpha_composite(sp, ((strip_w - tw) // 2, 760 - th))
    strip.paste(cell.convert('RGB'), (i * strip_w, 0))
strip.save(os.path.join(TOOLS, 'preview_sprites_on_gray.jpg'), 'JPEG', quality=88)
print('wrote preview_sprites_on_gray.jpg')

# --- 2) title_kv 合成: 関羽(armor) を白馬戦場に立たせる ---
title = cover(Image.open(os.path.join(BG, 'bg_hakuba_senjo_hiru.jpg')).convert('RGB'), canvasW, canvasH)
title = ImageEnhance.Brightness(title).enhance(0.62)
title = ImageEnhance.Color(title).enhance(0.85)
hero = Image.open(os.path.join(SPR, 'guanyu_armor.png')).convert('RGBA')
w, h = hero.size
hh = 1300; hw = round(w * hh / h)
hero = hero.resize((hw, hh), Image.LANCZOS)
tcanvas = title.convert('RGBA')
# 下端から少し上げて足元を地面に
tcanvas.alpha_composite(hero, ((canvasW - hw) // 2, canvasH - hh - 30))
# 上部を更に暗くしてロゴ可読性(縦グラデ)
grad = Image.new('L', (1, canvasH), 0)
for y in range(canvasH):
    # 上40%を暗く、下も少し暗く
    top = max(0, int(150 * (1 - y / (canvasH * 0.45)))) if y < canvasH * 0.45 else 0
    bot = max(0, int(120 * ((y - canvasH * 0.7) / (canvasH * 0.3)))) if y > canvasH * 0.7 else 0
    grad.putpixel((0, y), min(200, top + bot))
grad = grad.resize((canvasW, canvasH))
dark = Image.new('RGBA', (canvasW, canvasH), (6, 8, 6, 0))
dark.putalpha(grad)
tcanvas.alpha_composite(dark)
out = tcanvas.convert('RGB')
out.save(os.path.join(APP, 'assets/title_kv.jpg'), 'JPEG', quality=90)
print('wrote assets/title_kv.jpg', out.size)
