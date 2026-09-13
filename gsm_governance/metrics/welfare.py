import numpy as np
def compute_welfare(gsi,hfi,weights): return float(weights.theta_g*gsi+weights.theta_f*hfi)
def _gini(x):
    x=np.sort(np.asarray(x,float)); n=x.size
    if n==0 or np.allclose(x,0): return 0.
    i=np.arange(1,n+1); return float((2*(i*x).sum()-(n+1)*x.sum())/(n*x.sum()))
def distribution_sensitive_hfi(hfi_vector,rho=.1):
    x=np.asarray(hfi_vector,float)
    if x.size==0: raise ValueError("hfi_vector must be non-empty")
    return float(x.min()-rho*_gini(x))
