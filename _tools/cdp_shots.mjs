// Chrome を CDP で実駆動して各場面を撮る。node22 内蔵 WebSocket 使用。
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const URL = 'http://localhost:8123/index.html';
const OUT = '/Users/ngmt.mtk/guanyu-vn/_tools/shots';
const PORT = 9223;
mkdirSync(OUT, { recursive: true });

const prof = '/tmp/guanyu_cdp_profile';
const chrome = spawn(CHROME, [
  '--headless=new', `--remote-debugging-port=${PORT}`, `--user-data-dir=${prof}`,
  '--no-first-run', '--no-default-browser-check', '--hide-scrollbars',
  '--force-device-scale-factor=2', '--window-size=412,915',
], { stdio: 'ignore' });

async function getWs() {
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch(`http://localhost:${PORT}/json/version`);
      const j = await r.json();
      if (j.webSocketDebuggerUrl) return j.webSocketDebuggerUrl;
    } catch {}
    await sleep(250);
  }
  throw new Error('CDP起動せず');
}

const wsUrl = await getWs();
const ws = new WebSocket(wsUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

let _id = 0; const pending = new Map(); const events = [];
ws.onmessage = (m) => {
  const d = JSON.parse(m.data);
  if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); }
  else if (d.method) events.push(d);
};
function cmd(method, params = {}, sessionId) {
  const id = ++_id;
  return new Promise((res) => { pending.set(id, res); ws.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) })); });
}

// ターゲット(ページ)にアタッチ
const { result: targets } = await cmd('Target.getTargets');
const page = targets.targetInfos.find(t => t.type === 'page');
const { result: { sessionId } } = await cmd('Target.attachToTarget', { targetId: page.targetId, flatten: true });
const S = (m, p) => cmd(m, p, sessionId);

await S('Page.enable'); await S('Runtime.enable'); await S('Log.enable');
const jsErrors = [];
ws.addEventListener('message', (m) => {
  const d = JSON.parse(m.data);
  if (d.method === 'Runtime.exceptionThrown') jsErrors.push(d.params.exceptionDetails?.text + ' ' + (d.params.exceptionDetails?.exception?.description || ''));
  if (d.method === 'Log.entryAdded' && d.params.entry.level === 'error') jsErrors.push('LOG ' + d.params.entry.text);
});

async function nav() {
  await S('Page.navigate', { url: URL });
  await sleep(2500); // 読み込み+プリロード
}
async function evalJs(expr) { const r = await S('Runtime.evaluate', { expression: expr, awaitPromise: true }); if (r.result?.exceptionDetails) jsErrors.push(JSON.stringify(r.result.exceptionDetails)); return r.result?.result?.value; }
async function shot(name) {
  const r = await S('Page.captureScreenshot', { format: 'png' });
  writeFileSync(`${OUT}/${name}.png`, Buffer.from(r.result.data, 'base64'));
  console.log('shot', name);
}

// in-page シーク用ヘルパ
const HELPER = `window.__seek=function(act,n){ start(); go(act); for(var i=0;i<n;i++){ advance(); } return nodeId+':'+idx; };`;

await nav();
await shot('00_title');                  // タイトル(title_kv)

await evalJs(HELPER);
await evalJs('start();'); await sleep(600); await shot('01_act01_open');           // 開幕(夜山道+関羽)

await evalJs("__seek('act04', 9);"); await sleep(900); await shot('02_act04_battle'); // 白馬・顔良CG
await evalJs("__seek('act05', 6);"); await sleep(900); await shot('03_act05_dialog'); // 関羽×張遼 対話
await evalJs("__seek('act08', 8);"); await sleep(900); await shot('04_act08_cg');      // 刮骨CG
await evalJs("__seek('act10', 20);"); await sleep(900); await shot('05_act10_climax'); // 威震華夏CG
await evalJs("__seek('act11', 6);"); await sleep(900); await shot('06_act11_sunquan'); // 孫権使者(立ち絵)
await evalJs("__seek('act13', 12);"); await sleep(900); await shot('07_act13_death');   // 臨沮CG
await evalJs("__seek('act13', 30);"); await sleep(900); await shot('08_act13_epilogue');// 後日譚(史官bg)

console.log('JS errors:', jsErrors.length ? jsErrors : 'なし');
ws.close(); chrome.kill();
await sleep(300);
