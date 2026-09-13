import numpy as np
def compute_gsi(g,config):
    a=g.as_array(); raw=float(config.alpha@a)+sum(config.kappa[i,j]*a[i]*a[j] for i in range(5) for j in range(i+1,5))
    denom=float(config.alpha.sum()*100+np.triu(config.kappa,1).sum()*10000)
    return raw/denom*100 if denom>0 else raw
def compute_hfi(f,config): return float(config.gamma@f.as_array())
