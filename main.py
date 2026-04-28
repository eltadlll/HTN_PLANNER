"""

Entry point.  Runs 3 scenarios through the HTN planner, prints results,
shows the decomposition tree, and animates execution.

Usage:
    python main.py                 # all scenarios, animated
    python main.py --no-animate    # skip the step-by-step delay
    python main.py --graphviz      # also export PNG trees (needs graphviz)
"""

import sys
from domain    import build_domain, SCENARIOS
from visualizer import print_tree, save_graphviz
from animator  import animate_plan



ANIMATE  = "--no-animate" not in sys.argv
GRAPHVIZ = "--graphviz"   in sys.argv
DELAY    = 0.5 if ANIMATE else 0.0


# ─────────────────────────────────────────────
# Run one scenario
# ─────────────────────────────────────────────

def run_scenario(name: str, state: dict):
    print("\n" + "█" * 60)
    print(f"  SCENARIO : {name.upper().replace('_', ' ')}")
    print("█" * 60)

    # Show initial conditions
    print("\nInitial Conditions:")
    for k, v in state.items():
        print(f"   {k:<22} = {v}")

    # Build domain & plan
    planner = build_domain()
    plan, tree = planner.plan(["DeliverPackage"], state)

    # Result
    if plan is None:
        print("\n❌  Planning FAILED – no valid plan found.")
    else:
        print(f"\n✅  Plan found  ({len(plan)} steps):")
        for i, step in enumerate(plan, 1):
            print(f"   {i:02d}. {step}")

    # Decomposition tree (text)
    print_tree(tree)

    # Optional PNG
    if GRAPHVIZ:
        save_graphviz(tree, filename=f"tree_{name}")

    # Animation
    if plan:
        animate_plan(plan, state, delay=DELAY)


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("   🤖  HTN ROBOT DELIVERY PLANNER")
    print("=" * 60)
    print("Domain  : Robot Delivery")
    print("Engine  : Hand-built recursive HTN (no HTN libraries)")
    print("Scenarios:", list(SCENARIOS.keys()))
    print()

    for scenario_name, initial_state in SCENARIOS.items():
        run_scenario(scenario_name, initial_state)

    print("\nDone. Run with --graphviz to export PNG decomposition trees.\n")


if __name__ == "__main__":
    main()
