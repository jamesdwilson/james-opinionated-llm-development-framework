import { test } from 'node:test';
import assert from 'node:assert/strict';
import { installMonitoring, parseDsn, diagnostic } from '../public/monitoring.js';
const key = 'a'.repeat(32);
test('blank monitoring installs no listeners and dispatches nothing', () => {
  assert.equal(installMonitoring({ dsn:' ' }, { addEventListener(){throw Error('listener');} }), null);
});
test('strict DSN rejects malformed, remote, password, query and normalized evasions before dispatch', () => {
  for (const dsn of ['https://example.com/1', `http://${key}@example.com/1`, `http://${key}:secret@127.0.0.1/1`, `http://${key}@127.1/1`, `http://${key}@127.0.0.1/0`, `http://${key}@127.0.0.1/1?q=x`, `http://${key}@127.0.0.1/1#x`, `http://${key}@127.0.0.1/a/../1`, 'secret']) {
    assert.throws(() => installMonitoring({dsn}, {fetch(){throw Error('dispatch');}}), /^Error: Monitoring configuration rejected$/);
  }
  assert.ok(parseDsn(`http://${key}@127.0.0.1:12345/1`));
});
test('both global hooks send only bounded allowlisted fields with credentials omitted', async () => {
  const hooks={}, requests=[];
  const scope={addEventListener:(k,v)=>hooks[k]=v, crypto:{randomUUID:()=> 'b'.repeat(32)}, fetch:async(...r)=>{requests.push(r);return {ok:true};}};
  installMonitoring({dsn:`http://${key}@127.0.0.1:12345/1`, release:'lab-v1', environment:'isolated', canary:'c'.repeat(32)},scope);
  hooks.error({error:Error('email@example.com secret')}); hooks.unhandledrejection({reason:'cookie secret'});
  await new Promise(r=>setImmediate(r));
  assert.equal(requests.length,2);
  for(const [,options] of requests){
    assert.equal(options.redirect,'error'); assert.equal(options.credentials,'omit'); assert.equal(options.referrerPolicy,'no-referrer');
    const event=JSON.parse(options.body);
    assert.deepEqual(Object.keys(event).sort(),['environment','event_id','exception','level','platform','release','tags','timestamp']);
    assert.equal(event.exception.values[0].value,'Browser failure (details withheld)');
    assert.ok(!options.body.includes('secret'));
  }
});
test('diagnostics never reflect transport, API or auth input',()=>{
  for(const kind of ['auth','api','transport','secret /private/runtime']) assert.match(diagnostic(kind),/^Monitoring (auth|api|transport|failure)$/);
});
test('task HTTP configuration excludes privileged fields and runtime paths', async()=>{
  const {createTaskServer}=await import('../src/server.mjs');
  const {mkdtemp,rm}=await import('node:fs/promises');
  const {resolve,join}=await import('node:path');
  const dir=await mkdtemp(resolve('.tmp/boundary-'));
  const server=createTaskServer({databasePath:join(dir,'tasks.sqlite'),monitoring:{dsn:'',token:'SENTINEL-READ-TOKEN',runtimeFile:'SENTINEL-RUNTIME-PATH'}});
  try{
    const address=await server.listen();
    const text=await (await fetch(`http://127.0.0.1:${address.port}/monitoring-config`)).text();
    assert.ok(!text.includes('SENTINEL'));assert.deepEqual(JSON.parse(text),{dsn:'',testCanary:false});
  }finally{await server.close();await rm(dir,{recursive:true,force:true});}
});
