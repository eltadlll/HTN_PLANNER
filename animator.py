

import time
from domain import build_domain, SCENARIOS



class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    GREY   = "\033[90m"
    BLUE   = "\033[94m"


def _fmt_state(state: dict) -> str:
    lines = []
    icons = {
        "robot_location":   "🤖",
        "package_location": "📦",
        "has_car":          "🚗",
        "car_fuelled":      "⛽",
        "robot_charged":    "🔋",
        "door_locked":      "🔒",
    }
    for k, v in state.items():
        icon = icons.get(k, "  ")
        val_str = str(v)
        if v is True:
            val_str = C.GREEN + "True" + C.RESET
        elif v is False:
            val_str = C.RED + "False" + C.RESET
        else:
            val_str = C.CYAN + val_str + C.RESET
        lines.append(f"   {icon}  {k:<20} = {val_str}")
    return "\n".join(lines)



def animate_plan(plan: list[str], initial_state: dict, delay: float = 0.6):
    
    planner = build_domain()
    state   = dict(initial_state)

    print("\n" + C.BOLD + C.BLUE + "━" * 60 + C.RESET)
    print(C.BOLD + "  🎬  STEP-BY-STEP PLAN EXECUTION" + C.RESET)
    print(C.BOLD + C.BLUE + "━" * 60 + C.RESET)
    print(C.GREY + "\nInitial world state:" + C.RESET)
    print(_fmt_state(state))
    print()

    for step_num, task_name in enumerate(plan, start=1):
        time.sleep(delay)
        print(C.YELLOW + C.BOLD + f"  Step {step_num:02d}  ▶  {task_name}" + C.RESET)

        op = planner.operators[task_name]

        if not op.precondition(state):
            print(C.RED + "  ✗ Precondition FAILED – this should not happen!" + C.RESET)
            return

        new_state = op.effect(dict(state))

        # Show what changed
        changed = {k: new_state[k] for k in new_state if new_state.get(k) != state.get(k)}
        if changed:
            for k, v in changed.items():
                old = state.get(k)
                print(C.GREY + f"      {k}: " + C.RED + str(old) +
                      C.GREY + " → " + C.GREEN + str(v) + C.RESET)

        state = new_state
        print()

    print(C.GREEN + C.BOLD + "  ✅  DELIVERY COMPLETE!" + C.RESET)
    print(C.GREY + "\nFinal world state:" + C.RESET)
    print(_fmt_state(state))
    print(C.BOLD + C.BLUE + "━" * 60 + C.RESET + "\n")
