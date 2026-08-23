const sliders = ["air_temperature_k","process_temperature_k","rotational_speed_rpm","torque_nm","tool_wear_min"];
const units = {air_temperature_k:"K",process_temperature_k:"K",rotational_speed_rpm:"RPM",torque_nm:"Nm",tool_wear_min:"min"};
let chatMessages = [];
let chatContext = null;
let lastSensorData = null;

sliders.forEach(id=>{
  const rangeEl = document.getElementById(id);
  const numEl = document.getElementById(id+"_num");
  const out = numEl; // use the numeric input as the single display
  const warn = document.getElementById(id+"_warn");

  const min = parseFloat(rangeEl.min);
  const max = parseFloat(rangeEl.max);

  const renderFromRange = ()=>{
    if(numEl) numEl.value = rangeEl.value;
    if(warn) { warn.style.display = 'none'; numEl.classList && numEl.classList.remove('out-of-range'); }
  };

  const handleNumInput = ()=>{
    const v = parseFloat(numEl.value);
    if(isNaN(v)){
      if(warn) { warn.style.display = 'block'; warn.textContent = 'Invalid number'; }
      numEl.classList && numEl.classList.add('out-of-range');
      return;
    }
    // numEl already reflects the typed value
    if(v < min || v > max){
      if(warn) { warn.style.display = 'block'; warn.textContent = 'Is the input correct? Value is outside normal range.'; }
      numEl.classList && numEl.classList.add('out-of-range');
    } else {
      if(warn) { warn.style.display = 'none'; }
      numEl.classList && numEl.classList.remove('out-of-range');
      rangeEl.value = numEl.value;
    }
  };

  rangeEl.addEventListener('input', renderFromRange);
  if(numEl) numEl.addEventListener('input', handleNumInput);
  renderFromRange();
});

const PRESETS = {
  normal: {air_temperature_k:298.1, process_temperature_k:308.6, rotational_speed_rpm:1551, torque_nm:42.0, tool_wear_min:90},
  twf:    {air_temperature_k:298.1, process_temperature_k:308.6, rotational_speed_rpm:1400, torque_nm:42.0, tool_wear_min:253},
  osf:    {air_temperature_k:298.1, process_temperature_k:308.6, rotational_speed_rpm:1100, torque_nm:60.0, tool_wear_min:210},
  hdf:    {air_temperature_k:298.1, process_temperature_k:304.5, rotational_speed_rpm:1320, torque_nm:38.0, tool_wear_min:60},
  pwf:    {air_temperature_k:298.1, process_temperature_k:308.6, rotational_speed_rpm:2900, torque_nm:77.0, tool_wear_min:90},
};

// Clear active class from all preset buttons
function clearPresetActive(){
  document.querySelectorAll('.preset-btn').forEach(b=>b.classList.remove('active'));
}

document.querySelectorAll(".preset-btn").forEach(btn=>{
  btn.addEventListener("click", ()=>{
    clearPresetActive();
    btn.classList.add('active');
    const p = PRESETS[btn.dataset.preset];
    sliders.forEach(id=>{
      const range = document.getElementById(id);
      const num = document.getElementById(id+"_num");
      range.value = p[id];
      if(num) num.value = p[id];
      const warn = document.getElementById(id+"_warn");
      if(warn) warn.style.display = 'none';
    });
  });
});

// When any input is changed manually, remove preset active state
sliders.forEach(id=>{
  const range = document.getElementById(id);
  const num = document.getElementById(id+"_num");
  if(range) range.addEventListener('input', clearPresetActive);
  if(num) num.addEventListener('input', clearPresetActive);
});

function readPayload(){
  const sensor_data = {};
  const machineType = document.getElementById("machineType");
  sliders.forEach(id=>{
    const num = document.getElementById(id+"_num");
    const range = document.getElementById(id);
    const v = num ? parseFloat(num.value) : parseFloat(range.value);
    sensor_data[id] = isNaN(v) ? parseFloat(range.value) : v;
  });
  sensor_data.machine_type = machineType.value;
  return {
    machine_id: document.getElementById("machineId").value || "UNKNOWN",
    sensor_data,
  };
}

function riskColorClass(status){
  return status === "Normal" ? "normal" : "failed";
}

function confidenceLabel(value){
  return `${(Number(value) * 100).toFixed(2)}`;
}

function cleanChatText(content){
  const cleaned = String(content)
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/__(.*?)__/g, "$1")
    .replace(/\*([^*\n]+)\*/g, "$1")
    .replace(/_([^_\n]+)_/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/^\s*#{1,6}\s*(.+)$/gm, "\n\n$1\n")
    .replace(/^\s*((?:summary|recommended actions|safety notes|estimated downtime|root cause)[^\n]*)$/gim, "\n\n$1\n")
    .replace(/^\s*(?:repair guidance provided by|machine id|date)\s*:?.*$/gim, "")
    .replace(/^\s*-{3,}\s*$/gm, "")
    .replace(/^\s*[-*]\s+/gm, "- ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  const lines = cleaned.split("\n");
  const formatted = [];
  let inSection = false;
  lines.forEach(line=>{
    const trimmed = line.trim();
    if(!trimmed){
      formatted.push("");
      return;
    }
    const section = trimmed.replace(/^-\s*/, "");
    if(/^[A-Za-z][^\n:]{1,80}:$/.test(section)){
      if(formatted.length && formatted[formatted.length - 1] !== "") formatted.push("");
      formatted.push(section);
      formatted.push("");
      inSection = true;
    }else if(inSection && /^-\s+/.test(trimmed)){
      formatted.push(`  ${trimmed}`);
    }else{
      formatted.push(trimmed);
    }
  });
  return formatted.join("\n").replace(/\n{3,}/g, "\n\n").trim();
}

function renderChatHistory(){
  const history = document.getElementById("chatHistory");
  if(!history) return;
  history.innerHTML = "";
  chatMessages.forEach(message=>{
    const item = document.createElement("p");
    item.className = `chat-message ${message.role}`;
    item.textContent = cleanChatText(message.content);
    history.appendChild(item);
  });
  history.scrollTop = history.scrollHeight;
}

function setChatTyping(isTyping){
  const history = document.getElementById("chatHistory");
  if(!history) return;
  const indicator = document.getElementById("chatTyping");
  if(isTyping && !indicator){
    const item = document.createElement("p");
    item.id = "chatTyping";
    item.className = "chat-message assistant typing";
    item.textContent = "AI is typing...";
    history.appendChild(item);
  } else if(!isTyping && indicator){
    indicator.remove();
  }
  history.scrollTop = history.scrollHeight;
}

function renderResult(data){
  const empty = document.getElementById("resultEmpty");
  const content = document.getElementById("resultContent");
  empty.style.display = "none";
  content.style.display = "block";

  const d = data.diagnosis;
  const g = data.repair_guidance;
  const chatInterface = document.getElementById("chatInterface");
  const chatToggle = document.getElementById("chatToggleBtn");
  if(d.status === "Failed"){
    chatContext = {
      machine_id: data.machine_id,
      diagnosis: data.diagnosis,
      additional_diagnoses: data.additional_diagnoses || [],
      repair_guidance: data.repair_guidance || null,
      sensor_data: lastSensorData,
    };
    chatMessages = [];
    renderChatHistory();
    if(chatToggle) chatToggle.style.display = "flex";
  } else if(chatInterface){
    chatInterface.classList.remove("is-open");
    chatInterface.setAttribute("aria-hidden", "true");
    if(chatToggle) chatToggle.style.display = "none";
    chatMessages = [];
    chatContext = null;
  }
  const cls = riskColorClass(d.status);
  const confidencePct = confidenceLabel(d.confidence);

  let html = `
    <div class="status-strip ${cls}">
      <div class="status-ring">${d.status === "Normal" ? "OK" : d.failure_mode}</div>
      <div class="status-text">
        <p class="machine">MACHINE ${data.machine_id}</p>
        <p class="headline">${d.status === "Normal" ? "Normal condition" : (d.failure_mode_label || "Detected issue")}</p>
        <p class="sub">Model confidence: ${confidencePct}% · Risk level: ${d.risk_level}</p>
      </div>
    </div>

  `;

  if (g) {
    html += `
      <p class="section-title">Root cause</p>
      <div class="prose"><p>${g.root_cause}</p></div>

      <p class="section-title">Repair steps</p>
      <ul class="steps">
        ${g.recommended_actions.map(a=>`<li>${a}</li>`).join("")}
      </ul>

      <p class="section-title">Safety notes</p>
      <div class="safety-box">
        ${g.safety_notes.map(s=>`<p>⚠ ${s}</p>`).join("")}
      </div>

      ${g.estimated_downtime_minutes ? `<p class="section-title">Estimated downtime</p><div class="prose"><p>${g.estimated_downtime_minutes} minutes</p></div>` : ""}
    `;
  }

  const remaining = data.additional_diagnoses || [];
  if(remaining.length){
    html += `
      <p class="section-title">Other possible failure modes</p>
      <div class="diagnosis-list">
        ${remaining.map(item=>`
          <div class="diagnosis-item possible-diagnosis-card">
            <div class="possible-mode-ring">${item.failure_mode}</div>
            <div class="diagnosis-info">
              <div class="diagnosis-name">${item.failure_mode_label || item.failure_mode}</div>
              <div class="diagnosis-confidence">Model confidence: ${confidenceLabel(item.confidence)}%</div>
            </div>
          </div>
        `).join("")}
      </div>
    `;
  }

  content.innerHTML = html;
}

function renderError(message){
  const empty = document.getElementById("resultEmpty");
  const content = document.getElementById("resultContent");
  empty.style.display = "none";
  content.style.display = "block";
  content.innerHTML = `<div class="err-box">Failed to fetch diagnosis: ${message}</div>`;
}

document.getElementById("runBtn").addEventListener("click", async ()=>{
  const btn = document.getElementById("runBtn");
  const endpoint = "http://localhost:8000/api/v1/predict";
  btn.disabled = true;
  btn.textContent = "Processing...";

  try {
    const payload = readPayload();
    lastSensorData = payload.sensor_data;
    const res = await fetch(endpoint, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload),
    });
    if(!res.ok){
      const errData = await res.json().catch(()=>({detail:res.statusText}));
      throw new Error(errData.detail || res.statusText);
    }
    const data = await res.json();
    renderResult(data);
  } catch(err){
    renderError(err.message || String(err));
  } finally {
    btn.disabled = false;
    btn.textContent = "Run diagnosis";
  }
});

document.getElementById("sendChatBtn").addEventListener("click", async ()=>{
  const input = document.getElementById("chatInput");
  const button = document.getElementById("sendChatBtn");
  const content = input.value.trim();
  if(!content || button.disabled) return;

  chatMessages.push({role: "user", content});
  input.value = "";
  renderChatHistory();
  setChatTyping(true);
  button.disabled = true;

  try{
    const response = await fetch("http://localhost:8000/api/v1/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        messages: [
          {
            role: "system",
            content: "Use this diagnosis JSON as the context for the technician's questions:\n" + JSON.stringify(chatContext),
          },
          ...chatMessages,
        ],
      }),
    });
    if(!response.ok){
      const errorData = await response.json().catch(()=>({detail: response.statusText}));
      throw new Error(errorData.detail || response.statusText);
    }
    const data = await response.json();
    chatMessages.push({role: "assistant", content: data.reply});
    setChatTyping(false);
    renderChatHistory();
  }catch(error){
    setChatTyping(false);
    const errorItem = document.createElement("p");
    errorItem.className = "chat-error";
    errorItem.textContent = `Chat unavailable: ${error.message || String(error)}`;
    document.getElementById("chatHistory").appendChild(errorItem);
  }finally{
    button.disabled = false;
    input.focus();
  }
});

document.getElementById("chatToggleBtn").addEventListener("click", ()=>{
  const chatInterface = document.getElementById("chatInterface");
  chatInterface.classList.add("is-open");
  chatInterface.setAttribute("aria-hidden", "false");
  generateDiagnosticReport();
});

async function generateDiagnosticReport(){
  const history = document.getElementById("chatHistory");
  const button = document.getElementById("sendChatBtn");
  if(!history || !chatContext || chatMessages.length || button.disabled) return;

  setChatTyping(true);
  button.disabled = true;
  try{
    const response = await fetch("http://localhost:8000/api/v1/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({messages: [
        {
          role: "system",
          content: "You are an expert factory maintenance engineer. Use this machine detection report and sensor JSON as authoritative context:\n" + JSON.stringify(chatContext),
        },
        {
          role: "user",
          content: "Generate a comprehensive diagnostic report with these exact sections: Root Cause Analysis, Machine Variant Context, Repair SOP, and Prevention. Keep Root Cause Analysis and Machine Variant Context concise and readable as paragraphs when appropriate. You may and should use numbered or bulleted lists for Repair SOP, especially for step-by-step actions, and for Prevention, especially for preventive measures. Put each list item on its own line. Keep the advice practical and safety-focused. Do not include author attribution, a date, a separate machine ID header, or horizontal separator lines.",
        },
      ]}),
    });
    if(!response.ok){
      const errorData = await response.json().catch(()=>({detail: response.statusText}));
      throw new Error(errorData.detail || response.statusText);
    }
    const data = await response.json();
    chatMessages.push({role: "assistant", content: data.reply});
    setChatTyping(false);
    renderChatHistory();
  }catch(error){
    setChatTyping(false);
    const errorItem = document.createElement("p");
    errorItem.className = "chat-error";
    errorItem.textContent = `Report unavailable: ${error.message || String(error)}`;
    history.appendChild(errorItem);
  }finally{
    button.disabled = false;
    document.getElementById("chatInput").focus();
  }
}

document.getElementById("closeChatBtn").addEventListener("click", ()=>{
  const chatInterface = document.getElementById("chatInterface");
  chatInterface.classList.remove("is-open");
  chatInterface.setAttribute("aria-hidden", "true");
});

