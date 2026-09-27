"""
Visualization utilities for GSM-J.
Requires matplotlib (optional dependency).
"""

from __future__ import annotations

import numpy as np

from gsm_governance.core.parameters import JUSTICE_DIMENSIONS
from gsm_governance.core.system import MultiLevelGovernance


def _require_matplotlib():
    try:
        import matplotlib.pyplot as plt  # noqa
    except ImportError:
        raise ImportError(
            "matplotlib is required for visualization; "
            "install with: pip install gsm-governance[viz]"
        )


# ===========================================================================
# Trajectory plots
# ===========================================================================

def plot_welfare(
    history: list[dict],
    save_path: str | None = None,
) -> None:
    _require_matplotlib()
    import matplotlib.pyplot as plt

    times = [r["t"] for r in history]
    w = [r["W_star"] for r in history]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(times, w, lw=2)
    ax.set_xlabel("Time")
    ax.set_ylabel("W*")
    ax.set_title("Welfare trajectory")
    ax.grid(alpha=0.3)
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)


def plot_dimension_trajectories(
    history: list[dict],
    save_path: str | None = None,
) -> None:
    _require_matplotlib()
    import matplotlib.pyplot as plt

    times = [r["t"] for r in history]
    fig, ax = plt.subplots(figsize=(10, 6))
    for d in JUSTICE_DIMENSIONS:
        series = [r["dim_means"][d] for r in history]
        ax.plot(times, series, label=d, lw=2)
    ax.set_xlabel("Time")
    ax.set_ylabel("Mean justice dimension")
    ax.set_title("Justice dimension trajectories")
    ax.legend(loc="best")
    ax.grid(alpha=0.3)
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)


def plot_interventions(
    history: list[dict],
    save_path: str | None = None,
) -> None:
    _require_matplotlib()
    import matplotlib.pyplot as plt

    times = [r["t"] for r in history]
    active = [r["active_interventions"] for r in history]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(times, active, lw=2)
    ax.set_xlabel("Time")
    ax.set_ylabel("Active interventions")
    ax.set_title("Intervention activity")
    ax.grid(alpha=0.3)
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)


# ===========================================================================
# Radar chart
# ===========================================================================

def plot_justice_radar(
    governance: MultiLevelGovernance,
    uids: list[str],
    save_path: str | None = None,
) -> None:
    _require_matplotlib()
    import matplotlib.pyplot as plt

    angles = np.linspace(0, 2 * np.pi,
                         len(JUSTICE_DIMENSIONS), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
    for uid in uids:
        if uid not in governance.jurisdictions:
            continue
        j = governance.jurisdictions[uid]
        values = [j.state.justice.d[d] for d in JUSTICE_DIMENSIONS]
        values += values[:1]
        ax.plot(angles, values, label=uid, linewidth=2)
        ax.fill(angles, values, alpha=0.15)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([d.capitalize() for d in JUSTICE_DIMENSIONS])
    ax.set_ylim(0, 1)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    ax.set_title("Justice profile")
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)