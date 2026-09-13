from dataclasses import dataclass,field
from typing import Optional
import numpy as np, pandas as pd
from .parameters import GSMConfig,LevelParameters
from .state import GovernanceState,FlourishingState,Observation
@dataclass
class Jurisdiction:
    name:str; level:str; governance:GovernanceState; flourishing:FlourishingState; target:Optional[GovernanceState]=None; params:LevelParameters=field(default_factory=LevelParameters)
    def __post_init__(self):
        if self.target is None:self.target=GovernanceState.from_array(self.governance.as_array())
    def observation(self,time): return Observation(self.name,self.level,time,self.governance,self.flourishing)
class MultiLevelGovernance:
    def __init__(self,config=None,jurisdictions=None,vertical_top_down=None,vertical_bottom_up=None,horizontal=None,information=None):
        self.config=config or GSMConfig(); self.jurisdictions=list(jurisdictions or []); self.vertical_top_down=vertical_top_down or {}; self.vertical_bottom_up=vertical_bottom_up or {}; self.horizontal=horizontal or {}; self.information=information or {}
    @classmethod
    def from_single_jurisdiction(cls,name,accountability,competence,cohesion,continuity,learning,economic=70,quality=70,wellbeing=70,sustainability=70,level="national",config=None):
        return cls(config or GSMConfig(),[Jurisdiction(name,level,GovernanceState(accountability,competence,cohesion,continuity,learning),FlourishingState(economic,quality,wellbeing,sustainability))])
    def _get(self,name):
        for j in self.jurisdictions:
            if j.name==name:return j
        raise KeyError(name)
    def add_jurisdiction(self,j): self.jurisdictions.append(j)
    def gsi(self,name=None):
        from ..metrics.indices import compute_gsi
        j=self.jurisdictions[0] if name is None and len(self.jurisdictions)==1 else self._get(name)
        return compute_gsi(j.governance,self.config)
    def hfi(self,name=None,distribution_sensitive=False):
        from ..metrics.indices import compute_hfi
        from ..metrics.welfare import distribution_sensitive_hfi
        if distribution_sensitive:return distribution_sensitive_hfi(np.array([compute_hfi(j.flourishing,self.config) for j in self.jurisdictions]),self.config.rho)
        j=self.jurisdictions[0] if name is None and len(self.jurisdictions)==1 else self._get(name); return compute_hfi(j.flourishing,self.config)
    def misalignment(self,name,vertical=False):
        from ..metrics.misalignment import context_sensitive_misalignment,vertical_misalignment
        return vertical_misalignment(self) if vertical else context_sensitive_misalignment(self._get(name).governance,self._get(name).target)
    def welfare(self,name,distribution_sensitive=False):
        from ..metrics.welfare import compute_welfare
        return compute_welfare(self.gsi(name),self.hfi(distribution_sensitive=True) if distribution_sensitive else self.hfi(name),self.config.welfare_weights)
    def snapshot(self,time=0): return pd.DataFrame([j.observation(time).to_record() for j in self.jurisdictions])
