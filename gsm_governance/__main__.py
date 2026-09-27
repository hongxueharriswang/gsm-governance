"""Demonstration entry point: python -m gsm_governance."""

from __future__ import annotations

from gsm_governance.core.parameters import (
    JUSTICE_DIMENSIONS,
    GSMConfig,
    JusticeInteractionMatrix,
    MJRegime,
)
from gsm_governance.core.state import JusticeState
from gsm_governance.core.system import MultiLevelGovernance
from gsm_governance.dynamics.simulation import Simulation


def _build_demo() -> Simulation:
    config = GSMConfig()
    gov = MultiLevelGovernance(config=config)

    # Levels: global (6), regional (5), national (4), community (2)
    gov.add_jurisdiction("G", level=6)
    gov.add_jurisdiction("R1", level=5)
    gov.add_jurisdiction("R2", level=5)
    for nid in ("N1", "N2", "N3"):
        gov.add_jurisdiction(nid, level=4)

    communities = {
        "C1": {"distributive": 0.55, "procedural": 0.50, "recognition": 0.20,
               "corrective": 0.20, "intergenerational": 0.40},
        "C2": {"distributive": 0.60, "procedural": 0.55, "recognition": 0.40,
               "corrective": 0.25, "intergenerational": 0.45},
        "C3": {"distributive": 0.45, "procedural": 0.40, "recognition": 0.22,
               "corrective": 0.15, "intergenerational": 0.30},
        "C4": {"distributive": 0.65, "procedural": 0.60, "recognition": 0.50,
               "corrective": 0.35, "intergenerational": 0.55},
        "C5": {"distributive": 0.50, "procedural": 0.45, "recognition": 0.30,
               "corrective": 0.08, "intergenerational": 0.35},
        "C6": {"distributive": 0.55, "procedural": 0.50, "recognition": 0.40,
               "corrective": 0.25, "intergenerational": 0.40},
    }
    for uid, vals in communities.items():
        gov.add_jurisdiction(uid, level=2, justice=JusticeState(vals))

    for p, c in [("G", "R1"), ("G", "R2"),
                 ("R1", "N1"), ("R1", "N2"), ("R2", "N3"),
                 ("N1", "C1"), ("N1", "C2"),
                 ("N2", "C3"), ("N2", "C4"),
                 ("N3", "C5"), ("N3", "C6")]:
        gov.link_vertical(p, c)

    for a, b in [("R1", "R2"), ("N1", "N2"), ("N2", "N3"),
                 ("C1", "C2"), ("C3", "C4"), ("C5", "C6")]:
        gov.link_horizontal(a, b)

    sim = Simulation(
        gov, config,
        M_J=JusticeInteractionMatrix(regime=MJRegime.SYMMETRIC),
    )
    # Inject exploitation with partial compensation
    sim.set_exploitation("N1", "C1", {
        "distributive": 0.30, "procedural": 0.20, "recognition": 0.10,
        "corrective": 0.00, "intergenerational": 0.15,
    })
    sim.set_compensation("N1", "C1", {
        "distributive": 0.15, "procedural": 0.05, "recognition": 0.00,
        "corrective": 0.00, "intergenerational": 0.05,
    })
    return sim


def _summarize(history, label=""):
    if not history:
        print(f"[{label}] empty history")
        return
    last = history[-1]
    print(f"--- {label} ---")
    print(f"  steps         : {len(history)}")
    print(f"  t             : {last['t']:.2f}")
    print(f"  W*            : {last['W_star']:.4f}")
    print(f"  mean justice  : {last['mean_justice']:.4f}")
    print(f"  C2 violations : {last['C2_violations']}")
    print(f"  C3 violations : {last['C3_violations']}")
    print(f"  C4 violations : {last['C4_violations']}")
    print(f"  active ivs    : {last['active_interventions']}")
    print(f"  cum. cost     : {last['total_cost']:.4f}")


def _print_profile(sim: Simulation):
    print("Justice profile (per jurisdiction):")
    print("  " + "uid".ljust(6)
          + "".join(d[:4].rjust(8) for d in JUSTICE_DIMENSIONS)
          + "".join(k.rjust(8) for k in ("A", "C", "S", "T", "L")))
    for uid in sorted(sim.governance.jurisdictions.keys()):
        j = sim.governance.jurisdictions[uid]
        row = "  " + uid.ljust(6)
        for d in JUSTICE_DIMENSIONS:
            row += f"{j.state.justice.d[d]:8.3f}"
        for k in ("A", "C", "S", "T", "L"):
            row += f"{getattr(j.state, k):8.3f}"
        print(row)


def main():
    print("=" * 72)
    print("GSM-J v0.3.0 — demonstration run")
    print("=" * 72)

    sim = _build_demo()
    history = sim.run(steps=400)

    _summarize(history, "GSM-J v0.3.0 default")
    print()
    _print_profile(sim)
    print()
    print("Intervention statistics:")
    for k, v in sim.enforcer.stats.items():
        if isinstance(v, float):
            print(f"  {k:12s}: {v:.4f}")
        else:
            print(f"  {k:12s}: {v}")

    print()
    print("=" * 72)
    print("Comparison: single-channel vs. multi-channel intervention cost")
    print("=" * 72)

    for label, weights in (
        ("single-channel (v0.2.0 style)",
         {"C": 1.0, "S": 0.0, "T": 0.0, "A": 0.0}),
        ("multi-channel (v0.3.0 default)",
         {"C": 0.50, "S": 0.25, "T": 0.15, "A": 0.10}),
    ):
        cfg = GSMConfig(intervention_weights=weights)
        gov = MultiLevelGovernance(config=cfg)
        # Rebuild identical hierarchy
        gov.add_jurisdiction("G", level=6)
        gov.add_jurisdiction("R1", level=5)
        gov.add_jurisdiction("R2", level=5)
        for nid in ("N1", "N2", "N3"):
            gov.add_jurisdiction(nid, level=4)
        communities = {
            "C1": {"distributive": 0.55, "procedural": 0.50, "recognition": 0.20,
                   "corrective": 0.20, "intergenerational": 0.40},
            "C2": {"distributive": 0.60, "procedural": 0.55, "recognition": 0.40,
                   "corrective": 0.25, "intergenerational": 0.45},
            "C3": {"distributive": 0.45, "procedural": 0.40, "recognition": 0.22,
                   "corrective": 0.15, "intergenerational": 0.30},
            "C4": {"distributive": 0.65, "procedural": 0.60, "recognition": 0.50,
                   "corrective": 0.35, "intergenerational": 0.55},
            "C5": {"distributive": 0.50, "procedural": 0.45, "recognition": 0.30,
                   "corrective": 0.08, "intergenerational": 0.35},
            "C6": {"distributive": 0.55, "procedural": 0.50, "recognition": 0.40,
                   "corrective": 0.25, "intergenerational": 0.40},
        }
        for uid, vals in communities.items():
            gov.add_jurisdiction(uid, level=2, justice=JusticeState(vals))
        for p, c in [("G", "R1"), ("G", "R2"),
                     ("R1", "N1"), ("R1", "N2"), ("R2", "N3"),
                     ("N1", "C1"), ("N1", "C2"),
                     ("N2", "C3"), ("N2", "C4"),
                     ("N3", "C5"), ("N3", "C6")]:
            gov.link_vertical(p, c)
        for a, b in [("R1", "R2"), ("N1", "N2"), ("N2", "N3"),
                     ("C1", "C2"), ("C3", "C4"), ("C5", "C6")]:
            gov.link_horizontal(a, b)
        sim_x = Simulation(gov, cfg)
        sim_x.set_exploitation("N1", "C1", {
            "distributive": 0.30, "procedural": 0.20, "recognition": 0.10,
            "corrective": 0.00, "intergenerational": 0.15,
        })
        sim_x.set_compensation("N1", "C1", {
            "distributive": 0.15, "procedural": 0.05, "recognition": 0.00,
            "corrective": 0.00, "intergenerational": 0.05,
        })
        hist_x = sim_x.run(steps=400)
        _summarize(hist_x, label)
        print()


if __name__ == "__main__":
    main()