import numpy as np
def resilience_metrics(hfi_trajectory,hfi_star,epsilon=1.):
    x=np.asarray(hfi_trajectory,float); loss=np.maximum(0,hfi_star-x); hits=np.where(np.abs(x-hfi_star)<epsilon)[0]
    return {"recovery_time":float(hits[0]) if hits.size else float(len(x)),"max_loss":float(loss.max(initial=0)),"cumulative_loss":float(loss.sum())}
