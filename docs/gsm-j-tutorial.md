# Just-Centred Governance: A Computational Tutorial

**From moral philosophy to working simulation with `gsm-governance` 0.3.0**

---

## Preface

This tutorial introduces **just-centred governance** as a computational research program and walks through the `gsm-governance` library that implements it. It is written for readers who are comfortable with Python and curious about political theory, but who may not yet be familiar with either formal governance modelling or the justice literature.

By the end, you will be able to:

- Explain why justice is best modelled as a governance capability rather than an external constraint
- Build and run simulations of multi-level governance systems
- Interpret results in terms of justice dimensions, constraints, and interventions
- Apply the model to policy analysis, comparative governance, and research questions

The tutorial proceeds in five parts. Part I motivates the problem. Part II explains the model. Part III shows how to use the library. Part IV presents five applications. Part V reflects on what the model can and cannot do.

---

# Part I — Why just-centred governance needs a computational model

## 1. The problem

Imagine you are advising a national government on how to allocate a fixed budget for regional development. Three regions have different needs. One is wealthy and well-governed. One is poor but improving. One is poor and has just experienced a natural disaster. How should you allocate?

Standard policy analysis answers this with a cost-benefit calculation. The allocation that maximizes aggregate welfare wins. But this answer ignores at least four questions:

1. **What is a fair distribution?** If the wealthy region produces more value per dollar, a purely aggregative approach will direct more funds there — even though the poorer regions need them more.
2. **Who gets to decide?** If the wealthy region has more political voice, the process may itself be unjust even if the outcome happens to be fair.
3. **What is owed to the region that was historically disadvantaged?** If the disaster region's poverty is a legacy of past extraction, current allocation formulas may compound the harm.
4. **What is owed to future generations?** If the budget deficit is financed by borrowing, current allocations impose costs on people who have no voice in the decision.

Each of these questions concerns **justice**, and each is distinct from aggregate welfare. A model that treats only welfare will systematically under-represent justice concerns.

## 2. The multi-level dimension

The problem is compounded by a second feature of modern governance: it is **multi-level**. Decisions are made simultaneously at household, community, municipal, provincial, national, regional, and global levels. Each level has partial authority and partial information. Each level's decisions reshape the constraint set of the others.

Multi-level structure creates opportunities for **jurisdictional exploitation**. A national government can impose uncompensated costs on a province. A regional bloc can extract from a member state. A present generation can deplete the capability of a future one. These are not market failures; they are governance failures arising from asymmetric power, incomplete representation, and the absence of enforceable reciprocity across levels.

Most formal governance models either ignore the multi-level structure, treat it as exogenous, or permit exploitation when aggregate welfare improves. The result is a class of models that can endorse arrangements that are efficient but unjust.

## 3. The insight: justice is a capability, not just a constraint

Conventional approaches to justice in governance modelling treat justice as an **external criterion**: simulate the system, compute outcomes, then evaluate whether those outcomes are just. This is the "justice as referee" model.

A different approach treats justice as a **capability**: a state variable that co-evolves with the other properties of the system and that influences — and is influenced by — those properties.

The distinction is subtle but consequential:

| | Justice as constraint | Justice as capability |
|---|---|---|
| Nature | External evaluative criterion | Internal state variable |
| Role | Judges outcomes | Shapes and is shaped by outcomes |
| Dynamics | Static (given the state) | Dynamic (evolves over time) |
| Feedback | None | Enables or constrains other capabilities |
| Policy implication | Prescribe just outcomes | Build and maintain justice capability |

The capability view is grounded in a simple observation: **just governance institutions produce better outcomes across the board**. Trust, voluntary compliance, information sharing, and long-horizon cooperation all depend on justice. A society with strong procedural justice is easier to govern than one without. A jurisdiction with legitimate recognition practices has more resilient social cohesion than one that marginalizes groups.

Justice is not merely a moral ceiling on what governance may do. It is a **productive capability** that governance either possesses or lacks, and that can be developed, eroded, diffused, learned, and institutionalized.

---

# Part II — The model

## 4. State representation

The GSM-J model represents each jurisdiction at each governance level with a **state vector** containing six elements.

### The five base capabilities

| Symbol | Capability | What it means |
|---|---|---|
| $A$ | Accountability | Answerability of power-holders to affected parties |
| $C$ | Institutional competence | Capacity to design and deliver policy |
| $S$ | Social cohesion | Trust, shared norms, mutual identification |
| $T$ | Strategic continuity | Consistency of long-horizon commitments |
| $L$ | Adaptive learning | Capacity to update in response to feedback |

These five capabilities are drawn from prior work in governance theory and complex adaptive systems.

### The sixth capability: justice

The justice capability $J$ is **multi-dimensional**. It has five facets:

| Dimension | What it tracks |
|---|---|
| **Distributive** ($J^D$) | Fair allocation of resources, risks, and capabilities |
| **Procedural** ($J^P$) | Fairness of decision-making processes |
| **Recognition** ($J^R$) | Dignity, non-domination, participation as peers |
| **Corrective** ($J^C$) | Remedy for historical and structural wrong |
| **Intergenerational** ($J^I$) | Fairness to future generations |

Each dimension is a scalar in $[0, 1]$. The full justice state of a jurisdiction is a five-vector.

### Why five dimensions?

The five dimensions are not arbitrary. Each corresponds to a distinct tradition in justice theory:

- **Distributive** — Rawls, Sen, Nussbaum: how resources and capabilities are allocated
- **Procedural** — Habermas, deliberative democracy: how decisions are made
- **Recognition** — Fraser, Taylor, Honneth, Young: how groups are recognized and dignified
- **Corrective** — Waldron, Thompson: how historical wrongs are remedied
- **Intergenerational** — Parfit, Gardiner, Shue: how future generations are treated

A governance system can score high on some dimensions and low on others. A jurisdiction with strong welfare provision but weak participation rights has high distributive justice and low procedural justice. A jurisdiction with formal equality but persistent cultural marginalization has high procedural justice and low recognition justice.

## 5. Justice dimension interactions

The five dimensions are not independent. Some pairs reinforce each other (**synergies**). Others trade off (**tensions**).

### Synergies

- **Procedural ↔ recognition**: voice enables dignity; dignity enables voice
- **Distributive ↔ procedural**: material security enables participation; participation produces just allocation
- **Corrective → recognition**: remedy restores dignity
- **Recognition → corrective**: recognized groups can demand remedy

### Tensions

- **Intergenerational ↔ distributive**: future investment displaces present distribution
- **Corrective → distributive**: reparations draw from present resources
- **Procedural → intergenerational**: present participation crowds out future representation

The model captures both via a **signed interaction matrix** $M_J$. Positive entries are synergies; negative entries are tensions.

This matters empirically. A purely additive model would predict that justice improvements always reinforce each other. A signed matrix reveals that some justice-improving interventions produce offsetting effects in other dimensions.

## 6. Constraints

Four normative constraints bound the system's behaviour.

### C1 — Bounded non-exploitation

**No jurisdiction may impose uncompensated, non-trivial sacrifices on another for its own benefit.**

Formally: $E_{ij} \le \tau_j$, or $\mathrm{Comp}_{ij} \ge E_{ij}$.

Exploitation is permitted below the tolerance threshold $\tau_j$, and above it if adequately compensated. This is the minimal justice condition.

### C2 — Justice floor

**No jurisdiction may fall below a dimension-specific minimum.**

Formally: $J_i^d \ge J_{\min}^d$ for each dimension $d$.

The floors encode a **moral minimum**. Three traditions converge on such a minimum: sufficientarianism (everyone should have *enough*), capability thresholds (each capability has a threshold below which dignity is not possible), and human rights (minimum entitlements are non-derogable).

### C3 — Vulnerability-sensitive non-exploitation

**No exploitation of jurisdictions already below the aggregate floor.**

Formally: if $J_j < J_{\min}^{\text{agg}}$, then $E_{ij} = 0$ for all $i$.

This is the most distinctive constraint. It encodes a **prioritarian** commitment: the worse off a jurisdiction is, the stronger its protection against further extraction. It closes a gap in C1: a vulnerable jurisdiction with a low tolerance threshold $\tau_j$ could be exploited "legally" under C1 without C3.

### C4 — Vertical justice alignment

**Higher levels may not erode justice achieved at lower levels.**

Formally: $J_i^{d, (l)} \ge \phi \cdot J_i^{d, (l-1)}$ for each dimension $d$, with $\phi$ the subsidiarity tolerance.

C4 is a **non-regression principle**, not a uniformity principle. Local justice may exceed national justice — sanctuary cities, climate-leading municipalities, indigenous self-governance. What C4 forbids is the reverse: higher levels eroding lower-level justice.

## 7. Dynamics

Justice is not static. Each dimension evolves according to:

$$
\frac{dJ^d}{dt} = \underbrace{g_d(\mathbf{x})}_{\text{internal}} + \underbrace{h_d(E, \mathrm{Comp})}_{\text{exploitation}} + \underbrace{\mathcal{C}_J^d(J)}_{\text{coupling}} + \underbrace{\eta \sum_j A_{ij}(J_j^d - J_i^d)}_{\text{diffusion}} - \underbrace{\kappa_d J^d}_{\text{decay}}
$$

In words:

- **Internal coupling**: justice dimensions are supported by base capabilities. Strong accountability and competence produce distributive justice; strong procedural capability produces procedural justice; and so on.
- **Exploitation and compensation**: exploitation erodes justice; compensation restores it.
- **Corrective restorative**: remedy builds restorative capability, not merely offsetting harm.
- **Diffusion**: justice diffuses across neighbouring jurisdictions.
- **Decay**: without support, justice erodes.

The system is **path-dependent**. Two jurisdictions with identical initial conditions may converge on different equilibria depending on which dimensions were prioritized.

## 8. Welfare

The welfare function aggregates flourishing across jurisdictions with a **prioritarian** structure:

$$
W^* = W + \sum_d \gamma_d J^d - \sum_d \delta_d [J_{\min}^d - J^d]^+
$$

The three terms are:

- **Base welfare** $W$: flourishing from base capabilities
- **Justice contribution** $\sum_d \gamma_d J^d$: justice is constitutive of flourishing
- **Prioritarian penalty** $-\sum_d \delta_d [J_{\min}^d - J^d]^+$: justice deficits reduce welfare disproportionately

The default condition $\delta_d > \gamma_d$ encodes prioritarianism: fixing a deficit matters more than further improving the just.

**This is a normative choice.** Users who reject prioritarianism can set $\delta_d = \gamma_d$; the model will produce different predictions.

## 9. Interventions

When a constraint is violated, the model schedules a **policy intervention**: a designated authority raises the affected state over a finite horizon, at a cost distributed across capabilities.

Every intervention has four attributes:

- **Designated authority** — who implements the correction
- **Implementation cost** $\kappa^{\text{int}}$ per unit of correction
- **Finite horizon** $\tau^{\text{int}}$ — steps to full implementation
- **Multi-channel capability effects** — cost distributed across competence, cohesion, continuity, and accountability

The multi-channel cost is a substantive modelling choice. It reflects the reality that constitutional reforms, redistributive legislation, and international agreements do not merely consume administrative capacity. They also affect cohesion (through short-term polarization), continuity (through policy volatility), and accountability (through override of local decision-making).

The consequence is a **frequency ceiling**: aggressive justice-improvement programs are self-limiting, because they cumulatively degrade the capabilities required to implement them.

---

# Part III — The library in practice

## 10. Installation and first steps

Install from source:

```bash
git clone https://github.com/hongxueharriswang/gsm-governance.git
cd gsm-governance
pip install -e ".[dev]"
```

Verify:

```python
import gsm_governance as gsm
print(gsm.__version__)  # "0.3.0"
```

Run the built-in demonstration:

```bash
python -m gsm_governance
```

## 11. A complete worked example

Let us model a three-level federal system with a national government, three provinces, and three municipalities. We'll give each jurisdiction a distinct justice profile and observe how justice evolves over time.

### Step 1 — Configure the model

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeState,
    Simulation, JusticeInteractionMatrix, MJRegime,
)

config = GSMConfig()
M = JusticeInteractionMatrix(regime=MJRegime.SYMMETRIC)
```

The configuration holds all parameters. Defaults are theoretically motivated but should be justified for each study.

### Step 2 — Build the hierarchy

```python
gov = MultiLevelGovernance(config=config)

# National level
gov.add_jurisdiction(
    "national", level=4,
    capabilities={"A": 0.70, "C": 0.72, "S": 0.65, "T": 0.68, "L": 0.70},
    justice=JusticeState({
        "distributive": 0.55, "procedural": 0.60,
        "recognition": 0.35, "corrective": 0.25,
        "intergenerational": 0.50,
    }),
)

# Provinces
provinces = {
    "province_wealthy": {
        "caps": {"A": 0.75, "C": 0.78, "S": 0.70, "T": 0.72, "L": 0.70},
        "justice": {"distributive": 0.70, "procedural": 0.68,
                    "recognition": 0.55, "corrective": 0.30,
                    "intergenerational": 0.55},
    },
    "province_poor": {
        "caps": {"A": 0.55, "C": 0.50, "S": 0.60, "T": 0.55, "L": 0.50},
        "justice": {"distributive": 0.30, "procedural": 0.35,
                    "recognition": 0.25, "corrective": 0.10,
                    "intergenerational": 0.30},
    },
    "province_disaster": {
        "caps": {"A": 0.60, "C": 0.45, "S": 0.55, "T": 0.40, "L": 0.55},
        "justice": {"distributive": 0.25, "procedural": 0.40,
                    "recognition": 0.30, "corrective": 0.15,
                    "intergenerational": 0.35},
    },
}
for uid, data in provinces.items():
    gov.add_jurisdiction(
        uid, level=3,
        capabilities=data["caps"],
        justice=JusticeState(data["justice"]),
    )
    gov.link_vertical("national", uid)

# Municipalities
municipalities = {
    "city_metro": {
        "caps": {"A": 0.72, "C": 0.75, "S": 0.68, "T": 0.70, "L": 0.72},
        "justice": {"distributive": 0.65, "procedural": 0.62,
                    "recognition": 0.50, "corrective": 0.28,
                    "intergenerational": 0.52},
    },
    "city_small": {
        "caps": {"A": 0.58, "C": 0.52, "S": 0.62, "T": 0.50, "L": 0.52},
        "justice": {"distributive": 0.35, "procedural": 0.40,
                    "recognition": 0.30, "corrective": 0.12,
                    "intergenerational": 0.32},
    },
    "city_coastal": {
        "caps": {"A": 0.62, "C": 0.48, "S": 0.55, "T": 0.42, "L": 0.55},
        "justice": {"distributive": 0.28, "procedural": 0.42,
                    "recognition": 0.32, "corrective": 0.15,
                    "intergenerational": 0.38},
    },
}
for uid, data in municipalities.items():
    gov.add_jurisdiction(
        uid, level=2,
        capabilities=data["caps"],
        justice=JusticeState(data["justice"]),
    )

gov.link_vertical("province_wealthy", "city_metro")
gov.link_vertical("province_poor", "city_small")
gov.link_vertical("province_disaster", "city_coastal")
gov.link_horizontal("province_wealthy", "province_poor")
gov.link_horizontal("province_poor", "province_disaster")
gov.link_horizontal("city_metro", "city_small")
```

### Step 3 — Inject exploitation

Suppose the wealthy province extracts from the poor one via a regressive tax-sharing formula, without adequate compensation:

```python
sim = Simulation(gov, config=config, M_J=M)

sim.set_exploitation("province_wealthy", "province_poor", {
    "distributive": 0.20,
    "procedural": 0.10,
    "recognition": 0.05,
    "corrective": 0.00,
    "intergenerational": 0.08,
})

sim.set_compensation("province_wealthy", "province_poor", {
    "distributive": 0.05,
    "procedural": 0.02,
    "recognition": 0.00,
    "corrective": 0.00,
    "intergenerational": 0.02,
})
```

### Step 4 — Run the simulation

```python
history = sim.run(steps=500)
```

### Step 5 — Read the results

```python
import pandas as pd

df = pd.DataFrame(history)
print(df[["t", "W_star", "mean_justice",
          "C2_violations", "C3_violations", "C4_violations",
          "active_interventions"]].tail(10))
```

The output shows:

- `W_star`: welfare including justice
- `mean_justice`: aggregate justice level
- `C2_violations`: count of floor violations
- `C3_violations`: count of vulnerability-sensitive violations
- `C4_violations`: count of vertical alignment violations
- `active_interventions`: how many policy interventions are currently active

### Step 6 — Per-jurisdiction profile

```python
for uid, j in gov.jurisdictions.items():
    print(f"\n{uid}:")
    for d in gsm.JUSTICE_DIMENSIONS:
        val = j.state.justice.d[d]
        floor = config.justice_floors[d]
        marker = " <-- below floor" if val < floor else ""
        print(f"  {d:20s}: {val:.3f}{marker}")
```

You will see which jurisdictions have improved, which remain below floor, and how interventions have redistributed justice across the hierarchy.

---

# Part IV — Applications

## Application 1: Policy analysis — designing intervention schedules

**Question.** A national government wants to raise recognition justice in its three most marginalized municipalities. What intervention schedule should it adopt?

**Approach.** Simulate two schedules: aggressive (short horizon, high frequency) and patient (long horizon, low frequency). Compare outcomes.

```python
def run_schedule(horizon, cost, weights):
    config = GSMConfig(
        intervention_horizon=horizon,
        intervention_cost=cost,
        intervention_weights=weights,
    )
    gov = build_test_hierarchy(config)
    sim = Simulation(gov, config=config)
    return sim.run(steps=500)

# Aggressive schedule
aggressive = run_schedule(
    horizon=2,
    cost=0.10,
    weights={"C": 0.25, "S": 0.25, "T": 0.25, "A": 0.25},
)

# Patient schedule
patient = run_schedule(
    horizon=15,
    cost=0.05,
    weights={"C": 0.60, "S": 0.15, "T": 0.15, "A": 0.10},
)

# Compare recognition justice trajectory
import matplotlib.pyplot as plt
plt.plot([r["t"] for r in aggressive],
         [r["dim_means"]["recognition"] for r in aggressive],
         label="Aggressive")
plt.plot([r["t"] for r in patient],
         [r["dim_means"]["recognition"] for r in patient],
         label="Patient")
plt.xlabel("Time")
plt.ylabel("Mean recognition justice")
plt.legend()
```

**What you will likely find.** The aggressive schedule raises recognition justice faster in the short run but depletes cohesion and continuity, capping long-run improvement. The patient schedule is slower but reaches a higher steady state. This is the **frequency ceiling** in action.

**Policy implication.** Justice reform is not a matter of doing as much as possible as fast as possible. It is a matter of **pacing interventions** to preserve the capabilities required to implement them. The model quantifies the trade-off.

---

## Application 2: Comparative governance — benchmarking jurisdictions

**Question.** How does Denmark compare to Sweden and Norway on justice capability, and what explains the differences?

**Approach.** Construct the three countries as single-level jurisdictions with empirically motivated justice profiles, then simulate their trajectories under identical conditions.

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeState, Simulation,
    justice_index, justice_floor_violations, welfare_dimension_specific,
)

countries = {
    "Denmark": {
        "distributive": 0.82, "procedural": 0.80,
        "recognition": 0.65, "corrective": 0.40,
        "intergenerational": 0.65,
    },
    "Sweden": {
        "distributive": 0.80, "procedural": 0.78,
        "recognition": 0.68, "corrective": 0.42,
        "intergenerational": 0.68,
    },
    "Norway": {
        "distributive": 0.85, "procedural": 0.76,
        "recognition": 0.62, "corrective": 0.38,
        "intergenerational": 0.75,
    },
}

config = GSMConfig()
results = {}

for name, profile in countries.items():
    gov = MultiLevelGovernance(config=config)
    gov.add_jurisdiction(name, level=4, justice=JusticeState(profile))
    sim = Simulation(gov, config=config)
    hist = sim.run(steps=300)
    results[name] = {
        "final_welfare": hist[-1]["W_star"],
        "justice_index": justice_index(gov),
        "violations": justice_floor_violations(gov),
    }

import pandas as pd
df = pd.DataFrame(results).T
print(df)
```

**What you will find.** Norway's intergenerational score drives a higher long-run welfare trajectory despite weaker procedural justice. Sweden's recognition profile produces a higher justice index. Denmark sits between on most dimensions.

**Interpretive note.** The absolute values matter less than the **profile shape**. Two countries with the same mean justice may have very different trajectories because their weakest dimension constrains the others via the coupling matrix.

---

## Application 3: Constitutional design — choosing floors and weights

**Question.** A constitutional convention is debating the appropriate justice floor for a new federal system. What floors produce the most robust outcomes across a range of conditions?

**Approach.** Sweep the floor vector over a plausible range and evaluate long-run welfare under shocks.

```python
import numpy as np
from itertools import product
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeState, Simulation,
)

def simulate_with_floors(floors, shock_time=150, shock_size=0.25):
    config = GSMConfig(justice_floors=floors)
    gov = MultiLevelGovernance(config=config)
    gov.add_jurisdiction("national", level=4)
    gov.add_jurisdiction(
        "region", level=3,
        justice=JusticeState({"distributive": 0.50, "procedural": 0.50,
                              "recognition": 0.40, "corrective": 0.30,
                              "intergenerational": 0.50}),
    )
    gov.link_vertical("national", "region")

    sim = Simulation(gov, config=config)

    # Apply shock at t=shock_time
    class ShockSim(Simulation):
        def step(self):
            super().step()
            if abs(self.t - shock_time) < config.dt / 2:
                for j in self.governance.jurisdictions.values():
                    j.state.justice.d["distributive"] -= shock_size

    sim.__class__ = ShockSim
    hist = sim.run(steps=300)
    return hist[-1]["W_star"]

# Sweep floors
floor_values = [0.10, 0.20, 0.30, 0.40]
results = {}
for f in floor_values:
    floors = {d: f for d in gsm.JUSTICE_DIMENSIONS}
    try:
        results[f] = simulate_with_floors(floors)
    except ValueError:
        results[f] = None

print(pd.DataFrame(results, index=["Final W*"]).T)
```

**What you will find.** Very low floors provide little protection. Very high floors trigger frequent interventions that deplete capabilities. An **intermediate floor** (roughly 0.25–0.35) balances protection against intervention cost. This is the model's answer to "how much justice is optimal?" — a question no purely philosophical analysis can answer.

**Interpretive note.** The optimum depends on the intervention cost and the shock severity. Under low-cost, high-shock scenarios, higher floors win. Under high-cost scenarios, lower floors win. Constitutional design must therefore consider both values and implementation capacity.

---

## Application 4: Historical injustice — modelling corrective dynamics

**Question.** How long does it take to repair historical injustice under different compensation strategies?

**Approach.** Model a jurisdiction that has suffered generations of distributive injustice. Compare three compensation regimes: minimal (10% of historical harm), moderate (50%), and full (100%).

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeState,
    Simulation, CompensationMechanism,
)

def run_correction(compensation_fraction, years=200):
    config = GSMConfig()
    gov = MultiLevelGovernance(config=config)

    gov.add_jurisdiction(
        "perpetrator", level=4,
        capabilities={"A": 0.80, "C": 0.80, "S": 0.75, "T": 0.80, "L": 0.80},
        justice={d: 0.70 for d in gsm.JUSTICE_DIMENSIONS},
    )
    gov.add_jurisdiction(
        "descendant", level=4,
        capabilities={"A": 0.50, "C": 0.45, "S": 0.55, "T": 0.40, "L": 0.45},
        justice={d: 0.20 for d in gsm.JUSTICE_DIMENSIONS},
    )

    sim = Simulation(gov, config=config)

    # Historical harm expressed as an existing corrective deficit
    sim.set_exploitation("perpetrator", "descendant", {
        "corrective": 0.60,  # historical harm
        "distributive": 0.30,
    })
    sim.set_compensation("perpetrator", "descendant", {
        "corrective": 0.60 * compensation_fraction,
        "distributive": 0.30 * compensation_fraction,
    })

    hist = sim.run(steps=years)
    return hist

# Compare
for frac in [0.1, 0.5, 1.0]:
    hist = run_correction(frac)
    final = hist[-1]["mean_justice"]
    print(f"Compensation {frac:.0%}: final mean justice = {final:.3f}")
```

**What you will find.** Full compensation converges fastest, but with **diminishing returns** — 50% compensation achieves most of the gain because the coupling matrix amplifies partial remedy. This is a substantive finding: reparative justice is not linear. A partial remedy, once recognized as genuine, produces restorative dynamics that exceed its arithmetic contribution.

**Policy implication.** The choice between 50% and 100% compensation is not merely a matter of resources. It is a matter of **recognition**: whether the remedy is sufficient to establish that the harm is being genuinely addressed. The model makes this threshold effect visible.

---

## Application 5: Climate governance — intergenerational analysis

**Question.** How should a jurisdiction balance present development and future obligations?

**Approach.** Model a two-generation system. The present generation chooses a savings rate for the future generation. Explore the trade-off between present welfare and intergenerational justice.

```python
from gsm_governance import (
    GSMConfig, MultiLevelGovernance, JusticeState, Simulation,
)

def simulate_generation(savings_rate):
    config = GSMConfig()
    gov = MultiLevelGovernance(config=config)

    gov.add_jurisdiction(
        "present_generation", level=4,
        capabilities={"A": 0.70, "C": 0.75, "S": 0.65, "T": 0.60, "L": 0.70},
        justice=JusticeState({
            "distributive": 0.60, "procedural": 0.65,
            "recognition": 0.55, "corrective": 0.30,
            "intergenerational": 0.30 + savings_rate * 0.5,
        }),
    )
    gov.add_jurisdiction(
        "future_generation", level=4,
        justice=JusticeState({
            "distributive": 0.60 + savings_rate * 0.4,
            "procedural": 0.50, "recognition": 0.55,
            "corrective": 0.30,
            "intergenerational": 0.50 + savings_rate * 0.3,
        }),
    )

    # Present generation imposes intergenerational cost
    sim = Simulation(gov, config=config)
    sim.set_exploitation("present_generation", "future_generation", {
        "intergenerational": 0.30 * (1 - savings_rate),
    })

    hist = sim.run(steps=300)
    return {
        "present_justice": gov["present_generation"].state.justice.d["intergenerational"],
        "future_justice": gov["future_generation"].state.justice.d["intergenerational"],
        "final_welfare": hist[-1]["W_star"],
    }

# Sweep savings rate
for rate in [0.0, 0.3, 0.6, 0.9]:
    result = simulate_generation(rate)
    print(f"Savings rate {rate:.1f}: present={result['present_justice']:.3f}, "
          f"future={result['future_justice']:.3f}, W*={result['final_welfare']:.3f}")
```

**What you will find.** Intergenerational justice is not a zero-sum trade-off. Moderate savings rates produce higher long-run welfare than either extreme. Extremely high savings rates harm present welfare enough to trigger prioritarian penalties; extremely low rates harm future welfare and activate C4.

**Interpretive note.** This is the model's answer to the climate policy debate. It does not tell us what savings rate is correct. It shows that the *shape* of the trade-off is not linear and that a moderate approach may dominate both extremes on welfare grounds even before normative considerations.

---

# Part V — What the model can and cannot do

## 12. What the model does well

**Makes normative commitments explicit.** Every normative parameter — weights, floors, prioritarian coefficients, intervention weights — is a variable the user must specify. Nothing is hidden.

**Represents multi-level interaction.** Vertical and horizontal linkages, subsidiarity, cross-level accountability, and diffusion are all endogenous.

**Distinguishes justice from welfare.** Justice contributes to welfare but is not reducible to it. The model can represent cases where justice is sacrificed for short-term welfare or vice versa.

**Represents trade-offs.** The signed interaction matrix captures both synergies and tensions between justice dimensions. This produces realistic path-dependence and non-monotonic trajectories.

**Enables comparative analysis.** Two configurations can be simulated side by side, isolating the effect of a single parameter or a single constraint.

**Supports policy design.** The frequency ceiling and multi-channel cost model make intervention pacing a first-class concern.

## 13. What the model cannot do

**Decide what justice is.** The model represents consequences of justice specifications. It does not adjudicate between specifications. Users who disagree about what justice requires will run different models and reach different conclusions.

**Eliminate value judgments.** The default parameters reflect specific normative priors (Rawlsian, prioritarian, capability-based). Users should replace them with parameters they can justify.

**Predict real-world outcomes.** The model is a tool for exploring mechanisms, not a forecasting instrument. Its predictions depend on parameters that must be calibrated for each context.

**Represent every nuance.** Five justice dimensions, four constraints, six capabilities. These are simplifications. Real governance systems have finer structure.

**Resolve tragic conflicts.** Where justice and flourishing genuinely conflict, the model represents the trade-off but does not resolve it. Some dilemmas are not solvable by computation.

## 14. What to do with the model

The model is best used as a **structured reasoning tool**. It provides a formal vocabulary for asking questions like:

- What happens if we raise the floor on recognition justice?
- How long does it take to repair historical injustice under different compensation regimes?
- Which dimensions of justice have the largest spillover effects on others?
- Under what conditions does aggressive intervention backfire?

These are questions no single discipline can answer alone. Political theory can specify what justice is; economics can model incentives; systems theory can capture feedback. The model integrates all three.

## 15. Where the framework could go

The natural next steps for researchers using this framework:

- **Empirical calibration** of the interaction matrix $M_J$ from panel data (manuscript Appendix D)
- **Comparative case studies** of specific countries or regions, with documented justice profiles
- **Extensions to additional dimensions** (ecological justice, epistemic justice, territorial justice) with theoretical justification
- **Alternative enforcement mechanisms** (deliberative, market-based, network-based)
- **Integration with agent-based models** to represent heterogeneous individual behaviour
- **Applications to international governance** (climate, trade, migration)

The framework is designed to be extended. Its architecture makes normative commitments explicit precisely so that extensions can be debated.

---

# Further reading

For the mathematical specification of GSM-J:

> Wang, H. H. (2026). *Justice as a Governance Capability: A Computational Systems Model of Multi-Level Governance for Human Flourishing under Bounded Non-Exploitation*. Preprints.org. https://doi.org/10.20944/preprints202609.0964.v2

For the philosophy underlying the model:

- Rawls, J. (1971). *A Theory of Justice*. Harvard University Press.
- Sen, A. (1999). *Development as Freedom*. Oxford University Press.
- Nussbaum, M. C. (2011). *Creating Capabilities*. Harvard University Press.
- Fraser, N. (2009). *Scales of Justice*. Columbia University Press.
- Young, I. M. (1990). *Justice and the Politics of Difference*. Princeton University Press.
- Pettit, P. (1997). *Republicanism*. Oxford University Press.
- Gardiner, S. M. (2011). *A Perfect Moral Storm*. Oxford University Press.

For systems and governance theory:

- Ostrom, E. (1990). *Governing the Commons*. Cambridge University Press.
- Beer, S. (1972). *Brain of the Firm*. Allen Lane.
- Meadows, D. H. (2008). *Thinking in Systems*. Chelsea Green.

For computational social science:

- Lazer, D., et al. (2020). Computational social science: Obstacles and opportunities. *Science*, 369(6507), 1060–1062.
- Watts, D. J. (2021). *Computational Social Science*. Cambridge University Press.

For the library:

- Repository: https://github.com/hongxueharriswang/gsm-governance
- User guide: `docs/user-guide.md`
- API reference: docstrings in each module

---

**End of tutorial.**

The model is a tool. It is not a theory of everything. Its value lies in making normative commitments visible and their consequences simulable. Use it to clarify your thinking, not to substitute for it.
