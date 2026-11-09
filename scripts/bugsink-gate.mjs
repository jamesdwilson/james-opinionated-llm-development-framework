import {trackChild, callbackFlow, existingIdentity, deadline} from './bugsink/lifecycle.mjs';
import { spawn, execFileSync } from 'node:child_process';
import { mkdtemp, mkdir, readFile, rm, stat, writeFile } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { randomUUID } from 'node:crypto';
import net from 'node:net';
import { createReadback } from './bugsink/api-client.mjs';
import assert from 'node:assert/strict';
import { chromium } from '@playwright/test';
import { createTaskServer } from '../src/server.mjs';
const evidence=resolve('evidence/bugsink'); await mkdir(evidence,{recursive:true});
const run=process.argv[2] || ('repair-stack-'+Date.now()); if(!/^[a-z0-9-]+$/.test(run)) throw Error('Invalid run label');
const failureMode=process.argv[3]?.startsWith('--fail-')?process.argv[3].slice(7):undefined;
const before=existingIdentity();
await mkdir('.tmp',{recursive:true});
const dir=await mkdtemp(resolve('.tmp/bugsink-'));
let browserOwner, browserTracked, browserPort, tracked, child, browser, server, config, port, phase='setup', childOutput='', failureReached=false, result={passed:false};
const childEnv={PATH:'/usr/bin:/bin', PYTHONDONTWRITEBYTECODE:'1', LAB_STATE:dir, LAB_FAIL:failureMode==='bootstrap'?'bootstrap':failureMode==='output'?'output':''};
const forbidden=[];
const check=value=>{const s=typeof value==='string'?value:JSON.stringify(value); if(forbidden.some(v=>s.includes(v)))throw Error('Sensitive material crossed boundary');};
let api;
const rows=x=>Array.isArray(x)?x:x.results;
try{
  child=spawn('/Users/james/.hermes-next-v0.22.4/cache/scratch/bugsink-2.6.3-venv/bin/python',['-B',resolve('scripts/bugsink/service.py')],{env:childEnv,stdio:['ignore','pipe','pipe']});
  tracked=trackChild(child);
  await deadline((async()=>{while(!tracked.output.includes('READY')){if(tracked.error)throw tracked.error;if(tracked.done)throw Error('Isolated startup failed');await new Promise(r=>setTimeout(r,25));}})(),60000);
  childOutput=tracked.output;
  config=JSON.parse(await readFile(join(dir,'runtime.json'),'utf8'));
  phase='runtime-file-permissions';
  forbidden.push(config.token,dir,join(dir,'runtime.json'));
  assert.equal((await stat(join(dir,'runtime.json'))).mode & 0o777,0o600);
  for(const name of ['default.sqlite3','snappea.sqlite3','django-key']) assert.equal((await stat(join(dir,name))).mode & 0o777,0o600);
  for(const name of ['default.sqlite3','snappea.sqlite3']) assert.equal((await readFile(join(dir,name))).subarray(0,15).toString(),'SQLite format 3');
  assert.equal(config.version,'2.6.3'); assert.notEqual(config.port,8100);
  phase='startup-output';
  check(childOutput); assert.equal(childOutput.trim(),'READY');
  api=createReadback(config);
  phase='api-boundary';
  if(failureMode==='response'){failureReached=true;await createReadback(config,async()=>new Response(new ReadableStream({pull(c){c.enqueue(new Uint8Array(300000));}})))('projects/');}
  if(failureMode==='already-exited'){failureReached=true;child.kill('SIGTERM');await tracked.completion;throw Error('Injected exited child');}
  if(failureMode==='after-ready'){failureReached=true;throw Error('Injected cleanup verification');}
  await api('projects/',{token:'invalid',expected:401});
  await api('projects/',{method:'POST',expected:403});
  const projects=rows(await api('projects/')); assert.equal(projects.length,1); assert.equal(projects[0].id,config.project);
  assert.equal(rows(await api(`issues/?project=${config.project}`)).length,0);
  const canary=randomUUID().replaceAll('-',''), release='lab-'+canary, environment='isolated';
  const monitoring={dsn:config.dsn,release,environment,canary,testCanary:true};
  check(monitoring);
  server=createTaskServer({databasePath:join(dir,'tasks.sqlite'),monitoring});
  port=(await server.listen()).port;
  phase='browser';
  // No runtime path/token in browser env, trace, report, navigation or task-server options.
  browserOwner=await chromium.launchServer({host:'127.0.0.1',timeout:15000,env:{PATH:process.env.PATH,HOME:process.env.HOME}});
  browserTracked=trackChild(browserOwner.process());
  browserPort=Number(new URL(browserOwner.wsEndpoint()).port);
  browser=await chromium.connect(browserOwner.wsEndpoint(),{timeout:10000});
  const context=await browser.newContext(); const page=await context.newPage();
  const errors=[],sent=[]; const captures=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',m=>captures.push(m.text()));
  const flow=callbackFlow();
  page.on('request',flow.wrap(r=>{if(failureMode==='callback'){failureReached=true;throw Error('Injected callback');}check(r.url());check(r.headers());if(r.postData())check(r.postData());if(r.url().includes('/store/'))sent.push({body:JSON.parse(r.postData()),headers:r.headers()});}));
  const start=Date.now();
  await page.goto(`http://127.0.0.1:${port}/?canary=1`);
  await page.getByText('The test error was contained. You can continue creating tasks.',{exact:true}).waitFor();
  await page.getByLabel('Task title',{exact:true}).fill('Recovery still works');
  await page.getByRole('radio',{name:'Complete directly',exact:true}).check();
  await page.getByRole('button',{name:'Create task',exact:true}).click();
  await page.getByRole('heading',{name:'Recovery still works',exact:true}).waitFor();
  flow.check();
  check(await page.content()); check(captures);
  assert.deepEqual(errors,['Isolated lab canary']); assert.equal(sent.length,1);
  assert.equal(sent[0].headers.cookie,undefined); assert.equal(sent[0].headers.authorization,undefined);
  const expected=sent[0].body;
  assert.deepEqual(Object.keys(expected).sort(),['environment','event_id','exception','level','platform','release','tags','timestamp']);
  if(failureMode==='after-browser'){failureReached=true;throw Error('Injected browser cleanup verification');}
  phase='readback';
  const issues=await api(`issues/?project=${config.project}`); assert.equal(issues.next,null); assert.equal(rows(issues).length,1);
  const events=await api(`events/?issue=${rows(issues)[0].id}`); assert.equal(events.next,null);assert.equal(rows(events).length,1);
  const event=await api(`events/${rows(events)[0].id}/`);
  assert.equal(event.project,config.project);assert.equal(event.event_id.replaceAll('-',''),expected.event_id);
  assert.deepEqual(event.data,expected);
  assert.equal(event.data.release,release);assert.equal(event.data.environment,environment);assert.equal(event.data.tags.canary,canary);
  assert.deepEqual(event.data.exception.values,[{type:'LabCanaryError',value:'Isolated lab canary'}]);
  for(const time of [event.timestamp,event.ingested_at]) assert.ok(Date.parse(time)>=start-1000 && Date.parse(time)<=Date.now()+1000);
  assert.ok(event.data.timestamp*1000>=start && event.data.timestamp*1000<=Date.now());
  check(event);check(childOutput);
  result={passed:true,version:config.version,fresh:true,sqliteDatabases:2,events:1,exactPayload:true,recovery:true,eventId:expected.event_id,phase:'complete'};
}catch{
  if(failureMode==='bootstrap'||failureMode==='output'){
    try{failureReached=JSON.parse(await readFile(join(dir,'failure-reached.json'),'utf8')).mode===failureMode;}catch{}
  }
  result={passed:false,phase,failureMode,failureReached,diagnostic:'Isolated gate failed; sensitive diagnostics suppressed'};process.exitCode=1;
}
finally{
  let cleanup=true;
  let listener;
  try{listener=JSON.parse(await readFile(join(dir,'listener.json'),'utf8'));assert.equal(listener.pid,child.pid);assert.notEqual(listener.port,8100);}catch{if(child)cleanup=false;}
  try{if(browser)await deadline(browser.close());}catch{cleanup=false;}
  try{if(browserOwner)await deadline(browserOwner.close());}catch{try{await deadline(browserOwner.kill());}catch{cleanup=false;}}
  try{if(browserTracked)await browserTracked.stop();}catch{cleanup=false;}
  try{if(server)await deadline(server.close());}catch{cleanup=false;}
  try{if(tracked)await tracked.stop();}catch{cleanup=false;}
  try{await rm(dir,{recursive:true,force:true});}catch{cleanup=false;}
  const ports=[port,listener?.port,browserPort].filter(Boolean);
  for(const p of ports){try{await deadline(new Promise((yes,no)=>{const s=net.createServer();s.once('error',no);s.listen(p,'127.0.0.1',()=>s.close(yes));}));}catch{cleanup=false;}}
  let after;try{after=existingIdentity();}catch{cleanup=false;}
  result.cleanup={browserProcessExited:!browserTracked || browserTracked.done,browserDisconnected:!browser || !browser.isConnected(),taskServerClosed:cleanup,stateDeleted:await stat(dir).then(()=>false,()=>true),portsClear:cleanup,ports,childExited:!child || tracked.done,existing8100Unchanged:JSON.stringify(before)===JSON.stringify(after),existing8100Before:before,existing8100After:after};
  if(!cleanup || !result.cleanup.stateDeleted || !result.cleanup.existing8100Unchanged) {result.passed=false;process.exitCode=1;}
  const file=join(evidence,`${run}.json`);
  await writeFile(file,JSON.stringify(result,null,2)+'\n');
  // Final success/failure bytes exist, runtime secret-bearing files have been removed.
  try{
    const scan=JSON.parse(execFileSync('/usr/bin/python3',['scripts/bugsink/scan.py',evidence],{input:JSON.stringify([...forbidden,config?.dsn].filter(Boolean)),encoding:'utf8',maxBuffer:8*1024*1024,timeout:60000}));
    assert.equal(scan.passed,true);
    await writeFile(join(evidence,`${run}-scan.json`),JSON.stringify(scan,null,2)+'\n');
  }catch{process.exitCode=1;result.passed=false;result.scanFailure=true;await writeFile(file,JSON.stringify(result,null,2)+'\n');}
  console.log(JSON.stringify(result));
}
