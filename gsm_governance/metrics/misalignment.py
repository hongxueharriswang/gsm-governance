import numpy as np
def context_sensitive_misalignment(g,target,W=None):
    d=g.as_array()-target.as_array(); W=np.eye(5) if W is None else np.asarray(W); return float(np.sqrt(d@W@d))
def vertical_misalignment(system,jurisdiction_name=None,W_vert=None):
    order={"community":1,"municipal":2,"regional":3,"provincial":3,"national":4,"supranational":5,"international":5}
    js=sorted(system.jurisdictions,key=lambda j:order.get(j.level,99)); W=np.eye(5) if W_vert is None else W_vert
    if len(js)<2:return 0.
    vals=[]
    for a,b in zip(js,js[1:]):
        d=b.governance.as_array()-a.governance.as_array(); vals.append(np.sqrt(d@W@d))
    return float(np.mean(vals))
