#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scenes_draft.js を実在素材に整合させて scenes.js を再生成し、全アセット参照を検証する。
変更:
  act05: 幻CG cg_guanyu_leaves_xudu_dawn を削除 → 帰参の道(bg_road_kisan_yugure)へ場面転換に置換
  act07: 幻CG cg_act07_guanyu_reads_letter を削除（荊州陣のまま地の文継続）
  act09: 幻CG cg_guanyu_setsuetsu_jufu を削除（樊前陣のまま地の文継続）
  act10: 既存だが未使用だった cg_pangde_zan(龐徳斬) を「斬れ。」直後に投入
"""
import json, re, os

APP = os.path.expanduser('~/guanyu-vn')
DRAFT = os.path.expanduser('~/Shortcuts/Claude Code成果物/2026-06-16_関羽_scenes_draft.js')
OUT = os.path.join(APP, 'scenes.js')

src = open(DRAFT, encoding='utf-8').read()
order = json.loads(re.search(r'window\.SCENE_ORDER\s*=\s*(\[.*?\]);', src, re.S).group(1))
scenes = json.loads(re.search(r'window\.SCENES\s*=\s*(\{.*\})\s*;?\s*$', src, re.S).group(1))

# --- act05: 幻CG → 帰参の道へ場面転換 ---
new = []
for s in scenes['act05']:
    if s.get('t') == 'cg' and s.get('cg') == 'cg_guanyu_leaves_xudu_dawn':
        new.append({'t': 'bg', 'bg': 'bg_road_kisan_yugure', 'mood': 'dusk'})
        new.append({'t': 'sprite', 'key': 'guanyu_base'})
    else:
        new.append(s)
scenes['act05'] = new

# --- act07 / act09: 幻CG削除 ---
def drop_cg(act, cg):
    scenes[act] = [s for s in scenes[act] if not (s.get('t') == 'cg' and s.get('cg') == cg)]
drop_cg('act07', 'cg_act07_guanyu_reads_letter')
drop_cg('act09', 'cg_guanyu_setsuetsu_jufu')

# --- act10: 龐徳斬CGを「斬れ。」直後に投入 ---
new = []
for s in scenes['act10']:
    new.append(s)
    if s.get('t') == 'say' and s.get('name') == '関羽' and s.get('text', '').strip() == '斬れ。':
        new.append({'t': 'cg', 'cg': 'cg_pangde_zan'})
scenes['act10'] = new

# ================= 検証: 全アセット参照が実在するか =================
bg_dir = os.path.join(APP, 'assets/bg'); sp_dir = os.path.join(APP, 'assets/sprites'); cg_dir = os.path.join(APP, 'assets/cg')
have_bg = {f[:-4] for f in os.listdir(bg_dir) if f.endswith('.jpg')}
have_sp = {f[:-4] for f in os.listdir(sp_dir) if f.endswith('.png')}
have_cg = {f[:-4] for f in os.listdir(cg_dir) if f.endswith('.jpg')}
used_bg, used_sp, used_cg = set(), set(), set()
errors = []
for act in order:
    if act not in scenes:
        errors.append(f'SCENE_ORDER {act} が SCENES に無い'); continue
    for s in scenes[act]:
        t = s.get('t')
        if t == 'bg':
            used_bg.add(s['bg'])
            if s['bg'] not in have_bg: errors.append(f'{act}: 背景欠落 {s["bg"]}')
        elif t == 'sprite':
            used_sp.add(s['key'])
            if s['key'] not in have_sp: errors.append(f'{act}: 立ち絵欠落 {s["key"]}')
        elif t == 'cg':
            used_cg.add(s['cg'])
            if s['cg'] not in have_cg: errors.append(f'{act}: CG欠落 {s["cg"]}')

print('=== 参照検証 ===')
if errors:
    print('NG:'); [print('  -', e) for e in errors]
    raise SystemExit('検証失敗: 欠落参照あり。scenes.jsは書き出さない。')
print('OK: 全参照が実在素材に解決')
print(f'  使用 背景{len(used_bg)}/{len(have_bg)}  立ち絵{len(used_sp)}/{len(have_sp)}  CG{len(used_cg)}/{len(have_cg)}')
print('  未使用 背景:', sorted(have_bg - used_bg))
print('  未使用 立ち絵:', sorted(have_sp - used_sp))
print('  未使用 CG:', sorted(have_cg - used_cg))

# ================= 書き出し（act毎1行・diff容易） =================
lines = ['window.SCENE_ORDER = ' + json.dumps(order, ensure_ascii=False) + ';', 'window.SCENES = {']
for i, act in enumerate(order):
    comma = ',' if i < len(order) - 1 else ''
    lines.append(f'{json.dumps(act, ensure_ascii=False)}: ' + json.dumps(scenes[act], ensure_ascii=False) + comma)
lines.append('};')
open(OUT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')

# ビート数
total_say = sum(1 for a in order for s in scenes[a] if s.get('t') in ('say', 'narrate'))
print(f'  全{len(order)}幕 / 台詞・地の文 計{total_say}ビート')
