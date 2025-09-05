from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import os, pathlib
from src.predictive_core.core import PredictiveCore
from src.narrative_layer.writer import fallback_markdown

load_dotenv()
app = Flask(__name__, static_folder="frontend/static", static_url_path="/static")
core = PredictiveCore(cfg={})

@app.get("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.post("/v1/inquiries")
def inquiries():
    data = request.get_json() or {}
    inquiry = data.get("inquiry","").strip()
    if not inquiry:
        return jsonify({"error":"inquiry is required"}), 400
    return jsonify({"inquiry": inquiry})

@app.post("/v1/calculate")
def calculate():
    data = request.get_json() or {}
    inquiry = data.get("inquiry","").strip()
    if not inquiry:
        return jsonify({"error":"inquiry is required"}), 400
    result = core.calculate(inquiry)
    return jsonify(result), 200

@app.post("/v1/write")
def write_report():
    data = request.get_json() or {}
    inquiry = data.get("inquiry","").strip()
    if not inquiry:
        return jsonify({"error":"inquiry is required"}), 400
    calc = core.calculate(inquiry)
    md = fallback_markdown(calc)
    return jsonify({"narrative_md": md, "calculation": calc}), 200

@app.post("/v1/publish")
def publish():
    data = request.get_json() or {}
    title = data.get("title","Untitled")
    narrative_md = data.get("narrative_md","")
    return jsonify({"post_url": "/example-post"}), 200

@app.post("/v1/tts")
def tts():
    data = request.get_json() or {}
    text = data.get("text","").strip()
    if not text:
        return jsonify({"error":"text is required"}), 400
    audio_dir = pathlib.Path(app.static_folder) / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    (audio_dir / "sample.mp3").write_bytes(b"")  # placeholder
    return jsonify({"audio_url": "/static/audio/sample.mp3"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=True)
