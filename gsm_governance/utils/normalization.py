def minmax_normalize(value,lower,upper,out_range=(0.,100.)):
    if upper<=lower:raise ValueError("upper must exceed lower")
    lo,hi=out_range; return float(lo+(value-lower)/(upper-lower)*(hi-lo))
