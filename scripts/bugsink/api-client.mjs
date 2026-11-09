// Verification runs only in Node. Never import this module into browser code.
export function createReadback({port,token}, transport=fetch) {
  if (!Number.isInteger(port) || port<1024 || port>65535 || port===8100 || !/^[a-f0-9]{40}$/.test(token)) throw Error('Monitoring API configuration');
  return async function api(path,{method='GET',token:override=token,expected=200}={}) {
    if(!/^(projects\/|issues\/\?project=[1-9][0-9]*|events\/(?:\?issue=[a-f0-9-]+|[a-f0-9-]+\/))$/.test(path))throw Error('Monitoring API route');
    let response;
    try{response=await transport(`http://127.0.0.1:${port}/api/canonical/0/${path}`,{method,headers:{Authorization:`Bearer ${override}`},signal:AbortSignal.timeout(5000),redirect:'error'});}catch{throw Error('Monitoring transport');}
    if(response.status!==expected)throw Error('Monitoring API status');
    if(expected!==200)return;
    let reader, size=0, chunks=[];
    try{
      reader=response.body.getReader();
      while(true){const {done,value}=await reader.read();if(done)break;size+=value.byteLength;if(size>262144){await reader.cancel();throw Error('Monitoring API bound');}chunks.push(value);}
      const value=JSON.parse(Buffer.concat(chunks).toString('utf8'));
      const visit=(v,d=0)=>{if(d>20)throw Error();if(v && typeof v==='object')for(const x of Object.values(v))visit(x,d+1);};visit(value);
      if(path.startsWith('events/') && !path.includes('?')){if(!value || typeof value!=='object' || !value.data || typeof value.event_id!=='string' || !Number.isInteger(value.project))throw Error();}
      else if(!(Array.isArray(value) || (value && Array.isArray(value.results) && value.next===null)))throw Error();
      return value;
    }catch(e){try{await reader?.cancel();}catch{}throw Error(e.message==='Monitoring API bound'?'Monitoring API bound':'Monitoring API format');}
  };
}
