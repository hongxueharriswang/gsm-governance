"""
Data loaders.  These produce normalized dictionaries ready for
construction of a MultiLevelGovernance hierarchy.

No external network calls are made; users must supply cached files.
The v0.2.0 Denmark example has been retained but reframed as a
*stylized* demonstration (see manuscript §9.4).
"""

from __future__ import annotations

from typing import dict

import numpy as np


def load_denmark_raw(path: str | None = None) -> dict:
    """
    Load raw Denmark indicator data.

    If no path is supplied, returns the values used in the stylized
    demonstration (manuscript §9).  Values are illustrative, not empirical.
    """
    if path is None:
        return {
            "national": {
                "A": 0.82, "C": 0.85, "S": 0.78, "T": 0.75, "L": 0.80,
                "distributive": 0.78, "procedural": 0.75,
                "recognition": 0.60, "corrective": 0.35,
                "intergenerational": 0.55,
            },
            "regions": {
                "capital": {"A": 0.80, "C": 0.82, "S": 0.75, "T": 0.72, "L": 0.78,
                            "distributive": 0.80, "procedural": 0.76,
                            "recognition": 0.65, "corrective": 0.38,
                            "intergenerational": 0.58},
                "zealand": {"A": 0.78, "C": 0.80, "S": 0.76, "T": 0.73, "L": 0.76,
                            "distributive": 0.76, "procedural": 0.74,
                            "recognition": 0.58, "corrective": 0.34,
                            "intergenerational": 0.54},
                "south": {"A": 0.76, "C": 0.79, "S": 0.74, "T": 0.71, "L": 0.75,
                          "distributive": 0.75, "procedural": 0.73,
                          "recognition": 0.57, "corrective": 0.33,
                          "intergenerational": 0.53},
            },
        }
    import json
    with open(path, "r") as f:
        return json.load(f)


def normalize_denmark(raw: dict) -> dict:
    """
    Normalize a Denmark-style nested dictionary so that all capabilities
    and justice dimensions fall in [0, 1].
    """
    def _norm(d: dict) -> dict:
        out = {}
        for k, v in d.items():
            if isinstance(v, dict):
                out[k] = _norm(v)
            else:
                out[k] = float(np.clip(v, 0.0, 1.0))
        return out
    return _norm(raw)


def load_justice_indicators(path: str | None = None) -> dict:
    """
    Load justice dimension indicators suitable for calibrating M_J.

    Returns a dict keyed by jurisdiction uid, containing time series for
    each dimension.  Placeholder: returns an empty dict unless a path
    to a local CSV is supplied.
    """
    if path is None:
        return {}
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required to load justice indicator files")
    df = pd.read_csv(path)
    out = {}
    for uid, sub in df.groupby("uid"):
        out[uid] = sub.drop(columns=["uid"]).to_dict(orient="list")
    return out