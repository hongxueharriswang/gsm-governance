from gsm_governance import MultiLevelGovernance
from gsm_governance.data.loaders import normalize_denmark
g=normalize_denmark();m=MultiLevelGovernance.from_single_jurisdiction("Denmark",*g.as_array(),economic=95,quality=92.5,wellbeing=74,sustainability=88)
print(f"GSI={m.gsi():.2f} HFI={m.hfi():.2f}")
