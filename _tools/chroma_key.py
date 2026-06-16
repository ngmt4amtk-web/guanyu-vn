#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""緑ベタ #00B140 立ち絵 → 透過PNG。純PIL(ImageChops)。
キー信号 = G - max(R,B)（緑優勢度）。被写体(藍袍/黒袍/肌/鎧)は緑優勢にならないので安全。
despill = G を min(G,max(R,B)) にクランプして緑フリンジ除去。"""
import os, glob
from PIL import Image, ImageChops

SRC = os.path.expanduser('~/guanyu-vn/assets/sprites_raw')
DST = os.path.expanduser('~/guanyu-vn/assets/sprites')
os.makedirs(DST, exist_ok=True)

LOW, HIGH = 20, 90      # greenness<=LOW:不透明 / >=HIGH:透明 / 間は線形
OUT_H = 1200            # 出力高さ(web最適化・retina相当)
BBOX_ALPHA = 12         # bbox判定のalpha閾(微フリンジ無視)

def alpha_lut(g):
    if g <= LOW:  return 255
    if g >= HIGH: return 0
    return int(round(255 * (HIGH - g) / (HIGH - LOW)))
LUT = [alpha_lut(i) for i in range(256)]

def key_one(path):
    im = Image.open(path).convert('RGB')
    R, G, B = im.split()
    maxRB = ImageChops.lighter(R, B)             # max(R,B)
    greenness = ImageChops.subtract(G, maxRB)    # max(0, G-max(R,B))
    alpha = greenness.point(LUT)                 # 緑優勢→透明
    newG = ImageChops.darker(G, maxRB)           # despill: min(G,max(R,B))
    out = Image.merge('RGBA', (R, newG, B, alpha))
    # bbox crop（足元を画面下端に合わせるため透明余白を除去）
    mask = alpha.point(lambda a: 255 if a > BBOX_ALPHA else 0)
    bb = mask.getbbox()
    if bb:
        out = out.crop(bb)
    # 高さ正規化
    w, h = out.size
    if h > OUT_H:
        out = out.resize((max(1, round(w * OUT_H / h)), OUT_H), Image.LANCZOS)
    return out, bb, im.size

if __name__ == '__main__':
    files = sorted(glob.glob(os.path.join(SRC, '*.png')))
    print(f'{len(files)} sprites')
    for f in files:
        name = os.path.basename(f)
        out, bb, orig = key_one(f)
        outp = os.path.join(DST, name)
        out.save(outp, 'PNG', optimize=True)
        sz = os.path.getsize(outp) // 1024
        # 透明率(全消し/全残り検知用)
        a = out.split()[3]
        hist = a.histogram()
        opaque = sum(hist[200:]) ; transp = sum(hist[:20]) ; total = out.size[0]*out.size[1]
        print(f'{name:20s} orig{orig} bbox{bb} -> {out.size} {sz}KB  opaque={opaque*100//total}% transp={transp*100//total}%')
    print('done ->', DST)
