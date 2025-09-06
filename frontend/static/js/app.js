/* TimeWeaver UX glue
   - Run briefing (calculate → write)
   - TTS audio
   - Visual prompts + local library
   - Save inquiries + list history
   - Publish to Personal Paper (with images)
   - Relevant stock images (Unsplash)
*/
const $ = sel => document.querySelector(sel);

let LAST_CALC = null;
let LAST_REPORT = null; // { id, inquiry, narrative_md, length, created_at }
let LAST_PROMPTS = [];
window.__lastImageURLs = [];

// -------------- helpers --------------
async function postJSON(url, body){
  const r = await fetch(url, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(body || {})
  });
  const data = await r.json().catch(()=> ({}));
  if(!r.ok){ throw new Error(data.error || r.statusText); }
  return data;
}
function mdToDisplay(md){
  return md || "(no narrative)";
}
function setOutcome(calc){
  if(!calc){ $("#outcome").textContent = "(no calculation)"; return; }
  const pct = Math.round(calc.probability*100);
  const lo  = Math.round(calc.band[0]*100);
  const hi  = Math.round(calc.band[1]*100);
  $("#outcome").textContent = `${pct}%\nBand ${lo}–${hi}%`;
  $("#confidence").textContent = calc.confidence ? `Confidence: ${calc.confidence}` : "";
}

// -------------- core flows --------------
async function runBriefing(){
  const inquiry = ($("#inquiry").value || "").trim();
  if(!inquiry){ alert("Please enter an inquiry."); return; }
  const length = $("#length").value || "standard";

  try{
    // calculate
    const calc = await postJSON("/v1/calculate", { inquiry });
    LAST_CALC = { ...calc, inquiry };
    setOutcome(calc);

    // write
    const report = await postJSON("/v1/write", { calculation: LAST_CALC, length });
    LAST_REPORT = report;
    $("#report").textContent = mdToDisplay(report.narrative_md);
    $("#audio").style.display = "none"; // reset audio

    // fetch relevant stock images
    try {
      const driverWords = (LAST_CALC?.drivers || [])
        .slice(0, 3)
        .map(d => (d.factor || "").toString())
        .join(" ");
      const keywords = `${inquiry} ${driverWords}`.replace(/\s+/g, " ").trim().slice(0, 120);
      await fetchImages(keywords || "analysis briefing");
    } catch (e) {
      console.error(e);
      renderImages([]);
    }
  }catch(e){
    console.error(e);
    alert("Briefing failed: " + e.message);
  }
}

// -------------- TTS --------------
async function generateTTS(){
  const md = LAST_REPORT?.narrative_md || "";
  if(!md){ alert("No narrative to narrate. Run a briefing first."); return; }
  try{
    const res = await postJSON("/v1/tts", { text: md, voice: "narrator" });
    const audio = $("#audio");
    audio.src = res.audio_url;
    audio.style.display = "block";
    audio.play().catch(()=>{ /* autoplay might be blocked */ });
  }catch(e){
    console.error(e);
    alert("TTS failed: " + e.message);
  }
}

// -------------- Images: fetch + render --------------
async function fetchImages(keywords) {
  try {
    const res = await fetch("/v1/images", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ keywords })
    });
    const data = await res.json();
    window.__lastImageURLs = data.urls || [];
    renderImages(window.__lastImageURLs);
  } catch (e) {
    console.error(e);
    window.__lastImageURLs = [];
    renderImages([]);
  }
}
function renderImages(urls) {
  const wrap = document.getElementById("images");
  if (!wrap) return;
  wrap.innerHTML = "";
  if (!urls.length) {
    wrap.innerHTML = `<div class="muted">(no images found)</div>`;
    return;
  }
  urls.forEach(url => {
    const img = document.createElement("img");
    img.src = url;
    img.alt = "Briefing-related image";
    img.className = "img-thumb";
    img.addEventListener("click", () => window.open(url, "_blank"));
    wrap.appendChild(img);
  });
}

// -------------- Image prompts + library --------------
function loadPromptLibrary(){
  try{
    const arr = JSON.parse(localStorage.getItem("tw_prompt_library")||"[]");
    return Array.isArray(arr)? arr : [];
  }catch{ return []; }
}
function savePromptLibrary(arr){
  localStorage.setItem("tw_prompt_library", JSON.stringify(arr));
}
function renderPromptLibrary(){
  const lib = loadPromptLibrary();
  const box = $("#promptLibrary");
  box.innerHTML = "";
  if(lib.length===0){ box.textContent="(empty)"; return; }
  lib.slice().reverse().forEach(item=>{
    const div = document.createElement("div");
    div.className = "pill";
    div.style.whiteSpace = "pre-wrap";
    div.textContent = `• ${item.prompt}`;
    box.appendChild(div);
  });
}
async function generatePrompts(){
  if(!LAST_CALC){ alert("Run a briefing first (so we know the drivers/scenarios)."); return; }
  try{
    const res = await postJSON("/v1/image_prompts", { calculation: LAST_CALC });
    LAST_PROMPTS = res.prompts || [];
    const box = $("#prompts");
    box.innerHTML = "";
    if(LAST_PROMPTS.length===0){ box.textContent="(no prompts)"; return; }
    LAST_PROMPTS.forEach(p=>{
      const div = document.createElement("div");
      div.className = "pill";
      div.style.whiteSpace = "pre-wrap";
      div.textContent = p;
      box.appendChild(div);
    });
    const lib = loadPromptLibrary();
    LAST_PROMPTS.forEach(p=> lib.push({ prompt:p, ts: Date.now(), inquiry: LAST_CALC?.inquiry||"" }));
    savePromptLibrary(lib);
    renderPromptLibrary();
  }catch(e){
    console.error(e);
    alert("Prompt generation failed: " + e.message);
  }
}

// -------------- Save inquiries & history --------------
async function saveInquiry(){
  const inquiry = ($("#inquiry").value || "").trim();
  if(!inquiry){ alert("Enter an inquiry first."); return; }
  try{
    await postJSON("/v1/inquiries", { inquiry });
    await refreshHistory();
  }catch(e){
    console.error(e);
    alert("Failed to save inquiry: " + e.message);
  }
}
async function refreshHistory(){
  try{
    const r = await fetch("/v1/inquiries");
    const arr = await r.json();
    const box = $("#history");
    box.innerHTML = "";
    if(!Array.isArray(arr) || arr.length===0){ box.textContent = "(none)"; return; }
    arr.slice().reverse().forEach(it=>{
      const d = new Date(it.created_at*1000).toLocaleString();
      const row = document.createElement("div");
      row.className = "pill";
      row.style.whiteSpace = "pre-wrap";
      row.textContent = `${d} — ${it.inquiry}`;
      row.onclick = ()=> { $("#inquiry").value = it.inquiry; };
      box.appendChild(row);
    });
  }catch(e){
    console.error(e);
  }
}

// -------------- Publish --------------
async function publish(){
  if(!LAST_REPORT?.narrative_md){
    alert("Nothing to publish yet. Run a briefing first.");
    return;
  }
  const title = prompt("Post title:", (LAST_CALC?.inquiry || "Briefing").slice(0,80));
  if(!title){ return; }
  try{
    const res = await postJSON("/v1/publish", {
      title,
      narrative_md: LAST_REPORT.narrative_md,
      images: window.__lastImageURLs || [] // include images in blog post
    });
    alert("Published! Opening your Personal Paper post…");
    window.open(res.url, "_blank");
  }catch(e){
    console.error(e);
    alert("Publish failed: " + e.message);
  }
}

// -------------- boot --------------
window.addEventListener("DOMContentLoaded", ()=>{
  renderPromptLibrary();
  refreshHistory();
});
