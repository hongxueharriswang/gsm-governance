from gsm_governance import BoundedNonExploitationConstraint,CompensationVector
before={"A":80.,"B":70.};after={"A":83.,"B":62.};comp={("A","B"):CompensationVector.scalar(3.)}
r=BoundedNonExploitationConstraint(tau=5.).check(before,after,comp);print(r)
