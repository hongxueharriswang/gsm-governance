"""
Metadata for external data sources.  No fetching occurs here; loaders
are expected to consume locally cached files.
"""

from __future__ import annotations

from typing import dict

SOURCES: dict[str, dict[str, str]] = {
    "vdem": {
        "name": "V-Dem",
        "url": "https://www.v-dem.net/",
        "indicators": "procedural justice, accountability",
    },
    "wgi": {
        "name": "World Bank Worldwide Governance Indicators",
        "url": "https://info.worldbank.org/governance/wgi/",
        "indicators": "competence, rule of law, voice",
    },
    "wjp": {
        "name": "World Justice Project",
        "url": "https://worldjusticeproject.org/",
        "indicators": "procedural justice, corrective justice",
    },
    "undp": {
        "name": "UNDP Human Development Reports",
        "url": "https://hdr.undp.org/",
        "indicators": "distributive justice, flourishing",
    },
    "owid": {
        "name": "Our World in Data",
        "url": "https://ourworldindata.org/",
        "indicators": "intergenerational justice, sustainability",
    },
    "worldbank": {
        "name": "World Bank Open Data",
        "url": "https://data.worldbank.org/",
        "indicators": "distributive justice, competence",
    },
}


def source_metadata(key: str) -> dict[str, str]:
    if key not in SOURCES:
        raise KeyError(f"unknown source: {key}")
    return dict(SOURCES[key])