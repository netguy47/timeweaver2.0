async function runCalc(){
  const inquiry = document.getElementById('inquiry').value.trim();
  const res = await fetch('/v1/calculate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({inquiry})});
  const data = await res.json();
  const out = document.getElementById('outcome');
  const p = Math.round((data.probability||0)*100);
  const lo = Math.round((data.band?.[0]||0)*100);
  const hi = Math.round((data.band?.[1]||0)*100);
  out.innerHTML = `<div class="outcome">${p}%</div><div class="badge">Band ${lo}–${hi}%</div>`;
  document.getElementById('report').textContent = data.narrative || '';
  window._lastNarrative = data.narrative || '';
}
async function makeTTS(){
  const text = window._lastNarrative || document.getElementById('report').textContent;
  const res = await fetch('/v1/tts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text,voice:'narrator',language:'en'})});
  const data = await res.json();
  if(data.audio_url){
    const audio = document.getElementById('audio');
    audio.src = data.audio_url; audio.style.display='block';
  }
}
