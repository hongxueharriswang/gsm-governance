# gsm-governance

Reference implementation of the **computational theory of justice-centered
multi-level governance** (GSM-J) developed in:

> Wang, H. *A Computational Theory of Justice-Centered Multi-Level Governance
> for Human Flourishing under Bounded Non-Exploitation.*

This library implements the v5 version of the theory. It is not a systems
model with normative extensions; it is the reference implementation of a
computational theory whose normative parameters are explicit, swappable, and
reported (Section 1.7 of the paper).

## Install

```bash
pip install -e ".[dev]"
```

Requires Python 3.9+. The core library has no mandatory dependencies.

## Quick start

```python
from gsm_governance import GSMConfig, Simulation, load_stylized_nordic

config = GSMConfig(seed=42)
jurisdictions = load_stylized_nordic()
sim = Simulation(config, jurisdictions)
history = sim.run(n_steps=20)
print(history[-1]["welfare"])
```

See `examples/stylized_nordic.py` for a full walkthrough.

## What's new in 0.4.0

The 0.3.0 release implemented the theory as it stood in preprint v3. This
release (0.4.0) implements the v5 computational theory. The five substantive
changes:

### 1. M_J is decomposed into synergy and tension components

The matrix now has separate `m_plus` (>= 0) and `m_minus` (<= 0) components.
The net `m` is a property computed from them. This makes it possible to
represent a **contested pair** -- a pair whose net coefficient can be near
zero because of offsetting components, not because the mechanism is absent.

```python
from gsm_governance import JusticeInteractionMatrix

M = JusticeInteractionMatrix()
M.pair_type("intergenerational", "procedural")   # "contested"
M.pair_type("procedural", "intergenerational")   # "single_component_tension"
M.m[("intergenerational", "procedural")]         # net = +0.05
```

**Migration.** The `m` dict on `JusticeInteractionMatrix` is retained as a
read-only property that returns `m_plus + m_minus`. Existing code that reads
`matrix.m` will work; code that mutates it must now set `m_plus` or `m_minus`
directly.

### 2. C3 is a reduced threshold, not zero tolerance

C3 (Section 3.6.3) is implemented as `tau_vuln = phi_vuln * tau`, not as
`E > 0`. The effective threshold function is exported:

```python
from gsm_governance.constraints import effective_tau
tau = effective_tau(jurisdiction, config)
```

**Migration.** `GSMConfig.phi` is split into `phi_vuln` (C3) and `phi_d`
(C4). Default `phi_vuln = 0.50`, matching the paper's illustrative value.

### 3. C4 is an absolute dimension-specific margin

C4 (Section 3.6.4) is `J_child^d >= J_parent^d - phi_d`, not
`J_child^d >= phi * J_parent^d`. A `phi_d` dict of dimension-specific margins
replaces the scalar `phi`.

```python
config = GSMConfig(phi_d={"distributive": 0.05, "recognition": 0.10, ...})
```

### 4. Welfare supports the paper's quadratic shortfall form

The default welfare mode is the paper's Section 4.3 form
`W = sum w_d [gamma_d J - delta_d (1 - J)^2]`. The older linear-floor form is
available for comparison:

```python
config = GSMConfig(welfare_mode="linear_floor")
```

### 5. Dynamics include vertical alignment pressure

The justice step now includes the `beta_d (J_parent - J)` term of Section
4.1. C4 is no longer enforced only as a post-hoc constraint; it also shapes
the trajectory.

```python
config = GSMConfig(beta={"distributive": 0.10, ...})
```

### Other changes

- Naming: `load_denmark_raw()` and `normalize_denmark()` are deprecated in
  favour of `load_stylized_nordic_raw()` and `load_stylized_nordic()`. The
  paper's Section 6 states that no actual country is claimed to instantiate
  the model.
- `estimation.estimate_MJ` is a documented scaffold, not a working estimator.
  The paper's Section 3.3.3 is explicit that component identification
  requires additional information that a library cannot manufacture; the
  scaffold exposes the sign priors and component mask that a downstream
  Bayesian implementation would use.

## Concepts

- **State vector** `[A, C, S, T, L, J]` where `J = [J_D, J_P, J_R, J_C, J_I]`
  (Sections 3.2, 3.3).
- **Interaction matrix** `M_J = M_J^+ + M_J^-` with twelve committed pairs
  (Section 3.3.2).
- **Constraints** C1 (bounded non-exploitation), C2 (dimension floors),
  C3 (vulnerability), C4 (vertical alignment) (Section 3.6).
- **Welfare** dimension-specific, prioritarian by default (Section 4.3).
- **Accountability** dimension-specific (Section 3.7).
- **Intervention** multi-channel with cost, horizon, and recovery (Section 4.1).
- **Estimation** scaffold for Appendix D.

## License

MIT.
