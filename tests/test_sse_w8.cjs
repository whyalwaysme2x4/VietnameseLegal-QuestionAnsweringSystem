'use strict';
const assert=require('node:assert/strict');
const {readSSE}=require('../sse.js');
function response(bytes,size){return {body:new ReadableStream({start(controller){for(let i=0;i<bytes.length;i+=size)controller.enqueue(bytes.slice(i,i+size));controller.close();}})};}
(async()=>{
  let checks=0;const text=': keepalive\r\n\r\ndata: '+JSON.stringify({type:'plan',reason:'Tiếng Việt: điều, khoản, điểm'})+'\r\n\r\ndata: {"type":"final","answer":"Có căn cứ"}\n\ndata: {"type":"done"}\n\n';
  for(const size of [1,2,3,7,4096]){const events=[];await readSSE(response(new TextEncoder().encode(text),size),e=>events.push(e));assert.equal(events.length,3);assert.equal(events[0].reason,'Tiếng Việt: điều, khoản, điểm');checks++;}
  await assert.rejects(()=>readSSE(response(new TextEncoder().encode('data: {bad}\n\n'),1),()=>{}));checks++;
  await assert.rejects(()=>readSSE(response(new TextEncoder().encode('data: {"type":"final"}'),1),()=>{}));checks++;
  const events=[];await readSSE(response(new TextEncoder().encode(': heartbeat\n\n'),1),e=>events.push(e));assert.equal(events.length,0);checks++;
  console.log(JSON.stringify({suite:'W8 SSE byte-fragment parser',checks,passed:checks,aws_calls:0}));
})().catch(error=>{console.error(error);process.exitCode=1;});
