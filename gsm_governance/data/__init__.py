"""Data subpackage: external data loaders."""

from gsm_governance.data.loaders import (
    load_denmark_raw,
    load_justice_indicators,
    normalize_denmark,
)
from gsm_governance.data.sources import (
    SOURCES,
    source_metadata,
)

__all__ = [
    "SOURCES",
    "load_denmark_raw",
    "load_justice_indicators",
    "normalize_denmark",
    "source_metadata",
]