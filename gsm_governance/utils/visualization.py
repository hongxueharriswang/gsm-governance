import matplotlib.pyplot as plt
import numpy as np
from ..core.parameters import CAPABILITIES,FLOURISHING_DIMENSIONS
def plot_governance_radar(values,label="Governance",ax=None,color="steelblue"):
    v=list(values); n=5
    if len(v)!=n:raise ValueError("Expected 5 values")
    a=np.linspace(0,2*np.pi,n,endpoint=False).tolist(); v+=v[:1]; a+=a[:1]
    if ax is None:_,ax=plt.subplots(subplot_kw={"projection":"polar"})
    ax.plot(a,v,color=color,label=label);ax.fill(a,v,color=color,alpha=.2);ax.set_xticks(a[:-1]);ax.set_xticklabels(CAPABILITIES);ax.set_ylim(0,100);return ax
def plot_governance_trajectory(trajectory,time=None,ax=None):
    x=np.asarray(trajectory,float);time=np.arange(len(x)) if time is None else time
    if ax is None:_,ax=plt.subplots()
    for i,n in enumerate(CAPABILITIES):ax.plot(time,x[:,i],label=n)
    ax.legend();return ax
def plot_flourishing_trajectory(trajectory,time=None,ax=None):
    x=np.asarray(trajectory,float);time=np.arange(len(x)) if time is None else time
    if ax is None:_,ax=plt.subplots()
    for i,n in enumerate(FLOURISHING_DIMENSIONS):ax.plot(time,x[:,i],label=n)
    ax.legend();return ax
