// Deliberately no SDK, breadcrumbs, identity, stack, URL, or arbitrary error text.
export function diagnostic(kind) {
  return `Monitoring ${['auth','api','transport'].includes(kind) ? kind : 'failure'}`;
}
export function parseDsn(value) {
  if (value == null || (typeof value === 'string' && !value.trim())) return null;
  if (typeof value !== 'string' || !/^https?:\/\/[a-f0-9]{32}@(127\.0\.0\.1|localhost|\[::1\])(?::[1-9][0-9]{0,4})?\/[1-9][0-9]*$/.test(value)) throw Error('Monitoring configuration rejected');
  let u; try { u=new URL(value); } catch { throw Error('Monitoring configuration rejected'); }
  if (!Number.isSafeInteger(Number(u.pathname.slice(1)))) throw Error('Monitoring configuration rejected');
  return { endpoint:`${u.origin}/api${u.pathname}/store/?sentry_version=7&sentry_key=${u.username}` };
}
export function installMonitoring(config, scope=globalThis) {
  const target=parseDsn(config.dsn);
  if (!target) return null;
  if (![config.release,config.environment].every(v=>typeof v==='string' && /^[a-zA-Z0-9._-]{1,64}$/.test(v)) || !/^[a-f0-9]{32}$/.test(config.canary)) throw Error('Monitoring configuration rejected');
  const send=event=>{
    // Only the deliberate fixture exception has a known, non-sensitive message.
    const deliberate=event?.name==='LabCanaryError' && event?.message==='Isolated lab canary';
    const payload={event_id:scope.crypto.randomUUID().replaceAll('-',''), timestamp:Date.now()/1000, platform:'javascript', level:'error', release:config.release, environment:config.environment, tags:{canary:config.canary}, exception:{values:[{type:deliberate?'LabCanaryError':'BrowserError',value:deliberate?'Isolated lab canary':'Browser failure (details withheld)'}]}};
    try { Promise.resolve(scope.fetch(target.endpoint,{method:'POST',redirect:'error',mode:'cors',credentials:'omit',referrerPolicy:'no-referrer',headers:{'content-type':'text/plain'},body:JSON.stringify(payload)})).catch(()=>{}); } catch { /* Never echo transport material. */ }
  };
  scope.addEventListener('error',e=>send(e.error));
  scope.addEventListener('unhandledrejection',e=>send(e.reason));
  return true;
}
