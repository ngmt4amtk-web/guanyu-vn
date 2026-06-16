# 關羽 ─ 漢寿亭侯伝

正史『三国志』蜀書六 關羽傳（本文＋裴松之注）に基づく、一本道ノベルゲーム。**演義不使用**。

- 視点＝関羽一人称（規律ある武人の独白）。死の瞬間だけ三人称史官へ二段ハンドオフ。
- 本作のエンジン＝「傲＝序列で背後の観測を省略する癖」と「臨沮の死」が同じ認知機構から出る、という劇的アイロニー。
- 全13幕。選択肢なし。立ち絵15・背景16・CG5（焚天メソッドv1.1の系譜）。
- 縦画面・モバイル前提。AUTO / SKIP / LOG / 文字速度・ウインドウ非表示に対応。

## 構成
```
index.html        単一ファイルのVNエンジン（FGO風・縦画面）
scenes.js         全13幕の本文ビート（window.SCENES / SCENE_ORDER）
assets/bg/        背景 *.jpg
assets/sprites/   立ち絵 *.png（緑#00B140クロマキー透過済）
assets/cg/        見せ場CG *.jpg
assets/title_kv.jpg  タイトル背景（関羽×白馬戦場の合成）
_tools/           ビルド・検証スクリプト（クロマキー / scenes整合 / CDP実機検証）
```

## ビルド再現
```
python3 _tools/chroma_key.py        # 緑ベタ立ち絵 → 透過PNG（純PIL・despill込み）
python3 _tools/build_scenes.py      # scenes整合＋全アセット参照検証 → scenes.js
python3 _tools/preview_and_title.py # title_kv合成
node    _tools/cdp_shots.mjs         # Chrome実駆動で全場面スクショ（要 http.server :8123）
```

## 出典・考証
底本＝陳寿『三国志』蜀書六 關羽傳。排除した演義要素：桃園結義／五虎大将／温酒斬華雄／三英戦呂布／土山約三事／過五関斬六将・千里走単騎／単刀赴会／華容道／赤兎拝領・青龍偃月刀／華佗執刀・刮骨の囲碁／文醜斬殺の手柄化／能動的水攻め／虎女犬子／玉泉山顕聖・周倉。
脚色設計の詳細は `2026-06-16_正史関羽_脚色設計書.md`（Claude Code成果物）。
