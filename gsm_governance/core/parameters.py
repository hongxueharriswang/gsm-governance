from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

CAPABILITIES=("accountability","competence","cohesion","continuity","learning")
FLOURISHING_DIMENSIONS=("economic","quality","wellbeing","sustainability")
N_CAPABILITIES=5; N_FLOURISHING=4

def _default_kappa():
    x=np.zeros((5,5)); x[np.triu_indices(5,1)]=0.005; return x+x.T

@dataclass
class WelfareWeights:
    theta_g: float=0.5; theta_f: float=0.5
    def __post_init__(self):
        if min(self.theta_g,self.theta_f)<0 or not np.isclose(self.theta_g+self.theta_f,1): raise ValueError("Welfare weights must be non-negative and sum to 1.")

@dataclass
class LevelParameters:
    depreciation_g: np.ndarray | None=None; depreciation_f: np.ndarray | None=None
    eta: float=.10; B_fg: np.ndarray | None=None; kappa_M: float=.05; A_g: np.ndarray | None=None
    mu: float=.20; K_g: np.ndarray | None=None; zeta: float=.15; C_gf: np.ndarray | None=None
    xi: float=.10; d_f: np.ndarray | None=None; delta: float=.10; S: np.ndarray | None=None
    noise_g: float=0.; noise_f: float=0.
    def resolved(self):
        return LevelParameters(np.full(5,.02) if self.depreciation_g is None else np.asarray(self.depreciation_g),np.full(4,.02) if self.depreciation_f is None else np.asarray(self.depreciation_f),self.eta,np.eye(5,4)*.05 if self.B_fg is None else self.B_fg,self.kappa_M,np.eye(5) if self.A_g is None else self.A_g,self.mu,np.eye(5) if self.K_g is None else self.K_g,self.zeta,np.eye(4,5)*.05 if self.C_gf is None else self.C_gf,self.xi,np.ones(4) if self.d_f is None else self.d_f,self.delta,self.S,self.noise_g,self.noise_f)

@dataclass
class GSMConfig:
    alpha: np.ndarray=field(default_factory=lambda:np.full(5,.2)); kappa: np.ndarray=field(default_factory=_default_kappa)
    gamma: np.ndarray=field(default_factory=lambda:np.full(4,.25)); omega: np.ndarray | None=None; nu: np.ndarray | None=None
    lambda_1: float=.05; lambda_2: float=.005; lambda_3: float=.5; rho: float=.1
    welfare_weights: WelfareWeights=field(default_factory=WelfareWeights)
    def __post_init__(self):
        self.alpha=np.asarray(self.alpha,float); self.kappa=np.asarray(self.kappa,float); self.gamma=np.asarray(self.gamma,float)
        if self.alpha.shape!=(5,) or self.kappa.shape!=(5,5) or self.gamma.shape!=(4,): raise ValueError("Invalid parameter dimensions.")
        if not np.isclose(self.gamma.sum(),1): raise ValueError("gamma must sum to 1.")
