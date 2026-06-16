#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""再生成workflowの出力JSON(acts[].beats + consistency.fixes)から scenes.js を組み立てる。
使い方: python3 build_scenes_v2.py <result.json>
  - 整合fix(find/replace)を各幕のnarrate/sayテキストに適用(完全一致1回・外れたら警告のみ)
  - 全bg/sprite/cg参照を assets 実体と照合(欠落は致命=書き出さない)
  - scenes.js を act毎1行で書き出し、旧版を scenes_v1_backup.js に退避
"""
import json, re, os, sys

APP = os.path.expanduser('~/guanyu-vn')
OUT = os.path.join(APP, 'scenes.js')
ORDER = ['act01','act02','act03','act04','act05','act06','act07','act08','act09','act10','act11','act12','act13']
MOODS = {'warm','cool','night','dawn','dusk','storm','default'}

def load_result(path):
    raw = open(path, encoding='utf-8').read()
    i = raw.find('{')
    d = json.loads(raw[i:])
    # task出力ラッパ対応
    for k in ('result',):
        if 'acts' not in d and k in d:
            d = d[k]
    if isinstance(d, str):
        d = json.loads(d)
    return d

def main():
    res = load_result(sys.argv[1])
    acts = {a['act']: a for a in res['acts']}
    fixes = (res.get('consistency') or {}).get('fixes', [])

    # 整合fix適用
    applied = 0; missed = []
    for fx in fixes:
        act = fx['act']; find = fx.get('find_ja',''); rep = fx.get('replace_ja','')
        if act not in acts or not find: continue
        hit = 0
        for b in acts[act]['beats']:
            if b.get('t') in ('narrate','say') and b.get('text') and find in b['text']:
                b['text'] = b['text'].replace(find, rep); hit += 1
        if hit: applied += hit
        else: missed.append((act, find[:30]))
    print(f'整合fix: 適用{applied} 未命中{len(missed)}')
    for m in missed: print('  miss:', m)

    # 検証
    bg_dir=os.path.join(APP,'assets/bg'); sp_dir=os.path.join(APP,'assets/sprites'); cg_dir=os.path.join(APP,'assets/cg')
    have_bg={f[:-4] for f in os.listdir(bg_dir) if f.endswith('.jpg')}
    have_sp={f[:-4] for f in os.listdir(sp_dir) if f.endswith('.png')}
    have_cg={f[:-4] for f in os.listdir(cg_dir) if f.endswith('.jpg')}
    errors=[]; used_bg=set(); used_sp=set(); used_cg=set(); beat_counts={}
    scenes={}
    for act in ORDER:
        if act not in acts: errors.append(f'{act} 欠落(workflow未生成)'); continue
        beats=[]
        textbeats=0
        for b in acts[act]['beats']:
            t=b.get('t')
            if t=='bg':
                if not b.get('bg'): errors.append(f'{act}: bgキー無し'); continue
                used_bg.add(b['bg'])
                if b['bg'] not in have_bg: errors.append(f'{act}: 背景欠落 {b["bg"]}')
                mood=b.get('mood','default');
                if mood not in MOODS: mood='default'
                beats.append({'t':'bg','bg':b['bg'],'mood':mood})
            elif t=='sprite':
                if not b.get('key'): errors.append(f'{act}: spriteキー無し'); continue
                used_sp.add(b['key'])
                if b['key'] not in have_sp: errors.append(f'{act}: 立ち絵欠落 {b["key"]}')
                beats.append({'t':'sprite','key':b['key']})
            elif t=='cg':
                if not b.get('cg'): errors.append(f'{act}: cgキー無し'); continue
                used_cg.add(b['cg'])
                if b['cg'] not in have_cg: errors.append(f'{act}: CG欠落 {b["cg"]}')
                beats.append({'t':'cg','cg':b['cg']})
            elif t=='narrate':
                if not b.get('text'): continue
                beats.append({'t':'narrate','text':b['text']}); textbeats+=1
            elif t=='say':
                if not b.get('text'): continue
                beats.append({'t':'say','name':b.get('name',''),'text':b['text']}); textbeats+=1
        scenes[act]=beats; beat_counts[act]=textbeats

    print('=== 参照検証 ===')
    if errors:
        print('NG:'); [print('  -',e) for e in errors]
        raise SystemExit('検証失敗: 欠落あり。書き出さない。')
    print('OK: 全参照が実在素材に解決')
    print(f'  使用 背景{len(used_bg)}/{len(have_bg)}  立ち絵{len(used_sp)}/{len(have_sp)}  CG{len(used_cg)}/{len(have_cg)}')
    print('  未使用 背景:', sorted(have_bg-used_bg), '立ち絵:', sorted(have_sp-used_sp), 'CG:', sorted(have_cg-used_cg))
    print('  各幕テキストビート:', {a:beat_counts[a] for a in ORDER})
    print(f'  総テキストビート: {sum(beat_counts.values())} (旧版158)')

    # 旧版退避
    if os.path.exists(OUT):
        import shutil; shutil.copy(OUT, os.path.join(APP,'scenes_v1_backup.js'))
    lines=['window.SCENE_ORDER = '+json.dumps(ORDER,ensure_ascii=False)+';','window.SCENES = {']
    for i,act in enumerate(ORDER):
        comma=',' if i<len(ORDER)-1 else ''
        lines.append(f'{json.dumps(act,ensure_ascii=False)}: '+json.dumps(scenes[act],ensure_ascii=False)+comma)
    lines.append('};')
    open(OUT,'w',encoding='utf-8').write('\n'.join(lines)+'\n')
    print('wrote',OUT,os.path.getsize(OUT)//1024,'KB')

if __name__=='__main__':
    main()
