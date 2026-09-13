from .sources import SOURCES,DENMARK_RAW
from ..utils.normalization import minmax_normalize
from ..core.state import GovernanceState,FlourishingState
def load_denmark_raw():return dict(DENMARK_RAW)
def normalize_denmark():
    n={k:minmax_normalize(v,SOURCES[k].theoretical_min,SOURCES[k].theoretical_max) for k,v in DENMARK_RAW.items()};return GovernanceState(**n)
def load_flourishing(economic,quality,wellbeing,sustainability):return FlourishingState(economic,quality,wellbeing,sustainability)
