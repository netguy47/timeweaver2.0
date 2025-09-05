from pathlib import Path
import json

def render_prompt(calculation: dict) -> str:
    template = Path(__file__).parent.joinpath("prompts", "writer_en.md").read_text(encoding="utf-8")
    return template.replace("{{calculation_json}}", json.dumps(calculation, ensure_ascii=False, indent=2))

def fallback_markdown(calculation: dict) -> str:
    p = round(calculation["probability"]*100)
    lo = round(calculation["band"][0]*100)
    hi = round(calculation["band"][1]*100)
    drivers = calculation.get("drivers", [])
    scenarios = calculation.get("scenarios", [])[:4]
    drivers_md = "\n".join([f"- {d.get('factor','Driver')} ({d.get('direction','+')}); weight ~{int(100*d.get('weight',0.2))}%"
                             for d in drivers])
    scen_md = "\n".join([f"**{s.get('name','Scenario')}** — {int(100*s.get('likelihood',0.25))}%: {s.get('thesis','Plausible path.')}\nTripwires: {', '.join(s.get('tripwires', []))}"
                           for s in scenarios])
    return f"""## Executive Summary
Our calculation estimates a {p}% likelihood (uncertainty band {lo}–{hi}%).

## Definitions
Precisely define the key terms, actors, and timeframe.

## Our Calculation
Top drivers:\n{drivers_md}

## Scenarios
{scen_md}

## What to Watch Next
- Indicator A
- Indicator B
- Indicator C
"""
