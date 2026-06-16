import json, re, os
APP = os.path.expanduser('~/guanyu-vn')
src = open(os.path.join(APP,'scenes.js'), encoding='utf-8').read()
scenes = json.loads(re.search(r'SCENES = (\{.*\})\s*;', src, re.S).group(1))
names = {}
for a, bs in scenes.items():
    for b in bs:
        if b.get('t') == 'say':
            names[b['name']] = names.get(b['name'], 0) + 1
print('全say話者:', dict(sorted(names.items(), key=lambda x: -x[1])))
html = open(os.path.join(APP,'index.html'), encoding='utf-8').read()
meta = re.search(r'const CHARMETA = \{(.*?)\};', html, re.S).group(1)
defined = set(re.findall(r"'([^']+)':\{c:", meta))
n2c = re.search(r'const NAME2CHAR=\{(.*?)\};', html, re.S).group(1)
n2cnames = set(re.findall(r"'([^']+)':'", n2c))
print('CHARMETA定義済:', defined)
print('CHARMETA未定義(デフォルト茶):', set(names) - defined)
print('NAME2CHAR(スポット用):', n2cnames)
