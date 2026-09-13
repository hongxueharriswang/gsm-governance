import numpy as np,pytest
from gsm_governance import *
from gsm_governance.utils.normalization import minmax_normalize
def test_denmark_scores():
 m=MultiLevelGovernance.from_single_jurisdiction("Denmark",88.3,92.2,90,96.2,72.4,economic=95,quality=92.5,wellbeing=74,sustainability=88)
 assert m.gsi()==pytest.approx(78.77,abs=.05);assert m.hfi()==pytest.approx(87.375)
def test_constraint_conditions():
 c=BoundedNonExploitationConstraint(5)
 assert c.check({"A":80,"B":70},{"A":82,"B":70}).condition=="A"
 assert c.check({"A":80,"B":70},{"A":82,"B":67}).condition=="B"
 r=c.check({"A":80,"B":70},{"A":82,"B":62},{("A","B"):CompensationVector.scalar(3)})
 assert r.admissible and r.condition=="C"
 assert not c.check({"A":80,"B":70},{"A":82,"B":60}).admissible
def test_misc():
 assert minmax_normalize(.883,0,1)==pytest.approx(88.3)
 assert distribution_sensitive_hfi(np.array([90,80,70]),.1)<70
 assert resilience_metrics([70,80,90],90,1)["recovery_time"]==2
