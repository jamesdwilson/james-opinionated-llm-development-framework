import {execFileSync} from 'node:child_process';
export function deadline(p,ms=5000){let t;return Promise.race([p,new Promise((_,reject)=>{t=setTimeout(()=>reject(Error('Shutdown deadline')),ms);})]).finally(()=>clearTimeout(t));}
export function trackChild(child,limit=65536){
 let bytes=0, output='', error; let done=false;
 const completion=new Promise(resolve=>{const finish=()=>{done=true;resolve();};child.once('exit',finish);child.once('error',()=>{error=Error('Child startup');finish();});});
 for(const stream of [child.stdout,child.stderr])stream?.on('data',b=>{bytes+=b.length;if(bytes>limit){error=Error('Child output bound');child.kill('SIGTERM');}else output+=b.toString();});
 return {completion,get done(){return done || child.exitCode!==null || child.signalCode!==null;},get output(){return output;},get error(){return error;},async stop(){if(this.done)return;child.kill('SIGTERM');try{await deadline(completion,2000);}catch{if(!this.done)child.kill('SIGKILL');await deadline(completion,2000);}}};
}
export function callbackFlow(){let failure;return {wrap(fn){return (...args)=>{try{fn(...args);}catch{failure=Error('Browser callback failed');}};},check(){if(failure)throw failure;}};}
export function existingIdentity(exec=execFileSync){
 let raw;
 try{raw=exec('/usr/sbin/lsof',['-nP','-a','-iTCP:8100','-sTCP:LISTEN','-Fpcfn'],{encoding:'utf8',timeout:3000});}
 catch(e){if(e.status===1 && !String(e.stdout||'').trim() && !String(e.stderr||'').trim())return {status:'absent',owners:[]};throw Error('Listener inspection failed');}
 const owners=[];let owner;
 for(const line of raw.trim().split('\n')){if(line[0]==='p'){owner={pid:Number(line.slice(1)),listeners:[]};owners.push(owner);}else if(line[0]==='n' && owner)owner.listeners.push(line.slice(1));}
 if(!owners.length)throw Error('Listener identity unavailable');
 for(const o of owners){if(!Number.isSafeInteger(o.pid)||!o.listeners.length)throw Error('Listener identity unavailable');try{o.start=exec('/bin/ps',['-p',String(o.pid),'-o','lstart='],{encoding:'utf8',timeout:3000}).trim();}catch{throw Error('Process incarnation unavailable');}if(!o.start)throw Error('Process incarnation unavailable');o.listeners.sort();}
 return {status:'present',owners:owners.sort((a,b)=>a.pid-b.pid)};
}
