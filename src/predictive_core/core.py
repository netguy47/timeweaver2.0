from __future__ import annotations
from typing import Dict, Any, List
import random

class PredictiveCore:
    """One-facade predictive engine. Public result = our calculation."""
    def __init__(self, cfg: dict | None = None):
        self.cfg = cfg or {}

    def calculate(self, inquiry: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        corpus = self._ingest(inquiry, context or {})
        feats  = self._normalize(corpus)
        local  = self._local_patterns(feats)
        global_ = self._global_context(feats)
        scenarios = self._sample_scenarios(feats)
        fused = self._fuse_predictions(local, global_, scenarios)
        calibrated = self._calibrate_uncertainty(fused)
        narrative = self._write_report(inquiry, calibrated, corpus)
        evidence  = self._build_evidence(corpus, calibrated)
        return {
            "probability": calibrated["p"],
            "band": calibrated["band"],
            "drivers": calibrated["drivers"],
            "scenarios": calibrated["scenarios"],
            "narrative": narrative,
            "evidence": evidence
        }

    # --- private stubs ---
    def _ingest(self, inquiry: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"inquiry": inquiry, "signals": [], "context": context}

    def _normalize(self, corpus: Dict[str, Any]) -> Dict[str, Any]:
        return {"features": {"len": len(corpus.get("inquiry",""))}}

    def _local_patterns(self, feats: Dict[str, Any]) -> float:
        return random.uniform(0.45, 0.60)

    def _global_context(self, feats: Dict[str, Any]) -> float:
        return random.uniform(0.50, 0.65)

    def _sample_scenarios(self, feats: Dict[str, Any]) -> List[Dict[str, Any]]:
        base = [0.42, 0.35, 0.23]
        names = ["Status Quo Drifts","Shock & Realign","Dark Horse Surge"]
        return [{"name": n, "likelihood": p, "thesis": "Plausible trajectory.", "tripwires": ["Signal A","Signal B"]}
                for n,p in zip(names, base)]

    def _fuse_predictions(self, local: float, global_: float, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        p = 0.5*local + 0.5*global_
        drivers = [
            {"factor": "Momentum", "direction": "+", "weight": 0.26},
            {"factor": "Approval", "direction": "+", "weight": 0.21},
            {"factor": "Macro Sentiment", "direction": "-", "weight": 0.17},
        ]
        return {"p": p, "drivers": drivers, "scenarios": scenarios}

    def _calibrate_uncertainty(self, fused: Dict[str, Any]) -> Dict[str, Any]:
        p = fused["p"]
        band = (max(0.0, p-0.07), min(1.0, p+0.06))
        return {"p": p, "band": band, "drivers": fused["drivers"], "scenarios": fused["scenarios"]}

    def _write_report(self, inquiry: str, calc: Dict[str, Any], corpus: Dict[str, Any]) -> str:
        p = round(calc["p"]*100)
        lo, hi = calc["band"]
        lo, hi = round(lo*100), round(hi*100)
        drivers_md = "\n".join([f"- {d['factor']} ({'↑' if d['direction']=='+' else '↓'}; weight {int(d['weight']*100)}%)" for d in calc["drivers"]])
        scen_md = "\n".join([f"**{s['name']}** — {int(s['likelihood']*100)}%: {s['thesis']}. Tripwires: {', '.join(s['tripwires'])}"
                              for s in calc["scenarios"]])
        return f"""# {inquiry}

**Our calculation:** {p}% likelihood (uncertainty band {lo}–{hi}%).

## Why this matters (context)
One paragraph framing tied to names, dates, and stakes.

## Top drivers
{drivers_md}

## Plausible scenarios
{scen_md}

## What to watch next
- Concrete indicator one
- Concrete indicator two
- Concrete indicator three
"""

    def _build_evidence(self, corpus: Dict[str, Any], calc: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {"title":"Example Source","date":"2025-09-01","type":"news","trust":0.7,"recency_days":4,"summary":"Why this matters.","link":"https://example.com"}
        ]
