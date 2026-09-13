from gsm_governance import MultiLevelGovernance,Jurisdiction,GovernanceState,FlourishingState,Simulation,BoundedNonExploitationConstraint
levels=["community","municipal","provincial","national","international"]
js=[Jurisdiction(f"Canada:{l}",l,GovernanceState(82,83,84,85,86),FlourishingState(85,88,82,75)) for l in levels]
s=Simulation(MultiLevelGovernance(jurisdictions=js),BoundedNonExploitationConstraint(5),seed=42);print(s.run(3).to_dataframe().tail())
