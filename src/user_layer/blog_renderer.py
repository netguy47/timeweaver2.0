from datetime import datetime

def render_post_html(title: str, narrative_md: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><link rel="stylesheet" href="/static/css/style.css"></head>
<body class="page"><main class="container">
<header><h1>{title}</h1><p>{datetime.utcnow().isoformat()}Z</p></header>
<article>{narrative_md}</article>
</main></body></html>"""
