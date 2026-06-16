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

# ================= QA敵対的監査のmust-fix反映(正史/声/POV) =================
# 各置換は現テキストと完全一致で「ちょうど1回」命中することを assert（無言の no-op を防ぐ）
def replace_text(act, old, new):
    hit = 0
    for s in scenes[act]:
        if s.get('t') in ('say', 'narrate') and s.get('text') == old:
            s['text'] = new; hit += 1
    assert hit == 1, f'QA-fix未命中/重複 {act}: hit={hit}\n  old={old!r}'

# 1. act11: 全知視点逸脱(司馬懿/蔣濟/孫権内面)を関羽のPOV内・観測省略へ。孫権立ち絵も除去(関羽は孫権を見ていない)
before = len(scenes['act11'])
scenes['act11'] = [s for s in scenes['act11'] if not (s.get('t') == 'sprite' and s.get('key') == 'sunquan_base')]
assert len(scenes['act11']) == before - 1, 'act11 sunquan立ち絵除去に失敗'
replace_text('act11',
    '——その頃、北では別の算盤が弾かれていた。司馬懿と蔣濟が魏王に説く。孫権を後ろから動かせば、樊の囲みは戦わずして自ら解ける、と。江東の主は、使者の口が持ち帰った一語をまだ呑み下していない。',
    '使者の馬は北へ消えた。その蹄がどこへ何を運ぶのかを、樊城という前の的しか数えていない私の目は、追わなかった。')

# 2. act08: 設計書が逐語で禁じた対句+一拍キメ→身体知覚の密度へ
replace_text('act08',
    '痛みは確かに来る。だが私は肉を割き、酒を口へ運ぶ手を止めない。痛みは止めず、手も止めぬ。手が上だ。',
    '痛みは確かに来る。だが盤の肉に箸を伸ばすたび、刃が骨を擦って左の指先が一度跳ねても、箸を持つ右は卓の縁を離れない。')

# 3. act03: 演義残響(保護二嫂/土山約三事)を削り、忠=劉備本人の所在の一点へ
replace_text('act03',
    '先主の妻子はどこだ。先に通せ。',
    '先主は北の袁紹のもとへ奔った。生きているなら、向かう先はそこだ。')

# 4. act04→05: 正史『顔良斬殺=報恩完了→去る』に整合(未来形・未完を完了相へ)
replace_text('act05',
    '私は終には留まらぬ。必ず功を立てて曹公に報いてから去る。',
    '私は終には留まらぬ。曹公への報いは、顔良を斬って済んだ。あとは去るだけだ。')
replace_text('act05',
    '報いるべき功が一つ、まだこの手に残っている。それだけのことだ。',
    '報いるべき効はもう果たした。それだけのことだ。')

# 5. act09: 糜芳=江陵/士仁=公安 と任地を分離(正史・act12と整合)
replace_text('act09',
    '江陵は私の名で守られている。城壁は高く、糜芳・士仁が留守を預かる。東の孫権の境まで、間に置いた者の数を、私はそこで数えなかった。',
    '江陵は私の名で守られている。城壁は高く、糜芳が江陵を、士仁が公安を預かる。東の孫権の境まで、間に置いた者の数を、私はそこで数えなかった。')

# 6. act02: 〈受ける→ゆえに動く〉短文キメの3回反復を1つ解いて声の純度を上げる(nice-to-have)
replace_text('act02',
    '後に劉備が平原の相となり、私と張飛を別部司馬とした。兵を分けて率いる役だ。受けた、ゆえに動く。それだけを決めた。',
    '後に劉備が平原の相となり、私と張飛を別部司馬とした。兵を分けて率いる役を、私は黙って受けた。')

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
