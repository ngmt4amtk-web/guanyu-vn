#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ユーザー指摘v3: act02の従う理由を深める/act03冒頭を全体→自陣営→自分の順に整序/厚遇と盡封の具体(正史準拠)を追加。
各操作は完全一致1回をassert。"""
import json, re, os, shutil
APP = os.path.expanduser('~/guanyu-vn'); P = os.path.join(APP, 'scenes.js')
src = open(P, encoding='utf-8').read()
order = json.loads(re.search(r'SCENE_ORDER = (\[.*?\]);', src, re.S).group(1))
scenes = json.loads(re.search(r'SCENES = (\{.*\})\s*;', src, re.S).group(1))

def idx_of(act, pred):
    hits = [i for i, b in enumerate(scenes[act]) if pred(b)]
    assert len(hits) == 1, f'{act}: 一致 {len(hits)} != 1'
    return hits[0]

def repl(act, t, old, new, name=None):
    i = idx_of(act, lambda b: b.get('t')==t and b.get('text')==old and (name is None or b.get('name')==name))
    scenes[act][i]['text'] = new

def insert_after(act, t, anchor, beat, name=None):
    i = idx_of(act, lambda b: b.get('t')==t and b.get('text')==anchor and (name is None or b.get('name')==name))
    scenes[act].insert(i+1, beat)

# ---- act02: 従う理由を深める（劉備の志/器を見込む＝桃園でなく個人の決意） ----
repl('act02','say',
  'よく来てくれた。今は名も官もない身だが、この乱を鎮めようと人を募っている。おぬしの力を、私に貸してはくれぬか。',
  'よく来てくれた。私は名も官もない流れ者だが、この乱に泣く民を、どうしても見過ごせぬのだ。傾いた漢室を支え、この世の筋を通す――いまはその志ひとつで生きている。', name='劉備')
repl('act02','say',
  '見ず知らずの私に、そこまで言われるか。……よろしい。この身、あなたの戦に役立てよう。',
  '……武だけを頼りに生きてきた私が、その言葉に胸を衝かれるとはな。大言を吐く者は多いが、本気でそれを背負える器は、めったにおらぬ。', name='関羽')
insert_after('act02','say',
  '……武だけを頼りに生きてきた私が、その言葉に胸を衝かれるとはな。大言を吐く者は多いが、本気でそれを背負える器は、めったにおらぬ。',
  {'t':'say','name':'関羽','text':'見込んだ。この関羽の武、ことごとくあなたに預けよう。今日より、我が主はあなた一人だ。'}, name='関羽')

# ---- act03: 冒頭を 全体→自陣営→自分 のズームインに ----
repl('act03','narrate',
  '建安五年、西暦二〇〇年の正月。後漢の天下は群雄が各地に割拠し、徐州の要衝である下邳城は、劉備配下の関羽が留守を預かっていた。',
  '建安五年、西暦二〇〇年の正月。後漢の天下は群雄が各地に割拠していた。')
insert_after('act03','narrate',
  '徐州を得た劉備は、その中心をなす下邳城の守りを関羽に委ね、太守(郡の長官)の職務を代行させた。これを行太守事という。',
  {'t':'narrate','text':'そして徐州の要衝である下邳城は、劉備配下の関羽が留守を預かっていた。'})

# ---- act03: 厚遇を具体に（正史準拠の金帛馬・重加賞賜） ----
repl('act03','narrate',
  ' 曹公はさらに、たびたびの賞賜を重ねて関羽を厚くもてなした。その陣には、もと呂布に仕え今は曹公配下にある張遼(字は文遠)もいて、関羽とは旧知の間柄であった。'.strip(),
  '曹公はさらに、金や絹をはじめ数えきれぬほどの賜り物を積み、馬まで与えて、賞賜を幾度も重ねた。その陣には、もと呂布に仕え今は曹公配下にある張遼(字は文遠)もいて、関羽とは旧知の間柄であった。')

# ---- act05: 去る時の盡封を具体に（賜った金も絹も一つ残らず封じて返す） ----
repl('act05','narrate',
  '関羽は、曹操から与えられた物をことごとく封をして手をつけず、書を一通残して別れを告げた。',
  '関羽は、曹操から賜った金も絹も、賜り物のことごとくを封をして元のまま積み、ひとつも手をつけなかった。そして書を一通残し、別れを告げた。')

# ---- act03: 偏将軍の序列の誤りを訂正（雑号より上→実は基層格。厚遇は"捕虜を将軍に列す"異例さ） ----
repl('act03','narrate',
  '曹公は関羽を偏将軍に任じた。偏将軍は雑号の将軍より上の正規の将軍位であり、降ったばかりの捕虜に与えるには破格の処遇だった。',
  '曹公は関羽を偏将軍に任じた。偏将軍は将軍位としては下のほうの位だが、降ったばかりの捕虜をいきなり将軍に列すること自体が異例で、曹公がどれほど関羽を惜しんだかがうかがえた。')

# ---- 検証 ----
bg=set(f[:-4] for f in os.listdir(os.path.join(APP,'assets/bg')) if f.endswith('.jpg'))
sp=set(f[:-4] for f in os.listdir(os.path.join(APP,'assets/sprites')) if f.endswith('.png'))
cg=set(f[:-4] for f in os.listdir(os.path.join(APP,'assets/cg')) if f.endswith('.jpg'))
err=[]
for a in order:
    for b in scenes[a]:
        if b.get('t')=='bg' and b['bg'] not in bg: err.append(a+' bg '+b['bg'])
        if b.get('t')=='sprite' and b['key'] not in sp: err.append(a+' sp '+b['key'])
        if b.get('t')=='cg' and b['cg'] not in cg: err.append(a+' cg '+b['cg'])
assert not err, err
shutil.copy(P, os.path.join(APP,'scenes_prev.js'))
lines=['window.SCENE_ORDER = '+json.dumps(order,ensure_ascii=False)+';','window.SCENES = {']
for i,a in enumerate(order):
    lines.append(json.dumps(a,ensure_ascii=False)+': '+json.dumps(scenes[a],ensure_ascii=False)+(',' if i<len(order)-1 else ''))
lines.append('};')
open(P,'w',encoding='utf-8').write('\n'.join(lines)+'\n')
print('patch_v3 適用OK')
print('act02 say:', sum(1 for b in scenes['act02'] if b['t']=='say'),'/ act03 beats:', len(scenes['act03']))
