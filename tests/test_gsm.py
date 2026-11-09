"""Unit tests for gsm-governance 0.4.0."""
import pytest
from gsm_governance import (
    GSMConfig, State, Jurisdiction, JusticeInteractionMatrix,
    check_c1, check_c2, check_c3, check_c4,
    WelfareEvaluator, CompensationVector,
    PolicyInterventionEnforcer, Intervention, Simulation,
    load_stylized_nordic,
    CONTESTED_PAIRS, SINGLE_COMPONENT_TENSION_PAIRS, SINGLE_COMPONENT_SYNERGY_PAIRS,
    DIMENSIONS,
)


def test_contested_pair_is_only_one():
    assert CONTESTED_PAIRS == frozenset({("intergenerational", "procedural")})


def test_committed_pair_counts():
    assert len(SINGLE_COMPONENT_SYNERGY_PAIRS) == 7
    assert len(SINGLE_COMPONENT_TENSION_PAIRS) == 4
    assert len(CONTESTED_PAIRS) == 1
    assert (len(SINGLE_COMPONENT_SYNERGY_PAIRS)
            + len(SINGLE_COMPONENT_TENSION_PAIRS)
            + len(CONTESTED_PAIRS)) == 12


def test_interaction_matrix_pair_types():
    M = JusticeInteractionMatrix()
    assert M.pair_type("intergenerational", "procedural") == "contested"
    assert M.pair_type("procedural", "intergenerational") == "single_component_tension"
    assert M.pair_type("procedural", "recognition") == "single_component_synergy"
    assert M.pair_type("distributive", "recognition") == "uncommitted"


def test_interaction_matrix_net_is_sum_of_components():
    M = JusticeInteractionMatrix()
    for (d, e), net in M.m.items():
        p = M.m_plus.get((d, e), 0.0)
        m = M.m_minus.get((d, e), 0.0)
        assert abs(net - (p + m)) < 1e-9


def test_c3_uses_reduced_threshold_not_zero():
    config = GSMConfig(phi_vuln=0.5)
    vuln = Jurisdiction(id="v", level=2, tau=0.10,
                        state=State(justice={d: 0.10 for d in DIMENSIONS}))
    comp = {}
    expl = {("p", "v"): 0.03}
    assert check_c1([vuln], expl, comp, config) == []
    expl = {("p", "v"): 0.07}
    assert check_c1([vuln], expl, comp, config) == [("p", "v")]


def test_c3_reports_vulnerable_jurisdictions():
    config = GSMConfig(aggregate_floor=0.5)
    vuln = Jurisdiction(id="v", level=2, tau=0.10,
                        state=State(justice={d: 0.10 for d in DIMENSIONS}))
    assert check_c3([vuln], config) == ["v"]


def test_c4_uses_absolute_margin():
    config = GSMConfig(phi_d={d: 0.10 for d in DIMENSIONS})
    parent = Jurisdiction(id="p", level=1,
                          state=State(justice={d: 0.80 for d in DIMENSIONS}))
    child = Jurisdiction(id="c", level=2,
                         state=State(justice={d: 0.60 for d in DIMENSIONS}))
    parent.add_child(child)
    violations = check_c4([parent, child], config)
    assert len(violations) == len(DIMENSIONS)
    for d in DIMENSIONS:
        child.state.justice[d] = 0.75
    assert check_c4([parent, child], config) == []


def test_welfare_prioritarian_default():
    config = GSMConfig()
    w = WelfareEvaluator(config)
    assert not w.is_prioritarian()
    config = GSMConfig(
        gamma_w={d: 0.20 for d in DIMENSIONS},
        delta_w={d: 1.00 for d in DIMENSIONS},
    )
    assert WelfareEvaluator(config).is_prioritarian()


def test_welfare_quadratic_vs_linear():
    config_q = GSMConfig(welfare_mode="quadratic")
    config_l = GSMConfig(welfare_mode="linear_floor")
    j = Jurisdiction(id="j", level=1,
                     state=State(justice={d: 0.40 for d in DIMENSIONS}))
    w_q = WelfareEvaluator(config_q).welfare([j])
    w_l = WelfareEvaluator(config_l).welfare([j])
    assert abs(w_q["base"] - w_l["base"]) > 1e-6


def test_dynamics_alignment_pressure():
    from gsm_governance.dynamics import justice_step
    config = GSMConfig(beta={d: 1.0 for d in DIMENSIONS},
                       alpha={d: 1.0 for d in DIMENSIONS},
                       gamma={d: 0.0 for d in DIMENSIONS})
    parent = Jurisdiction(id="p", level=1,
                          state=State(justice={d: 0.90 for d in DIMENSIONS}))
    child = Jurisdiction(id="c", level=2,
                         state=State(justice={d: 0.20 for d in DIMENSIONS}))
    parent.add_child(child)
    M = JusticeInteractionMatrix()
    M.m_plus = {}
    M.m_minus = {}
    dJ = justice_step(child, config, M)
    assert abs(dJ["distributive"] - 0.70) < 1e-6


def test_compensation_adequacy():
    config = GSMConfig()
    c = CompensationVector(fiscal=0.10)
    assert c.is_adequate(0.08, config)
    assert not c.is_adequate(0.15, config)


def test_intervention_cost_effects():
    config = GSMConfig(kappa_int=0.10)
    j = Jurisdiction(id="j", level=1,
                     state=State(
                         justice={d: 0.50 for d in DIMENSIONS},
                         capabilities={"accountability": 0.5, "competence": 0.5,
                                       "cohesion": 0.5, "continuity": 0.5, "learning": 0.5},
                     ))
    enf = PolicyInterventionEnforcer(config)
    enf.add(Intervention(jurisdiction_id="j", start_t=0,
                         channel="fiscal", magnitude=0.20))
    j_before = dict(j.state.justice)
    enf.apply(0, [j])
    assert j.state.justice["distributive"] > j_before["distributive"]
    assert j.state.capabilities["cohesion"] < 0.5


def test_end_to_end_simulation():
    config = GSMConfig(seed=42)
    juris = load_stylized_nordic()
    sim = Simulation(config, juris)
    history = sim.run(10)
    assert len(history) == 10
    for row in history:
        assert "welfare" in row
        assert "violations" in row
        assert set(row["violations"]) == {"c1", "c2", "c3", "c4"}


def test_effective_threshold_export():
    from gsm_governance.constraints import effective_tau
    config = GSMConfig(aggregate_floor=0.5, phi_vuln=0.5)
    vuln = Jurisdiction(id="v", level=2, tau=0.10,
                        state=State(justice={d: 0.10 for d in DIMENSIONS}))
    assert abs(effective_tau(vuln, config) - 0.05) < 1e-9
    non_vuln = Jurisdiction(id="n", level=2, tau=0.10,
                            state=State(justice={d: 0.90 for d in DIMENSIONS}))
    assert abs(effective_tau(non_vuln, config) - 0.10) < 1e-9
