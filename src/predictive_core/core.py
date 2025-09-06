from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import math, random, time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEBUG_MODE = True

@dataclass
class Driver:
    name: str
    direction: str
    weight: float
    rationale: str

@dataclass
class Scenario:
    name: str
    likelihood: float
    thesis: str
    tripwires: List[str]

class PredictiveCore:
    def calculate(self, inquiry: str) -> Dict[str, Any]:
        if not inquiry.strip():
            logger.warning("Calculate called with empty inquiry - returning empty calc")
            return {}
        seed = abs(hash(inquiry)) % (2**32)
        rng = random.Random(seed)
        base = 0.55 + 0.15 * (rng.random() - 0.5)
        base = max(0.15, min(0.85, base))
        spread = 0.07 + 0.04 * rng.random()
        band_low = max(0.05, base - spread)
        band_high = min(0.95, base + spread)
        confidence = self._confidence_from_width(band_low, band_high)
        drivers = self._build_drivers(inquiry, rng)
        scenarios = self._build_scenarios(inquiry, rng)
        signal_strength = self._signal_strength(drivers, band_low, band_high)
        evidence = [
            {
                "title": f"Baseline trend data for '{inquiry}' (synthetic)",
                "date": "2025-09-01",
                "type": "other",
                "trust": 0.65,
                "summary": "Synthetic baseline constructed for local demo.",
                "link": "#"
            }
        ]
        calc = {
            "inquiry": inquiry,
            "probability": round(base, 3),
            "band": [round(band_low, 3), round(band_high, 3)],
            "confidence": confidence,
            "signal_strength": signal_strength,
            "drivers": [asdict(d) for d in drivers],
            "scenarios": [asdict(s) for s in scenarios],
            "evidence": evidence,
            "watch": self._watch_items(inquiry, rng),
            "timestamp": int(time.time())
        }
        if DEBUG_MODE:
            logger.info(f"Generated calc for '{inquiry}': {calc}")
        return calc

    def _confidence_from_width(self, low: float, high: float) -> str:
        width = high - low
        if width <= 0.12:
            return "High"
        if width <= 0.20:
            return "Medium"
        return "Low"

    def _build_drivers(self, inquiry: str, rng: random.Random) -> List[Driver]:
        bank = [
            ("Momentum", "↑", f"Recent directionality of the key metric for '{inquiry}' appears persistent."),
            ("Policy posture", "↑", f"Official guidance and regulatory tone amplify the trend in '{inquiry}'."),
            ("Counter-measures", "↓", f"Opposing actions could dampen the base trend related to '{inquiry}'."),
            ("Macroeconomic sentiment", "↑", f"Broader conditions tend to reinforce this outcome for '{inquiry}'."),
            ("Execution risk", "↓", f"Delivery complexity or talent bottlenecks could slow progress on '{inquiry}'.")
        ]
        rng.shuffle(bank)
        picks = bank[:4]
        weights = self._normalized([rng.uniform(0.15, 0.35) for _ in picks])
        drivers = []
        for (name, dirc, why), w in zip(picks, weights):
            drivers.append(Driver(name=name, direction=dirc, weight=round(w, 3), rationale=why))
        drivers.sort(key=lambda d: d.weight, reverse=True)
        return drivers

    def _build_scenarios(self, inquiry: str, rng: random.Random) -> List[Scenario]:
        s = [
            Scenario(
                name="Status Quo Drifts",
                likelihood=0.0,
                thesis=f"Inertia dominates '{inquiry}'; incremental change with few shocks.",
                tripwires=["Muted policy changes", "Stable funding/throughput"]
            ),
            Scenario(
                name="Shock & Realign",
                likelihood=0.0,
                thesis=f"External shock forces repricing and re-coordination in '{inquiry}'.",
                tripwires=["Sharp policy pivot", "Unexpected supply/tech event"]
            ),
            Scenario(
                name="Dark Horse Surge",
                likelihood=0.0,
                thesis=f"An underestimated actor/approach accelerates adoption or resistance for '{inquiry}'.",
                tripwires=["Surprise coalition", "Breakthrough demo with traction"]
            ),
        ]
        raw = [rng.uniform(0.2, 1.0) for _ in s]
        total = sum(raw)
        probs = [x / total for x in raw]
        for sc, p in zip(s, probs):
            sc.likelihood = round(p, 3)
        s.sort(key=lambda x: x.likelihood, reverse=True)
        return s

    def _watch_items(self, inquiry: str, rng: random.Random) -> List[str]:
        pool = [
            f"Credible first-principles cost breakdowns cross-checked by independents for '{inquiry}'",
            f"Cadence of on-the-record policy statements shifting stance on '{inquiry}'",
            f"Evidence of delivery throughput (hi-freq operational metrics) related to '{inquiry}'",
            f"Adoption signals by pivotal stakeholders in '{inquiry}'",
            f"Counter-measure maturity and test cadence for '{inquiry}'"
        ]
        rng.shuffle(pool)
        return pool[:3]

    def _normalized(self, xs: List[float]) -> List[float]:
        s = sum(xs)
        return [x / s for x in xs] if s > 0 else [1.0 / len(xs) for _ in xs]

    def _signal_strength(self, drivers: List[Driver], low: float, high: float) -> str:
        width = high - low
        top = drivers[0].weight if drivers else 0.0
        score = max(0.0, 1.0 - 2.0 * width) * 0.6 + top * 0.4
        if score >= 0.66:
            return "Strong"
        if score >= 0.4:
            return "Moderate"
        return "Soft"
