const $ = s => document.querySelector(s);
const form = $('form'), title = $('#title'), createButton = form.querySelector('button');
const ambiguous = location.pathname === '/ambiguous';
if (ambiguous) {
  $('#create-section > p').textContent = 'Choose one option to continue.';
  $('fieldset').innerHTML = '<legend>Completion setting</legend><label class="choice"><input type="radio" name="policy" value="direct">Core</label><label class="choice"><input type="radio" name="policy" value="approval">Required</label>';
}
form.addEventListener('change', () => { createButton.disabled = !form.querySelector('input:checked'); });
title.addEventListener('input', () => { if (title.value.trim() && title.value.trim().length <= 80) { $('#title-error').textContent = ''; title.removeAttribute('aria-invalid'); } });
let taskViews = [];
$('#actor').addEventListener('change', () => { $('#action-error').textContent = ''; $('#notice').textContent = `Acting as ${$('#actor').value}.`; drawTasks(); });
async function api(path, body) {
  const response = await fetch('/api/tasks' + path, body ? { method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify(body) } : {});
  const result = await response.json(); if (!response.ok) throw new Error(result.error.message); return result;
}
function el(tag, text, parent, attrs={}) { const n=document.createElement(tag); n.textContent=text; for (const [k,v] of Object.entries(attrs)) n.setAttribute(k,v); parent.append(n); return n; }
async function render(focusId) {
  const {tasks}=await api('');
  taskViews = await Promise.all(tasks.map(async task => ({ task, events: (await api(`/${task.id}/events`)).events })));
  drawTasks(focusId);
}
function drawTasks(focusId) {
  const container=$('#tasks'); container.replaceChildren();
  for (const {task, events} of taskViews) {
    const article=el('article','',container,{'aria-label':task.title});
    const heading=el('h2',task.title,article,{tabindex:'-1'});
    el('p',`Task ${task.id} · Created by ${task.creator}`,article,{class:'meta'});
    el('p',task.policy==='approval'?"Require another person's approval":'Complete directly',article);
    el('p',task.status==='open'?'Open':task.status==='complete'?'Complete':`Waiting for ${task.completedBy==='Alex'?'Sam':'Alex'}'s approval`,article,{class:'status','data-testid':'task-status'});
    if(task.status!=='complete') {
      const action=task.status==='open'?'complete':'approve';
      const canApprove = task.completedBy !== $('#actor').value;
      if(action==='approve') el('p',`Completion requested by ${task.completedBy}. ${canApprove ? 'You can approve this completion.' : `Switch “Acting as” to ${task.completedBy==='Alex'?'Sam':'Alex'} to approve.`}`,article);
      if(action==='complete' || canApprove) {
      const button=el('button',action==='complete'?'Request completion':'Approve completion',article,{type:'button'});
      button.onclick=async()=>{button.disabled=true;$('#action-error').textContent='';try{await api(`/${task.id}/${action}`,{actor:$('#actor').value});await render(task.id);}catch(e){$('#action-error').textContent=e.message;button.disabled=false;}};
      }
    }
    el('h3','History',article); const list=el('ol','',article);
    const labels={'task.created':'Created by','task.completion_requested':'Completion requested by','task.approved':'Approved by','task.completed':'Completed by'};
    for(const event of events){const li=el('li',`${labels[event.type]} ${event.actor}`,list);el('time',event.occurredAt,li,{datetime:event.occurredAt});}
    if(focusId===task.id) heading.focus();
  }
}
form.onsubmit=async e=>{e.preventDefault();const policy=form.querySelector('input:checked')?.value;if(!policy)return;createButton.disabled=true;$('#title-error').textContent='';title.removeAttribute('aria-invalid');try{const {task}=await api('',{title:title.value,creator:$('#actor').value,policy});$('#notice').textContent='Task created.';await render(task.id);title.value='';}catch(e){$('#title-error').textContent=e.message;title.setAttribute('aria-invalid','true');title.focus();}finally{createButton.disabled=false;}};
render().catch(e=>{$('#action-error').textContent=e.message;});
