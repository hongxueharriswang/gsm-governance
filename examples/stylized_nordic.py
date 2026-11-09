"""End-to-end example using the stylized-Nordic illustration of Section 6.

Illustrative only. Uses profiles from gsm_governance.data that are
pedagogical, not empirical.
"""
from gsm_governance import GSMConfig, Simulation, load_stylized_nordic


def main():
    config = GSMConfig(seed=42)
    jurisdictions = load_stylized_nordic()
    sim = Simulation(config, jurisdictions)
    history = sim.run(n_steps=20)

    print(f"Configuration: welfare_mode={config.welfare_mode}, "
          f"phi_vuln={config.phi_vuln}, symmetry={config.symmetry}")
    print(f"Prioritarian: {sim.welfare.is_prioritarian()}")
    print()
    print(f"{'t':>3} {'welfare':>10} {'base':>10} {'expl':>8} "
          f"{'c1':>3} {'c2':>3} {'c3':>3} {'c4':>3}")
    for row in history:
        v = row["violations"]
        print(f"{row['t']:>3} {row['welfare']['total']:>10.4f} "
              f"{row['welfare']['base']:>10.4f} "
              f"{row['welfare']['exploitation_penalty']:>8.4f} "
              f"{len(v['c1']):>3} {len(v['c2']):>3} "
              f"{len(v['c3']):>3} {len(v['c4']):>3}")
    print()
    print("Final justice by jurisdiction:")
    for j in jurisdictions:
        parts = "  ".join(
            f"{d[:4]}={j.state.justice[d]:.3f}" for d in j.state.justice)
        print(f"  {j.id:>14}  {parts}")


if __name__ == "__main__":
    main()
