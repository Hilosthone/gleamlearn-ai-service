# visual_spec.py — the closed set of visuals a "visual_lesson" may use, and their validation.
#
# The model returns DATA for one of these renderers; nothing is ever executed (no code, expressions, URLs or markup).
# Unknown types/fields and out-of-range values are dropped or clamped; a step whose visual is invalid keeps its text.
# The backend (src/learning/visual-lesson.ts) and the frontend validate the same contract again.
import math
import re
from typing import Any, Dict, List, Optional

VISUAL_TYPES = ("shape3d", "molecule", "graph2d", "vectors", "orbit", "wave", "flow", "labeled")
SHAPES = ("cube", "cuboid", "sphere", "cylinder", "cone", "pyramid", "torus", "prism")
FAMILIES = ("linear", "quadratic", "cubic", "sine", "cosine", "exponential", "logarithmic", "absolute")
ELEMENTS = ("H", "C", "N", "O", "F", "P", "S", "Cl", "Br", "I", "Na", "K", "Mg", "Ca", "Fe", "Cu", "Zn", "Al", "Si", "B", "Li", "He", "Ne", "Ar")

# Shown to the model: what each visual type is for and its exact fields.
REGISTRY_PROMPT = """Each step may have ONE "visual" chosen from this closed list (or null). Use only these fields:
- {"type":"shape3d","shape":"cube|cuboid|sphere|cylinder|cone|pyramid|torus|prism","dimensions":{"<name>":<number>},"labels":["..."],"caption":"..."}  geometry
- {"type":"molecule","name":"...","atoms":[{"id":"o1","element":"O"}],"bonds":[{"a":"o1","b":"h1","order":1}],"caption":"..."}  chemistry (elements: H C N O F P S Cl Br I Na K Mg Ca Fe Cu Zn Al Si B Li He Ne Ar)
- {"type":"graph2d","family":"linear|quadratic|cubic|sine|cosine|exponential|logarithmic|absolute","a":1,"b":0,"c":0,"d":0,"xMin":-10,"xMax":10,"xLabel":"x","yLabel":"y","points":[{"x":0,"y":0,"label":"..."}],"caption":"..."}  maths; y = a*f(b*x + c) + d
- {"type":"vectors","vectors":[{"x":3,"y":0,"z":0,"label":"Force"}],"showResultant":true,"caption":"..."}  physics forces/velocities
- {"type":"orbit","center":"Nucleus","bodies":[{"label":"Electron","radius":3,"period":10}],"caption":"..."}  orbits, electron shells
- {"type":"wave","amplitude":1,"wavelength":4,"waves":1,"label":"...","caption":"..."}  waves
- {"type":"flow","nodes":[{"id":"a","label":"..."}],"edges":[{"from":"a","to":"b","label":"..."}],"cycle":false,"caption":"..."}  processes and cycles
- {"type":"labeled","subject":"Plant cell","parts":[{"label":"Nucleus","description":"..."}],"caption":"..."}  structures and their parts
Choose the visual that genuinely helps; use null when none fits. Never invent other types or fields."""

_CTRL = re.compile(r"[\x00-\x1f\x7f]")


def _s(v: Any, limit: int) -> str:
    return re.sub(r"\s+", " ", _CTRL.sub(" ", v)).strip()[:limit] if isinstance(v, str) else ""


def _text(v: Any, limit: int) -> str:
    return re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", v.replace("\r\n", "\n")).strip()[:limit] if isinstance(v, str) else ""


def _n(v: Any, lo: float, hi: float, default: float) -> float:
    try:
        n = float(v)
    except (TypeError, ValueError):
        return default
    if math.isnan(n) or math.isinf(n):
        return default
    return min(hi, max(lo, n))


def _id(v: Any) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "", _s(v, 24))


def _list(v: Any, limit: int) -> List[Any]:
    return v[:limit] if isinstance(v, list) else []


def _dicts(v: Any, limit: int) -> List[Dict[str, Any]]:
    return [x for x in _list(v, limit) if isinstance(x, dict)]


def validate_visual(raw: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict) or raw.get("type") not in VISUAL_TYPES:
        return None
    t = raw["type"]
    caption = _s(raw.get("caption"), 200)
    if t == "shape3d":
        if raw.get("shape") not in SHAPES:
            return None
        dims = raw.get("dimensions") if isinstance(raw.get("dimensions"), dict) else {}
        dimensions = {_s(k, 24): _n(d, 0.1, 100, 1) for k, d in list(dims.items())[:4] if _s(k, 24)}
        return {"type": t, "caption": caption, "shape": raw["shape"], "labels": [x for x in (_s(l, 60) for l in _list(raw.get("labels"), 6)) if x], "dimensions": dimensions}
    if t == "molecule":
        atoms = [{"id": _id(a.get("id")), "element": a.get("element")} for a in _dicts(raw.get("atoms"), 24)]
        atoms = [a for a in atoms if a["id"] and a["element"] in ELEMENTS]
        ids = {a["id"] for a in atoms}
        if not atoms or len(ids) != len(atoms):
            return None
        bonds = [{"a": _id(b.get("a")), "b": _id(b.get("b")), "order": int(round(_n(b.get("order"), 1, 3, 1)))} for b in _dicts(raw.get("bonds"), 40)]
        bonds = [b for b in bonds if b["a"] in ids and b["b"] in ids and b["a"] != b["b"]]
        return {"type": t, "caption": caption, "name": _s(raw.get("name"), 80), "atoms": atoms, "bonds": bonds}
    if t == "graph2d":
        if raw.get("family") not in FAMILIES:
            return None
        x_min, x_max = _n(raw.get("xMin"), -100, 100, -10), _n(raw.get("xMax"), -100, 100, 10)
        if x_max <= x_min:
            x_min, x_max = -10, 10
        points = [{"x": _n(p.get("x"), -1000, 1000, 0), "y": _n(p.get("y"), -1000, 1000, 0), "label": _s(p.get("label"), 40)} for p in _dicts(raw.get("points"), 8)]
        return {"type": t, "caption": caption, "family": raw["family"], "a": _n(raw.get("a"), -100, 100, 1), "b": _n(raw.get("b"), -100, 100, 0), "c": _n(raw.get("c"), -100, 100, 0), "d": _n(raw.get("d"), -100, 100, 0), "xMin": x_min, "xMax": x_max, "xLabel": _s(raw.get("xLabel"), 30), "yLabel": _s(raw.get("yLabel"), 30), "points": points}
    if t == "vectors":
        vectors = [{"x": _n(a.get("x"), -10, 10, 0), "y": _n(a.get("y"), -10, 10, 0), "z": _n(a.get("z"), -10, 10, 0), "label": _s(a.get("label"), 40)} for a in _dicts(raw.get("vectors"), 8)]
        vectors = [v for v in vectors if v["x"] or v["y"] or v["z"]]
        return {"type": t, "caption": caption, "vectors": vectors, "showResultant": raw.get("showResultant") is True} if vectors else None
    if t == "orbit":
        bodies = [{"label": _s(b.get("label"), 40), "radius": _n(b.get("radius"), 1, 10, 3), "period": _n(b.get("period"), 1, 60, 10)} for b in _dicts(raw.get("bodies"), 8)]
        bodies = [b for b in bodies if b["label"]]
        return {"type": t, "caption": caption, "center": _s(raw.get("center"), 40) or "Centre", "bodies": bodies} if bodies else None
    if t == "wave":
        return {"type": t, "caption": caption, "amplitude": _n(raw.get("amplitude"), 0.1, 5, 1), "wavelength": _n(raw.get("wavelength"), 0.5, 20, 4), "waves": int(round(_n(raw.get("waves"), 1, 6, 1))), "label": _s(raw.get("label"), 60)}
    if t == "flow":
        nodes = [{"id": _id(n.get("id")), "label": _s(n.get("label"), 60)} for n in _dicts(raw.get("nodes"), 12)]
        nodes = [n for n in nodes if n["id"] and n["label"]]
        ids = {n["id"] for n in nodes}
        if len(nodes) < 2 or len(ids) != len(nodes):
            return None
        edges = [{"from": _id(e.get("from")), "to": _id(e.get("to")), "label": _s(e.get("label"), 40)} for e in _dicts(raw.get("edges"), 20)]
        edges = [e for e in edges if e["from"] in ids and e["to"] in ids and e["from"] != e["to"]]
        return {"type": t, "caption": caption, "nodes": nodes, "edges": edges, "cycle": raw.get("cycle") is True}
    # labeled
    parts = [{"label": _s(p.get("label"), 50), "description": _s(p.get("description"), 200)} for p in _dicts(raw.get("parts"), 10)]
    parts = [p for p in parts if p["label"]]
    return {"type": t, "caption": caption, "subject": _s(raw.get("subject"), 60), "parts": parts} if parts else None


def validate_visual_lesson(raw: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None
    steps = [{"title": _s(s.get("title"), 120), "explanation": _text(s.get("explanation"), 2500), "visual": validate_visual(s.get("visual"))} for s in _dicts(raw.get("steps"), 10)]
    steps = [s for s in steps if s["title"] and s["explanation"]]
    if len(steps) < 2:
        return None
    return {
        "version": 1,
        "title": _s(raw.get("title"), 200),
        "summary": _text(raw.get("summary"), 1200),
        "steps": steps,
        "keyTakeaways": [x for x in (_s(k, 200) for k in _list(raw.get("keyTakeaways"), 8)) if x],
    }
