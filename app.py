# app.py
from __future__ import annotations
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import os, json, time, pathlib, requests

# --- load env & app ---
load_dotenv()
app = Flask(
    __name__,
    static_folder="frontend/static",
    template_folder="frontend",
)

# --- storage dirs ---
DATA_DIR = pathlib.Path("data")
MEDIA_DIR = pathlib.Path("frontend/static/audio")
BLOG_DIR = pathlib.Path("data/blog")
for d in (DATA_DIR, MEDIA_DIR, BLOG_DIR):
    d.mkdir(parents=True, exist_ok=True)

# --- tiny json db ---
DB_PATH = DATA_DIR / "db.json"
if not DB_PATH.exists():
    DB_PATH.write_text(json.dumps({"inquiries": [], "reports": [], "posts": []}, indent=2), encoding="utf-8")

def _db_load():
    return json.loads(DB_PATH.read_text(encoding="utf-8"))

def _db_save(db):
    DB_PATH.write_text(json.dumps(db, indent=2), encoding="utf-8")


# --- core engine stubs you already have ---
from src.predictive_core.core import PredictiveCore
from src.narrative_layer.writer import render_report_markdown
core = PredictiveCore()


# ------------------ PAGES ------------------

@app.get("/")
def index():
    # serve the SPA from /frontend
    return send_from_directory("frontend", "index.html")

@app.get("/blog")
def blog_index():
    # list of posts with link back home
    db = _db_load()
    posts = db.get("posts", [])
    posts_sorted = sorted(posts, key=lambda x: x.get("created_at", 0), reverse=True)
    items = []
    for p in posts_sorted:
        ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(p["created_at"]))
        items.append(f"<li><a href='/blog/{p['slug']}'>{p['title']}</a> <small class='muted'>({ts})</small></li>")
    html = f"""
    <html>
      <head>
        <meta charset='utf-8' />
        <title>Personal Paper</title>
        <link rel='stylesheet' href='/static/css/style.css' />
        <link rel='icon' href='/static/favicon.ico'>
      </head>
      <body class='page'>
        <main class='container'>
          <section class='card'>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <h1 style="margin:0">Personal Paper</h1>
              <a class="btn" href="/" rel="noopener">Home</a>
            </div>
            <div class="hr"></div>
            <ul>
              {''.join(items) if items else "<li class='muted'>(no posts yet)</li>"}
            </ul>
          </section>
        </main>
      </body>
    </html>
    """
    return html

@app.get("/blog/<slug>")
def blog_item(slug):
    path = BLOG_DIR / f"{slug}.md"
    if not path.exists():
        return "Not found", 404
    body = path.read_text(encoding="utf-8")
    html = (
        "<html><head><meta charset='utf-8'><title>Personal Paper</title>"
        "<link rel='stylesheet' href='/static/css/style.css' />"
        "<link rel='icon' href='/static/favicon.ico'></head>"
        "<body class='page'><main class='container'>"
        "<section class='card'>"
        "<div style='display:flex;justify-content:space-between;align-items:center'>"
        "<a class='btn' href='/blog'>All Posts</a>"
        "<a class='btn' href='/' rel='noopener'>Home</a>"
        "</div>"
        "<div class='hr'></div>"
        "<pre style='white-space:pre-wrap'>"
        + body +
        "</pre></section></main></body></html>"
    )
    return html


# ------------------ API: INQUIRIES ------------------

@app.post("/v1/inquiries")
def save_inquiry():
    data = request.get_json() or {}
    inquiry = (data.get("inquiry") or "").strip()
    if not inquiry:
        return jsonify({"error": "inquiry is required"}), 400
    db = _db_load()
    rec = {"id": int(time.time()*1000), "inquiry": inquiry, "created_at": int(time.time())}
    db.setdefault("inquiries", []).append(rec)
    _db_save(db)
    return jsonify(rec), 200

@app.get("/v1/inquiries")
def list_inquiries():
    db = _db_load()
    return jsonify(db.get("inquiries", [])[-200:]), 200


# ------------------ API: CALCULATE / WRITE ------------------

@app.post("/v1/calculate")
def calculate():
    data = request.get_json() or {}
    inquiry = (data.get("inquiry") or "").strip()
    if not inquiry:
        return jsonify({"error": "inquiry is required"}), 400
    calc = core.calculate(inquiry)
    return jsonify(calc), 200

@app.post("/v1/write")
def write_report():
    data = request.get_json() or {}
    calc = data.get("calculation") or {}
    length = (data.get("length") or "standard").lower()
    if length not in ("brief", "standard", "deep"):
        length = "standard"
    md = render_report_markdown(calc, length=length)

    db = _db_load()
    rec = {
        "id": int(time.time()*1000),
        "inquiry": calc.get("inquiry"),
        "length": length,
        "narrative_md": md,
        "created_at": int(time.time()),
    }
    db.setdefault("reports", []).append(rec)
    _db_save(db)
    return jsonify(rec), 200


# ------------------ API: IMAGE PROMPTS ------------------

@app.post("/v1/image_prompts")
def image_prompts():
    data = request.get_json() or {}
    calc = data.get("calculation") or {}
    inquiry = calc.get("inquiry") or "Subject"
    drivers = calc.get("drivers", [])
    scenarios = calc.get("scenarios", [])
    prompts = []

    top_factors = ", ".join(d.get("factor","") for d in drivers[:3]) or "key operational drivers"
    top_scenario = (scenarios[0].get("name") + ": " + scenarios[0].get("thesis")) if scenarios else "primary scenario"

    prompts.append(
        f"Photorealistic briefing illustration: secure situation room, orbital overlays, "
        f"labels for {top_factors}; cinematic rim lighting, neutral reportage tone."
    )
    prompts.append(
        f"Technical cutaway: repurposed stealth destroyer as expedition platform, modular bays, "
        f"service drones, blueprint aesthetic with realistic annotations."
    )
    prompts.append(
        f"Operational concept board: {top_scenario}. Three panels (logistics, protection, revenue), "
        f"clean infoviz, muted palette, no logos."
    )
    prompts.append(
        f"Press-ready feature image: expeditionary unit embarkation at dawn, silhouettes, equipment detail, "
        f"long-lens compression, documentary realism."
    )

    return jsonify({"prompts": prompts[:5]}), 200


# ------------------ API: STOCK IMAGES (Unsplash) ------------------

@app.post("/v1/images")
def stock_images():
    """
    Fetch relevant stock images from Unsplash.
    Requires UNSPLASH_ACCESS_KEY in .env. Soft-fails to [].
    """
    data = request.get_json() or {}
    keywords = (data.get("keywords") or "analysis").strip()
    api_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not api_key:
        return jsonify({"urls": []}), 200

    try:
        r = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": keywords,
                "per_page": 8,
                "orientation": "landscape",
                "content_filter": "high",
            },
            headers={"Authorization": f"Client-ID {api_key}"},
            timeout=10,
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        urls = [it["urls"]["regular"] for it in results if "urls" in it]
        return jsonify({"urls": urls[:8]}), 200
    except Exception as e:
        return jsonify({"urls": [], "error": "IMAGE_FETCH_FAILED", "detail": str(e)}), 200


# ------------------ API: PUBLISH (with images) ------------------

@app.post("/v1/publish")
def publish():
    data = request.get_json() or {}
    report_md = (data.get("narrative_md") or "").strip()
    title = (data.get("title") or "Briefing").strip()
    images = data.get("images") or []

    if not report_md:
        return jsonify({"error": "narrative_md is required"}), 400

    ts = int(time.time())
    slug = f"{ts}-{title.lower().replace(' ', '-')[:40]}"

    md_blocks = [f"# {title}", "", report_md, ""]
    if images:
        md_blocks.append("## Related Images")
        for u in images[:8]:
            md_blocks.append(f"![related image]({u})")
        md_blocks.append("")

    (BLOG_DIR / f"{slug}.md").write_text("\n".join(md_blocks), encoding="utf-8")

    db = _db_load()
    db.setdefault("posts", []).append({"slug": slug, "title": title, "created_at": ts})
    _db_save(db)
    return jsonify({"slug": slug, "url": f"/blog/{slug}"}), 200


# ------------------ API: TTS (local pyttsx3) ------------------

@app.post("/v1/tts")
def tts():
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    voice = data.get("voice") or "default"
    if not text:
        return jsonify({"error": "text is required"}), 400

    try:
        import pyttsx3
        engine = pyttsx3.init()
        if voice and voice != "default":
            for v in engine.getProperty("voices"):
                if voice.lower() in (v.name or "").lower():
                    engine.setProperty("voice", v.id)
                    break
        out = MEDIA_DIR / f"tts_{int(time.time())}.wav"
        engine.save_to_file(text, str(out))
        engine.runAndWait()
        return jsonify({"audio_url": f"/static/audio/{out.name}", "format": "wav"}), 200
    except Exception as e:
        return jsonify({"error": "TTS_FAILED", "detail": str(e)}), 500


# ------------------ STATIC ------------------

@app.get("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("frontend/static", filename)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
