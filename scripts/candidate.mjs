import {readdir,readFile,lstat,readlink,realpath} from 'node:fs/promises';
import {chromium} from '@playwright/test';
import {dirname} from 'node:path';
import {createHash} from 'node:crypto';
export const hash=b=>createHash('sha256').update(b).digest('hex');
const regularChromiumRoot=dirname(dirname(dirname(chromium.executablePath())));
const chromiumRevision=chromium.executablePath().match(/^(.*\/ms-playwright)\/chromium-(\d+)\//);
if(!chromiumRevision)throw Error('Revisioned Playwright Chromium path required');
const headlessChromiumRoot=`${chromiumRevision[1]}/chromium_headless_shell-${chromiumRevision[2]}`;
export const candidatePaths=['src','public','scripts','test','e2e','research','stubs','node_modules','package.json','package-lock.json','bun.lock','playwright.config.ts','llm-policy.json','README.md','.gitignore','NORTH_STAR.md','JOURNEY_CATALOG.md','ACCEPTANCE_MATRIX.md','ACCEPTED_CHECKS.json','LLM_POLICY.md','/Users/james/.hermes-next-v0.22.4/cache/scratch/bugsink-2.6.3-venv/lib','/Users/james/.hermes-next-v0.22.4/cache/scratch/bugsink-2.6.3-venv/bin/python','/opt/homebrew/bin/bun',regularChromiumRoot,headlessChromiumRoot];
export async function manifest(){
 const files={};
 async function walk(path){const st=await lstat(path);if(st.isSymbolicLink()){files[path]=hash('symlink:'+await readlink(path));return;}if(st.isDirectory()){for(const n of (await readdir(path)).sort())await walk(path+'/'+n);}else if(st.isFile())files[path]=hash(await readFile(path));}
 for(const p of [...candidatePaths,await realpath('/opt/homebrew/bin/bun'),await realpath('/Users/james/.hermes-next-v0.22.4/cache/scratch/bugsink-2.6.3-venv/bin/python')])await walk(p);
 return {schema:1,files,id:hash(JSON.stringify(files))};
}
export function closure(candidate,records){
 const blocks=[];
 const exact=r=>JSON.stringify(r.before)===JSON.stringify(candidate) && JSON.stringify(r.after)===JSON.stringify(candidate);
 const independentlyVerified=r=>exact(r) && r.artifactsVerified===true && r.resultsVerified===true && r.semanticVerified===true && typeof r.executionId==='string' && /^[0-9a-f-]{36}$/.test(r.executionId);
 const exactRecords=records.filter(exact);
 const expectedExit=r=>r.kind==='failure'?1:['bun','chromium','bugsink','J05','J06','audit'].includes(r.kind)?0:null;
 for(const r of exactRecords)if(expectedExit(r)===null || !independentlyVerified(r) || r.exit!==expectedExit(r))blocks.push('Unresolved exact-candidate evidence '+String(r.run||r.kind||'unknown'));
 const usable=exactRecords.filter(r=>independentlyVerified(r) && r.exit===0);
 for(const kind of ['bun','chromium','bugsink'])if(new Set(usable.filter(r=>r.kind===kind).map(r=>r.executionId)).size<2)blocks.push('Missing repeated exact-candidate '+kind);
 for(const kind of ['J05','J06'])if(new Set(usable.filter(r=>r.kind===kind && r.review?.model==='gpt-6-sol' && r.review?.auth==='siwc' && r.review?.providerReasoning==='low' && r.review?.planningEffort==='balance' && r.review?.verdict===(kind==='J05'?'RED':'GREEN') && r.review?.outcome===(kind==='J05'?'stopped_at_unclear_choice':'completed_goal') && (kind!=='J06'||r.review?.contradictions?.length===0)).map(r=>r.executionId)).size<2)blocks.push('Missing fresh exact-candidate '+kind+' review pair');
 for(const mode of ['bootstrap','callback','already-exited','output','response'])if(!records.some(r=>r.kind==='failure' && r.failureMode===mode && independentlyVerified(r) && r.exit===1))blocks.push('Missing injected cleanup '+mode);
 for(const r of usable.filter(r=>r.kind==='bugsink'))if(!r.cleanup || ['browserProcessExited','browserDisconnected','taskServerClosed','stateDeleted','portsClear','childExited','existing8100Unchanged'].some(k=>r.cleanup[k]!==true))blocks.push('Incomplete cleanup');
 if(!usable.some(r=>r.kind==='audit'))blocks.push('Dependency security unresolved (finding 8)');
 return {passed:blocks.length===0,blocks};
}
