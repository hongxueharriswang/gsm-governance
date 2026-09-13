from dataclasses import dataclass,field
import copy, numpy as np, pandas as pd
from .transitions import TransitionModel
@dataclass
class SimulationHistory:
    records:list=field(default_factory=list)
    def to_dataframe(self):return pd.DataFrame(self.records)
class Simulation:
    def __init__(self,system,constraint=None,seed=None):self.system=system;self.constraint=constraint;self.rng=np.random.default_rng(seed)
    def run(self,n_steps,shocks=None,controls=None,callback=None):
        h=SimulationHistory(); self._record(h,0)
        for t in range(n_steps):
            before=copy.deepcopy([(j.governance,j.flourishing) for j in self.system.jurisdictions]); wb={j.name:self.system.welfare(j.name) for j in self.system.jurisdictions}
            for j in self.system.jurisdictions:
                m=TransitionModel(self.system.config,j.params); g=j.governance.as_array(); f=j.flourishing.as_array(); target=j.target.as_array(); c=(controls or {}).get(t,{}).get(j.name,np.zeros(5)); R=(shocks or {}).get(t,{}).get(j.name)
                from ..metrics.misalignment import context_sensitive_misalignment
                j.governance=j.governance.from_array(m.step_governance(g,f,target=target,control=c,rng=self.rng)); j.flourishing=j.flourishing.from_array(m.step_flourishing(f,g,context_sensitive_misalignment(before[self.system.jurisdictions.index(j)][0],j.target),R,self.rng))
            if self.constraint:
                wa={j.name:self.system.welfare(j.name) for j in self.system.jurisdictions}; result=self.constraint.check(wb,wa)
                if not result.admissible:
                    for j,(g,f) in zip(self.system.jurisdictions,before):j.governance,j.flourishing=g,f
            self._record(h,t+1)
            if callback:callback(t+1,self.system)
        return h
    def _record(self,h,t):
        for j in self.system.jurisdictions:
            r=j.observation(t).to_record();r.update(gsi=self.system.gsi(j.name),hfi=self.system.hfi(j.name));h.records.append(r)
