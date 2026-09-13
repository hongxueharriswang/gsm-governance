from dataclasses import dataclass
import numpy as np
from .parameters import CAPABILITIES,FLOURISHING_DIMENSIONS
@dataclass
class GovernanceState:
    accountability:float; competence:float; cohesion:float; continuity:float; learning:float
    def as_array(self): return np.array([self.accountability,self.competence,self.cohesion,self.continuity,self.learning],float)
    @classmethod
    def from_array(cls,a):
        a=np.asarray(a,float); 
        if a.shape!=(5,): raise ValueError("GovernanceState requires 5 values.")
        return cls(*a)
    def to_dict(self): return {k:getattr(self,k) for k in CAPABILITIES}
@dataclass
class FlourishingState:
    economic:float; quality:float; wellbeing:float; sustainability:float
    def as_array(self): return np.array([self.economic,self.quality,self.wellbeing,self.sustainability],float)
    @classmethod
    def from_array(cls,a):
        a=np.asarray(a,float)
        if a.shape!=(4,): raise ValueError("FlourishingState requires 4 values.")
        return cls(*a)
    def to_dict(self): return {k:getattr(self,k) for k in FLOURISHING_DIMENSIONS}
@dataclass
class Observation:
    jurisdiction:str; level:str; time:int; governance:GovernanceState; flourishing:FlourishingState
    def to_record(self):
        d={"jurisdiction":self.jurisdiction,"level":self.level,"time":self.time}
        d.update({f"gov_{k}":v for k,v in self.governance.to_dict().items()}); d.update({f"flo_{k}":v for k,v in self.flourishing.to_dict().items()}); return d
