'use strict';
// The same data: JSON / blank-line contract as the original frontend.
// UTF-8 and event delimiters may be split at any byte boundary by the network.
(function(root) {
  async function readSSE(response, onEvent) {
    if (!response.body) throw new Error('Không nhận được luồng SSE.');
    const reader=response.body.getReader(), decoder=new TextDecoder('utf-8');
    let buffer='';
    function drain() {
      let separator;
      while ((separator=/\r?\n\r?\n/.exec(buffer))!==null) {
        const frame=buffer.slice(0,separator.index);
        buffer=buffer.slice(separator.index+separator[0].length);
        const data=frame.split(/\r?\n/).filter(line=>line.startsWith('data:'))
          .map(line=>line.slice(5).replace(/^ /,'')).join('\n');
        if (!data.trim()) continue; // keepalive comments and empty events
        let event;
        try { event=JSON.parse(data); }
        catch { throw new Error('Sự kiện SSE không đúng định dạng JSON.'); }
        onEvent(event);
      }
    }
    try {
      while (true) {
        const {value,done}=await reader.read();
        buffer+=decoder.decode(value||new Uint8Array(),{stream:!done});
        drain();
        if (done) break;
      }
      if (buffer.trim() && !buffer.trim().startsWith(':'))
        throw new Error('Luồng SSE kết thúc giữa một sự kiện.');
    } catch(error) {
      try { await reader.cancel(); } catch {}
      throw error;
    } finally { reader.releaseLock(); }
  }
  root.DemoSSE={readSSE};
  if (typeof module!=='undefined' && module.exports) module.exports={readSSE};
})(globalThis);
