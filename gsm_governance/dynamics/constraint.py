from dataclasses import dataclass,field
from typing import Dict,Optional
import numpy as np
@dataclass
class CompensationVector:
    fiscal:float=0.; infrastructure:float=0.; representation:float=0.; regulatory:float=0.; future_commitment:float=0.; restitution:float=0.
    def as_array(self): return np.array([self.fiscal,self.infrastructure,self.representation,self.regulatory,self.future_commitment,self.restitution],float)
    @classmethod
    def scalar(cls,amount): return cls(fiscal=float(amount))
    def effective(self,lam):
        lam=np.asarray(lam,float)
        if lam.shape!=(6,):raise ValueError("valuation vector must have length 6")
        return float(lam@self.as_array())
@dataclass
class ThresholdFunction:
    omega:Dict[str,float]=field(default_factory=lambda:{"base":5.,"development":.1,"institutional_capacity":-.05,"historical_precedent":.05})
    def __call__(self,z): return max(0.,self.omega.get("base",0)+sum(w*z.get(k,0) for k,w in self.omega.items() if k!="base"))
@dataclass
class ConstraintResult:
    admissible:bool; condition:str; welfare_change:np.ndarray; threshold_used:np.ndarray; compensation_effective:np.ndarray; slack:np.ndarray
class BoundedNonExploitationConstraint:
    def __init__(self,tau=5.,weights=None,valuation_vectors:Optional[Dict[str,np.ndarray]]=None,contexts:Optional[Dict[str,dict]]=None): self.tau=tau; self.weights=weights; self.valuation_vectors=valuation_vectors or {}; self.contexts=contexts or {}
    def _tau(self,j):
        if callable(self.tau):return float(self.tau(self.contexts.get(j,{})))
        if isinstance(self.tau,(int,float)):return float(self.tau)
        return float(self.tau[j])
    def _lam(self,j): return np.asarray(self.valuation_vectors.get(j,np.ones(6)),float)
    def check(self,welfare_before,welfare_after,compensation=None):
        compensation=compensation or {}; names=list(welfare_before); dw=np.array([welfare_after[j]-welfare_before[j] for j in names]); tau=np.array([self._tau(j) for j in names]); ce=np.zeros(len(names))
        for n,j in enumerate(names): ce[n]=sum(c.effective(self._lam(j)) for (i,jj),c in compensation.items() if jj==j)
        slack=dw+tau+ce; ok=bool(np.all(slack>=0))
        if not ok:cond="violation"
        elif np.all(dw>=0):cond="A"
        elif np.all(dw+tau>=0):cond="B"
        else:cond="C"
        return ConstraintResult(ok,cond,dw,tau,ce,slack)
