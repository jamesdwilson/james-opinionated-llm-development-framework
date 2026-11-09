import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createReadback} from '../scripts/bugsink/api-client.mjs';
test('real readback client bounds auth, transport and JSON diagnostics',async()=>{
 const secret='SENTINEL token DSN runtime path';
 for(const [transport,message] of [[async()=>{throw Error(secret)},'Monitoring transport'],[async()=>({status:401,text:()=>secret}),'Monitoring API status'],[async()=>({status:200,json:()=>{throw Error(secret)}}),'Monitoring API format']]){
   await assert.rejects(createReadback({port:54321,token:'a'.repeat(40)},transport)('projects/'),{message});
 }
});
test('readback rejects port 8100 and noncanonical routes before dispatch',async()=>{
 assert.throws(()=>createReadback({port:8100,token:'a'.repeat(40)}),{message:'Monitoring API configuration'});
 await assert.rejects(createReadback({port:54321,token:'a'.repeat(40)},()=>{throw Error('dispatch')})('https://example.com'),{message:'Monitoring API route'});
});
test('oversized streamed API input is cancelled and shapes are rejected',async()=>{
 let cancelled=false, chunks=0;
 const body=new ReadableStream({pull(c){if(chunks++<2)c.enqueue(new Uint8Array(1024*1024));else c.close();},cancel(){cancelled=true;}});
 await assert.rejects(createReadback({port:54321,token:'a'.repeat(40)},async()=>new Response(body))('projects/'),/Monitoring API bound/);
 assert.equal(cancelled,true);
 for(const value of [null,{}, {results:'wrong',next:null}]) await assert.rejects(createReadback({port:54321,token:'a'.repeat(40)},async()=>Response.json(value))('projects/'),/Monitoring API format/);
});
