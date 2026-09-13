from dataclasses import dataclass
import numpy as np
@dataclass
class TransitionModel:
    config:object; params:object
    def __post_init__(self):self.params=self.params.resolved()
    def step_governance(self,g_t,f_prev,interact=None,M_eff=None,target=None,control=None,rng=None):
        p=self.params; interact=g_t if interact is None else interact; M_eff=np.eye(5) if M_eff is None else M_eff; target=g_t if target is None else target; control=np.zeros(5) if control is None else control
        x=(np.eye(5)-np.diag(p.depreciation_g))@g_t+p.eta*(p.B_fg@f_prev)+p.kappa_M*((M_eff*p.A_g)@interact)-p.mu*(p.K_g@(g_t-target))+control
        if p.noise_g:x+=p.noise_g*(rng or np.random.default_rng()).standard_normal(5)
        return np.clip(x,0,100)
    def step_flourishing(self,f_t,g_prev,D_star=0.,R=None,rng=None):
        p=self.params; x=(np.eye(4)-np.diag(p.depreciation_f))@f_t+p.zeta*(p.C_gf@g_prev)-p.xi*D_star*p.d_f
        if p.S is not None:x-=p.delta*(p.S@np.asarray(R if R is not None else np.zeros(p.S.shape[1])))
        if p.noise_f:x+=p.noise_f*(rng or np.random.default_rng()).standard_normal(4)
        return np.clip(x,0,100)
