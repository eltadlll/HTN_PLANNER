"""
domain.py
─────────
Robot Delivery Domain
─────────────────────
A robot must deliver a package from the warehouse to a customer.

World state keys
────────────────
  robot_location   : "warehouse" | "garage" | "street" | "customer"
  package_location : "warehouse" | "robot" | "customer"
  has_car          : bool   – car available in garage
  car_fuelled      : bool
  robot_charged    : bool
  door_locked      : bool   – customer's front door

Compound tasks (3+)
────────────────────
  DeliverPackage   – top-level goal
  GetPackage       – go to warehouse and pick up package
  TravelToCustomer – drive or walk to customer's location

Primitive operators (5+)
─────────────────────────
  charge_robot
  pick_up_package
  fuel_car
  drive_to_customer
  walk_to_customer
  knock_on_door
  hand_over_package
"""

from htn_engine import HTNPlanner, Operator, Method, CompoundTask


def build_domain() -> HTNPlanner:
    planner = HTNPlanner()

    # ─────────────────────────────────────────
    # Primitive Operators
    # ─────────────────────────────────────────

    planner.add_operator(Operator(
        name="charge_robot",
        precondition=lambda s: not s["robot_charged"],
        effect=lambda s: {**s, "robot_charged": True},
    ))

    planner.add_operator(Operator(
        name="pick_up_package",
        precondition=lambda s: (
            s["robot_location"] == "warehouse"
            and s["package_location"] == "warehouse"
            and s["robot_charged"]
        ),
        effect=lambda s: {**s, "package_location": "robot"},
    ))

    planner.add_operator(Operator(
        name="fuel_car",
        precondition=lambda s: s["has_car"] and not s["car_fuelled"],
        effect=lambda s: {**s, "car_fuelled": True},
    ))

    planner.add_operator(Operator(
        name="drive_to_customer",
        precondition=lambda s: (
            s["has_car"]
            and s["car_fuelled"]
            and s["package_location"] == "robot"
        ),
        effect=lambda s: {**s, "robot_location": "customer"},
    ))

    planner.add_operator(Operator(
        name="walk_to_customer",
        precondition=lambda s: s["package_location"] == "robot",
        effect=lambda s: {**s, "robot_location": "customer"},
    ))

    planner.add_operator(Operator(
        name="knock_on_door",
        precondition=lambda s: (
            s["robot_location"] == "customer"
            and s["door_locked"]
        ),
        effect=lambda s: {**s, "door_locked": False},
    ))

    planner.add_operator(Operator(
        name="hand_over_package",
        precondition=lambda s: (
            s["robot_location"] == "customer"
            and s["package_location"] == "robot"
            and not s["door_locked"]
        ),
        effect=lambda s: {**s, "package_location": "customer"},
    ))

    # ─────────────────────────────────────────
    # Compound Tasks
    # ─────────────────────────────────────────

    # 1. GetPackage – pick up from warehouse (charge first if needed)
    planner.add_compound_task(CompoundTask(
        name="GetPackage",
        methods=[
            Method(
                name="charge_then_pick_up",
                precondition=lambda s: not s["robot_charged"],
                subtasks=["charge_robot", "pick_up_package"],
            ),
            Method(
                name="pick_up_directly",
                precondition=lambda s: s["robot_charged"],
                subtasks=["pick_up_package"],
            ),
        ],
    ))

    # 2. TravelToCustomer – drive if car available & fuelled-up, else walk
    planner.add_compound_task(CompoundTask(
        name="TravelToCustomer",
        methods=[
            Method(
                name="fuel_then_drive",
                precondition=lambda s: s["has_car"] and not s["car_fuelled"],
                subtasks=["fuel_car", "drive_to_customer"],
            ),
            Method(
                name="drive",
                precondition=lambda s: s["has_car"] and s["car_fuelled"],
                subtasks=["drive_to_customer"],
            ),
            Method(
                name="walk",
                precondition=lambda s: not s["has_car"],
                subtasks=["walk_to_customer"],
            ),
        ],
    ))

    # 3. DeliverPackage – full delivery pipeline
    planner.add_compound_task(CompoundTask(
        name="DeliverPackage",
        methods=[
            Method(
                name="full_delivery",
                precondition=lambda s: True,   # always applicable
                subtasks=[
                    "GetPackage",
                    "TravelToCustomer",
                    "knock_on_door",
                    "hand_over_package",
                ],
            ),
        ],
    ))

    return planner


# ─────────────────────────────────────────────
# Example initial states
# ─────────────────────────────────────────────

SCENARIOS = {
    "with_car": {
        "robot_location":   "warehouse",
        "package_location": "warehouse",
        "has_car":          True,
        "car_fuelled":      False,
        "robot_charged":    False,
        "door_locked":      True,
    },
    "no_car": {
        "robot_location":   "warehouse",
        "package_location": "warehouse",
        "has_car":          False,
        "car_fuelled":      False,
        "robot_charged":    True,
        "door_locked":      True,
    },
    "ready_to_go": {
        "robot_location":   "warehouse",
        "package_location": "warehouse",
        "has_car":          True,
        "car_fuelled":      True,
        "robot_charged":    True,
        "door_locked":      True,
    },
}
