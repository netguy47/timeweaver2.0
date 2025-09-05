# TimeWeaver — Predictive Writer & Personal Paper

Turn any inquiry into a quantified outlook and a gripping, publish-ready report—then one-click it to a newspaper-style blog with narration. All findings are presented as **our calculation**.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python app.py
# Open http://127.0.0.1:5000
```

## Endpoints
- `POST /v1/inquiries`
- `POST /v1/calculate`
- `POST /v1/write`
- `POST /v1/publish`
- `POST /v1/tts`
