'use strict';
const $=id=>document.getElementById(id);
let domain='all',busy=false,ready=false,evaluating=false,currentSessionId=null,historyLoading=false,controller=null;
const SESSION_KEY='legalqa_w8_session';
function el(tag,cls,text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;}
function toast(text){$('toast').textContent=text;$('toast').style.display='block';setTimeout(()=>$('toast').style.display='none',5000);}
function scope(value){domain=value;document.querySelectorAll('.scope').forEach(b=>{b.classList.toggle('active',b.dataset.domain===value);b.setAttribute('aria-pressed',String(b.dataset.domain===value));});}
function scroll(){const a=$('scroll-area');a.scrollTop=a.scrollHeight;}
function addMessage(role,text){const n=el('article','message '+role);n.append(el('div','role',role==='bot'?'§ LUẬT VIỆT · RAG DEMO':'BẠN'),el('div','message-text',text));$('messages').append(n);return n;}
function updateControls(){
  $('send').disabled=busy||historyLoading||!ready||evaluating||!currentSessionId;
  $('question').disabled=busy||historyLoading;$('method').disabled=busy;
  $('new-chat').disabled=busy||historyLoading;$('stop-stream').hidden=!busy;
  document.body.classList.toggle('busy',busy);
}
async function api(path,options){const r=await fetch(path,options);const data=await r.json();if(!r.ok)throw new Error(data.error||'Yêu cầu chưa hoàn tất.');return data;}

async function openSource(id,snapshot){
  try{const s=snapshot?.text?snapshot:await api('/api/source/'+encodeURIComponent(id));
    $('dialog-title').textContent=s.article+(s.clause?' · Khoản '+s.clause:'');
    $('dialog-meta').textContent=s.number+' · '+s.issuer+' · Ban hành '+s.issued;
    $('dialog-text').textContent=s.text;$('dialog-file').textContent='Tệp: '+s.source_file+(snapshot?.text?' · Bản nguồn lưu cùng lượt hỏi':'');
    $('source-dialog').showModal();
  }catch{toast('Không mở được nguồn.');}
}
function renderSources(sources,cited=true){
  $('source-count').textContent=sources.length;$('sources').replaceChildren();
  if(!sources.length){$('sources').append(el('p','empty-source','Nguồn sẽ xuất hiện sau khi xử lý câu hỏi.'));return;}
  sources.forEach((s,i)=>{const c=el('article','source-card');
    c.append(el('div','number',(cited?'NGUỒN ĐƯỢC DẪN':'ỨNG VIÊN TRUY XUẤT')+` · ${i+1} / ${s.number}`),el('h3','',s.title),
      el('div','article',s.article+(s.clause?' · Khoản '+s.clause:'')),el('p','',s.issuer+' · '+s.issued));
    const b=el('button','','Đọc nội dung nguồn ↗');b.onclick=()=>openSource(s.id,s);c.append(b);$('sources').append(c);
  });
}
function showPayload(box,event){
  const cited=(event.sources||[]).length>0;
  const sources=cited?event.sources:(event.retrieved_sources||[]);
  const meta=el('div','result-meta');
  meta.append(el('span','',event.fixture_execution?'Kiểm thử tích hợp bằng fixture':event.llm?('Nova Micro / '+(event.llm_calls||1)+' calls'):'Retrieval trong corpus'),
    el('span','','Hiệu lực nguồn chưa xác minh'));
  if(sources.length){const b=el('button','text-button','Xem nguồn của câu trả lời này');b.onclick=()=>{
    renderSources(sources,cited);
    if(matchMedia('(max-width:940px)').matches){$('sources-panel').classList.add('mobile-open');$('close-sources-panel').hidden=false;}
  };meta.append(b);}
  box.append(meta);
  if(event.trace?.length){const d=el('details','trace');d.append(el('summary','','Xem luồng truy xuất'),el('pre','',JSON.stringify(event.trace,null,2)));box.append(d);}
  if(event.history_status==='failed')box.append(el('p','history-warning','Chưa lưu được lượt này vào lịch sử.'));
  renderSources(sources,cited);
}
function clearChat(){ $('messages').replaceChildren();$('welcome').hidden=false;renderSources([]);$('question').value='';$('sources-panel').classList.remove('mobile-open');$('close-sources-panel').hidden=true; }
async function loadSessions(){
  const data=await api('/api/session/get-sessions');$('chat-sessions').replaceChildren();
  for(const session of data.sessions){
    const row=el('div','history-row'+(session.id===currentSessionId?' active':''));
    const open=el('button','history-open',session.first_message);open.title=session.first_message;
    open.setAttribute('aria-current',String(session.id===currentSessionId));open.onclick=()=>openSession(session.id);
    const del=el('button','history-delete','×');del.setAttribute('aria-label','Xóa phiên '+session.id);del.onclick=()=>deleteSession(session.id);
    row.append(open,del);if(session.status==='processing')row.append(el('span','session-state','đang xử lý'));
    $('chat-sessions').append(row);
  }
  return data.sessions;
}
async function newSession(){
  if(busy||historyLoading)return;
  try{const data=await api('/api/session/start-session',{method:'POST'});currentSessionId=data.session_id;
    localStorage.setItem(SESSION_KEY,String(currentSessionId));clearChat();await loadSessions();updateControls();
  }catch(e){toast(e.message);}
}
async function openSession(id){
  if(busy||historyLoading)return;
  historyLoading=true;updateControls();
  try{
    const data=await api('/api/session/get-chat-history/'+id);currentSessionId=id;localStorage.setItem(SESSION_KEY,String(id));clearChat();
    const byMessage=new Map(data.chat_history.map(m=>[m.id,m]));
    for(const turn of data.turns){
      $('welcome').hidden=true;addMessage('user',turn.question);
      if(turn.status==='complete'){
        const message=byMessage.get(turn.bot_message_id);
        if(message){const box=addMessage('bot',message.message);if(message.payload)showPayload(box,message.payload);}
      }else{
        addMessage('bot',turn.status==='processing'?'Lượt này đang xử lý ở máy chủ. Bấm Tải lại lịch sử sau khi hoàn tất.':
          'Lượt trước chưa hoàn tất ('+(turn.error_code||'pipeline_error')+'). Bạn có thể gửi lại câu hỏi.');
      }
    }
    if(data.turns.length){const last=data.turns[data.turns.length-1];scope(last.domain);$('method').value=last.mode;}
    await loadSessions();scroll();
  }catch(e){toast(e.message);}
  finally{historyLoading=false;updateControls();}
}
async function deleteSession(id){
  if(busy||historyLoading)return;
  if(!confirm('Xóa phiên này cùng tin nhắn và nguồn đã lưu?'))return;
  try{await api('/api/session/delete-session/'+id,{method:'DELETE'});
    if(id===currentSessionId){currentSessionId=null;localStorage.removeItem(SESSION_KEY);clearChat();}
    const sessions=await loadSessions();
    if(!currentSessionId){if(sessions.length)await openSession(sessions[0].id);else await newSession();}
  }catch(e){toast(e.message);}
}

const steps={agentic_loading:'Đang nạp BERT và agent graph',plan:'Planner đã chọn hướng xử lý',extract:'BERT đã trích đoạn trọng tâm',
  grade:'Grader đã đánh giá nguồn',check:'Checker đã đối chiếu câu trả lời',iterate:'Đang tìm lại theo quyết định của agent',
  regenerate:'Đang sinh lại theo Checker',graph_node:'Đang thực thi agent graph',retrieve_start:'Đang truy xuất corpus',
  retrieve_done:'Đã có danh sách ứng viên',rerank_start:'CrossEncoder đang xếp hạng lại',rerank_done:'Đã chọn các chunk sau rerank',
  generate_start:'Nova Micro đang tổng hợp từ nguồn',generate_done:'Đã nhận câu trả lời từ Nova'};
async function send(question){
  if(busy||historyLoading||!question.trim())return;
  if(!ready||evaluating||!currentSessionId){toast('Hãy đợi model và phiên hội thoại sẵn sàng.');return;}
  busy=true;controller=new AbortController();updateControls();$('welcome').hidden=true;addMessage('user',question);$('question').value='';
  const pending=el('div','pending','Đang xử lý…'),progress=el('details','progress');progress.open=true;
  const list=el('ol','progress-list');progress.append(el('summary','','Tiến trình xử lý'),list);$('messages').append(progress,pending);scroll();
  let finalSeen=false,errorMessage=null;
  try{
    const response=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},signal:controller.signal,
      body:JSON.stringify({question,domain,mode:$('method').value,session_id:currentSessionId,request_id:crypto.randomUUID()})});
    if(!response.ok){const e=await response.json();throw new Error(e.error||'Không xử lý được câu hỏi.');}
    await DemoSSE.readSSE(response,event=>{
      if(event.type==='history_error'){toast(event.message);return;}
      if(event.type==='error'){errorMessage=event.message;list.append(el('li','',event.message));return;}
      if(event.type==='done')return;
      if(event.type==='final'){
        finalSeen=true;pending.remove();const box=addMessage('bot',event.answer||'Chưa có câu trả lời.');showPayload(box,event);scroll();return;
      }
      const text=(steps[event.type]||event.type)+(event.node?' · '+event.node+' / '+event.phase:'')+
        (event.n_docs!==undefined?' · '+event.n_docs+' đoạn':'');
      pending.textContent=text;list.append(el('li','',text));if(list.childElementCount>50)list.firstChild.remove();scroll();
    });
    if(!finalSeen)throw new Error(errorMessage||'Luồng kết thúc trước kết quả.');
  }catch(error){
    pending.remove();
    if(error.name==='AbortError')addMessage('bot','Đã dừng theo dõi luồng. Máy chủ vẫn có thể đang xử lý; tải lại lịch sử để xem kết quả.');
    else if(!finalSeen){addMessage('bot','Chưa hoàn tất: '+error.message);renderSources([]);}
    else toast('Đã nhận đáp án; kết nối kết thúc chưa đầy đủ. Kiểm tra lịch sử.');
  }finally{
    pending.remove();busy=false;controller=null;updateControls();scroll();
    try{await loadSessions();}catch{}pollStatus();
  }
}
document.querySelectorAll('.scope').forEach(b=>b.onclick=()=>{if(!busy&&!historyLoading)scope(b.dataset.domain);});
document.querySelectorAll('[data-question]').forEach(b=>b.onclick=()=>{if(!busy&&!historyLoading){scope(b.dataset.domain);send(b.dataset.question);}});
$('chat-form').onsubmit=e=>{e.preventDefault();send($('question').value);};
$('question').onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send($('question').value);}};
$('new-chat').onclick=newSession;$('refresh-history').onclick=()=>currentSessionId?openSession(currentSessionId):restoreSession();
$('stop-stream').onclick=()=>controller?.abort();
$('close-sources-panel').onclick=()=>{$('sources-panel').classList.remove('mobile-open');$('close-sources-panel').hidden=true;};
$('close-source').onclick=()=>$('source-dialog').close();$('mode-info').onclick=()=>$('mode-dialog').showModal();$('close-mode').onclick=()=>$('mode-dialog').close();

const phases={starting:'Đang khởi động',loading_embedding:'Đang nạp embedding',tokenizing_corpus:'Đang chuẩn bị corpus',
  embedding_corpus:'Đang đọc/tạo embedding',indexing_qdrant:'Đang tạo index riêng',loading_crossencoder:'Đang nạp CrossEncoder',
  configuring_llm:'Đang chuẩn bị kết nối Nova',ready:'Corpus và model đã sẵn sàng',failed:'Khởi động chưa thành công'};
async function pollStatus(){
  try{const s=await api('/api/status');ready=s.ready;evaluating=['queued','running'].includes(s.evaluation);
    $('evaluation-button').disabled=!ready||busy||evaluating;let text=phases[s.phase]||s.phase;
    if(s.phase==='embedding_corpus')text+=` · ${s.progress}/${s.total}`;
    if(s.fixture_execution)text='KIỂM THỬ FIXTURE · KHÔNG PHẢI ĐÁP ÁN PHÁP LUẬT\n'+text;
    else if(s.ready)text+=s.llm_ready?'\nAWS Nova Micro: có phiên đăng nhập':'\nCần đăng nhập AWS legalqa-w4';
    if(evaluating)text+=`\nRerank ablation: ${s.evaluation_progress||0}/200`;
    if(s.evaluation==='failed')text+='\nĐánh giá lỗi: '+s.evaluation_error;
    if(s.last_error)text+=' · '+s.last_error;
    $('runtime-status').textContent=text;if(s.evaluation==='complete')loadEvaluation();
  }catch{ready=false;$('runtime-status').textContent='Không kết nối được demo.';}
  updateControls();
}
async function loadEvaluation(){
  try{const d=await api('/api/evaluation');if(d.status!=='complete')return;
    const root=$('evaluation-results');root.replaceChildren(el('p','','Nhãn căn cứ chính đang chờ rà soát. Dev gồm pilot; điểm tạm thời, không phải test độc lập.'));
    function table(title,rows,mrr){root.append(el('h4','',title));const t=el('table'),h=el('tr');['Phương pháp','Recall@5','MRR@'+mrr].forEach(x=>h.append(el('th','',x)));t.append(h);
      Object.entries(rows).forEach(([name,v])=>{const r=el('tr');[name,(100*v['recall@5']).toFixed(1)+'%',v['mrr@'+mrr].toFixed(3)].forEach(x=>r.append(el('td','',x)));t.append(r);});root.append(t);}
    table('W3 · Dense baseline / 100 QA',{Dense:d.w3_dense_100},50);table('W4 · Retrieval / 150 QA',d.w4_retrieval_150,50);
    table('W5 · Rerank ablation / 200 QA',{'Không CrossEncoder':d.w5_rerank_200.w5_without_ce,'Có CrossEncoder':d.w5_rerank_200.w5_with_ce},5);
    root.append(el('p','','CrossEncoder thêm trung bình '+(d.ce_added_latency_mean_ms/1000).toFixed(2)+' giây/câu trên máy này. Không gọi LLM khi đo.'));
  }catch{}
}
$('evaluation-button').onclick=async()=>{if(!ready||busy||evaluating)return;
  try{await api('/api/evaluate',{method:'POST'});toast('Đã bắt đầu đánh giá 200 QA; không gọi LLM.');pollStatus();}catch(e){toast(e.message);}};
async function restoreSession(){
  try{const sessions=await loadSessions(),saved=Number(localStorage.getItem(SESSION_KEY));
    if(sessions.some(s=>s.id===saved))await openSession(saved);
    else if(sessions.length)await openSession(sessions[0].id);
    else await newSession();
  }catch(e){toast('Chưa tải được lịch sử: '+e.message);}
}
setInterval(pollStatus,5000);pollStatus();loadEvaluation();restoreSession();
