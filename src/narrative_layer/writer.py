import logging

logger = logging.getLogger(__name__)

DEBUG_MODE = True

def _num(x, pct=False):
    try:
        v = float(x)
        if pct and v <= 1:
            return f"{round(v * 100)}%"
        else:
            return f"{round(v)}%"
    except Exception as e:
        logger.warning(f"Number formatting failed for {x}: {e}")
        return str(x)

def estimate_word_count(text: str) -> int:
    return len(text.split())

def render_report_markdown(calc: dict, length: str = "standard") -> str:
    try:
        inquiry = (calc.get("inquiry") or "Untitled Inquiry").strip()
        prob = calc.get("probability", calc.get("likelihood"))
        band = calc.get("band") or calc.get("interval") or ""
        conf = calc.get("confidence") or "Medium"
        drivers = calc.get("drivers") or []
        scenarios = calc.get("scenarios") or []
        watch = calc.get("watch") or []

        if isinstance(band, (list, tuple)) and len(band) == 2:
            band_txt = f"{_num(band[0], pct=True)}–{_num(band[1], pct=True)}"
        else:
            band_txt = str(band) if band else "n/a"

        if length == "brief":
            want_drv = 3
            want_scn = 2
            desc = "concise"
            target_words = 600
        elif length == "deep":
            want_drv = 6
            want_scn = 4
            desc = "elaborate"
            target_words = 1000
        else:
            want_drv = 5
            want_scn = 3
            desc = "detailed"
            target_words = 800

        drv_lines = []
        for d in drivers[:want_drv]:
            name = d.get("name") or d.get("factor") or "Key Driver"
            dirn = d.get("direction") or d.get("trend") or "↔"
            wt = d.get("weight") or d.get("importance")
            wt_txt = f" (weight {_num(wt, pct=True)})" if wt is not None else ""
            rationale = d.get("rationale") or ""
            if desc == "elaborate":
                desc_line = f": {rationale} Imagine {name.lower()} as a force unfolding, reshaping the landscape dramatically."
            elif desc == "detailed":
                desc_line = f": {rationale} The effects of {name.lower()} influence interconnected systems profoundly."
            else:
                desc_line = f": {rationale}" if rationale else ""
            drv_lines.append(f"- **{name}** ({dirn}){wt_txt}{desc_line}")

        scn_lines = []
        for s in scenarios[:want_scn]:
            nm = s.get("name") or "Scenario"
            lk = s.get("likelihood") or s.get("prob") or None
            thesis = s.get("thesis") or ""
            trips = s.get("tripwires") or []
            lk_txt = f"{_num(lk, pct=True) if lk is not None else 'n/a'} likelihood"
            if desc == "elaborate":
                vignette = f"\n\n*The scene unfolds*: {thesis} This scenario envisages a transformation shaped by unforeseen forces."
            elif desc == "detailed":
                vignette = f"\n\n*Projection*: {thesis} With nuanced impacts that echo through domains."
            else:
                vignette = f": {thesis}"
            trips_txt = f"\n  *Watch for:* " + "; ".join(trips) if trips else ""
            scn_lines.append(f"### {nm} — {lk_txt}{vignette}{trips_txt}")

        if not watch:
            watch = [
                "Potential policy shifts affecting key elements",
                "Technological breakthroughs altering trajectories",
                "Geopolitical developments influencing outcomes"
            ]

        watch_md = "\n".join(f"- {w}" for w in watch)

        intro = (
            f"# {inquiry}\n\n"
            f"*In the realm where data meets foresight, here lies our assessment.*\n\n"
            f"Probability: **{_num(prob, pct=True) if prob is not None else 'n/a'}** "
            f"(Uncertainty band: {band_txt}, Confidence: {conf}).\n\n"
        )

        context = (
            "## Context\n"
            "This briefing synthesizes current signals into an insightful narrative.\n\n"
        )

        drivers_section = f"## Drivers\n{chr(10).join(drv_lines)}\n\n" if drv_lines else ""
        scenarios_section = f"## Scenarios\n{chr(10).join(scn_lines)}\n\n" if scn_lines else ""
        watch_section = (
            "## Watchlist\n"
            "Elements that could dramatically change the trajectory:\n"
            + watch_md + "\n\n"
        )

        analyst_note = (
            "## Analyst Note\n"
            "This document is a living report; updates are expected as events unfold.\n"
        )

        full_report = intro + context + drivers_section + scenarios_section + watch_section + analyst_note

        if len(full_report.split()) < target_words * 0.8 and DEBUG_MODE:
            logger.warning("Generated report is shorter than expected; consider enriching data.")

        return full_report

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return f"Error generating report: {e}"
