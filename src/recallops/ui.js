let runId;
const output=document.querySelector('#output'),status=document.querySelector('#status');
async function call(path,options={}){const r=await fetch(path,{headers:{'Content-Type':'application/json'},...options});const data=await r.json();output.textContent=JSON.stringify(data,null,2);status.textContent=`HTTP ${r.status}: ${data.status||data.error||'ok'}`;status.className=r.ok?'ok':'bad';return {r,data}}
document.querySelector('#create').onclick=async()=>{const {r,data}=await call('/api/runs',{method:'POST',body:JSON.stringify({event_text:document.querySelector('#event').value})});if(r.ok){runId=data.run_id;document.querySelector('#approve').disabled=false}};
document.querySelector('#approve').onclick=async()=>{const {r}=await call(`/api/runs/${runId}/approve`,{method:'POST'});if(r.ok)document.querySelector('#execute').disabled=false};
document.querySelector('#execute').onclick=async()=>{const {data}=await call(`/api/runs/${runId}/execute?fail_once=1`,{method:'POST'});if(data.recoverable)document.querySelector('#resume').disabled=false};
document.querySelector('#resume').onclick=()=>call(`/api/runs/${runId}/resume`,{method:'POST'});
