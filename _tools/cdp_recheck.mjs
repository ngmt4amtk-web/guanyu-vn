import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';
const CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const URL='http://localhost:8123/index.html'; const OUT='/Users/ngmt.mtk/guanyu-vn/_tools/shots'; const PORT=9226;
mkdirSync(OUT,{recursive:true});
const chrome=spawn(CHROME,['--headless=new',`--remote-debugging-port=${PORT}`,'--user-data-dir=/tmp/guanyu_cdp4','--no-first-run','--hide-scrollbars','--force-device-scale-factor=2','--window-size=412,915'],{stdio:'ignore'});
async function getWs(){for(let i=0;i<40;i++){try{const j=await (await fetch(`http://localhost:${PORT}/json/version`)).json();if(j.webSocketDebuggerUrl)return j.webSocketDebuggerUrl;}catch{}await sleep(250);}throw new Error('no cdp');}
const ws=new WebSocket(await getWs()); await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
let _id=0;const pend=new Map(); ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&pend.has(d.id)){pend.get(d.id)(d);pend.delete(d.id);}};
const cmd=(method,params={},s)=>new Promise(res=>{const id=++_id;pend.set(id,res);ws.send(JSON.stringify({id,method,params,...(s?{sessionId:s}:{})}));});
const {result:tg}=await cmd('Target.getTargets'); const page=tg.targetInfos.find(t=>t.type==='page');
const {result:{sessionId}}=await cmd('Target.attachToTarget',{targetId:page.targetId,flatten:true});
const S=(m,p)=>cmd(m,p,sessionId);
await S('Page.enable');await S('Runtime.enable');
await S('Page.navigate',{url:URL}); await sleep(2500);
const ev=async e=>{const r=await S('Runtime.evaluate',{expression:e,awaitPromise:true,returnByValue:true});return r.result?.result?.value;};
await ev(`window.__seek=function(act,n){start();go(act);for(var i=0;i<n;i++){advance();}return nodeId+':'+idx;};`);
async function shot(n){const r=await S('Page.captureScreenshot',{format:'png'});writeFileSync(`${OUT}/${n}.png`,Buffer.from(r.result.data,'base64'));}
const cases=[['act03',2,'fix03_act03'],['act05',5,'fix04_act05'],['act08',9,'fix02_act08'],['act09',6,'fix05_act09'],['act11',10,'fix01_act11']];
for(const [act,adv,nm] of cases){
  await ev(`__seek('${act}', ${adv});`); await sleep(800);
  const txt=await ev(`document.getElementById('text').textContent`);
  const onstage=await ev(`stage.map(function(s){return s.char}).join(',')`);
  await shot(nm);
  console.log(nm,'| stage:['+onstage+'] | text:', (txt||'').slice(0,70).replace(/\n/g,' '));
}
ws.close();chrome.kill();await sleep(300);
