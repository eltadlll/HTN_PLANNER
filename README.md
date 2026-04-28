# 🤖 HTN Robot Delivery Planner

A hand-built **Hierarchical Task Network (HTN)** planner in Python — no HTN libraries used. Every data structure and algorithm is written from scratch.

---

## 📁 File Structure

```
htn_project/
├── htn_engine.py   ← The HTN engine (Operator, Method, CompoundTask, HTNPlanner)
├── domain.py       ← Robot Delivery domain: tasks, operators, scenarios
├── visualizer.py   ← Text tree + optional Graphviz PNG export
├── animator.py     ← Step-by-step coloured console execution
├── main.py         ← Entry point — runs all 3 scenarios
└── README.md       ← This file
```

---

## 🧠 What is an HTN Planner?

An **HTN (Hierarchical Task Network)** planner decomposes high-level goals into low-level executable actions.

```
Goal: DeliverPackage
  └── Method: full_delivery
        ├── GetPackage          ← Compound task
        │     └── pick_up_package  ← Primitive operator
        ├── TravelToCustomer    ← Compound task
        │     └── drive_to_customer OR walk_to_customer
        ├── knock_on_door       ← Primitive operator
        └── hand_over_package   ← Primitive operator
```

The planner **chooses between alternative methods based on the current world state** (e.g., drive if a car is available, walk if not).

---

## 🌍 Domain: Robot Delivery

A robot must deliver a package from a warehouse to a customer's door.

### World State

| Key               | Type   | Meaning                          |
|-------------------|--------|----------------------------------|
| `robot_location`  | string | warehouse / customer             |
| `package_location`| string | warehouse / robot / customer     |
| `has_car`         | bool   | Car available in garage          |
| `car_fuelled`     | bool   | Car has fuel                     |
| `robot_charged`   | bool   | Robot battery is full            |
| `door_locked`     | bool   | Customer's front door is locked  |

### ◆ Compound Tasks (3)

| Task              | Methods                                              |
|-------------------|------------------------------------------------------|
| `DeliverPackage`  | `full_delivery` (always applicable)                  |
| `GetPackage`      | `charge_then_pick_up` OR `pick_up_directly`          |
| `TravelToCustomer`| `fuel_then_drive` OR `drive` OR `walk`               |

### ⚙ Primitive Operators (7)

| Operator            | Precondition                                  | Effect                        |
|---------------------|-----------------------------------------------|-------------------------------|
| `charge_robot`      | robot not charged                             | robot_charged = True          |
| `pick_up_package`   | at warehouse, package there, robot charged    | package_location = robot      |
| `fuel_car`          | has_car, car not fuelled                      | car_fuelled = True            |
| `drive_to_customer` | has_car, car fuelled, carrying package        | robot_location = customer     |
| `walk_to_customer`  | carrying package                              | robot_location = customer     |
| `knock_on_door`     | at customer, door locked                      | door_locked = False           |
| `hand_over_package` | at customer, carrying package, door open      | package_location = customer   |

---

## 🔄 Dynamic Logic (Method Selection)

The planner evaluates **method preconditions** in order and picks the **first applicable** one:

```
TravelToCustomer:
  ┌─ has_car AND NOT car_fuelled  →  fuel_then_drive  (fuel up, then drive)
  ├─ has_car AND car_fuelled      →  drive            (drive directly)
  └─ NOT has_car                  →  walk             (walk to customer)
```

This is the core of HTN intelligence — the same goal produces **different plans** depending on world state.

---

## 🚀 How to Run

### Requirements

```bash
pip install graphviz   # optional — only for PNG export
```

> **Core planner has zero dependencies** — it uses only Python standard library.

### Run all scenarios

```bash
python main.py
```

### Skip animation delay

```bash
python main.py --no-animate
```

### Also export PNG decomposition trees (requires graphviz binary)

```bash
# Install system graphviz first:
#   Ubuntu/Debian: sudo apt install graphviz
#   macOS:         brew install graphviz

python main.py --graphviz
```

---

## 📊 Sample Output

### Scenario: `with_car` (car available but needs fuelling, robot not charged)

**Plan found (6 steps):**
```
01. charge_robot
02. pick_up_package
03. fuel_car
04. drive_to_customer
05. knock_on_door
06. hand_over_package
```

**Decomposition Tree:**
```
🎯 ROOT
└── ✅ [COMPOUND] DeliverPackage  via «full_delivery»
    └── ✅ [COMPOUND] GetPackage  via «charge_then_pick_up»
        ├── ✅ [OP] charge_robot
        ├── ✅ [OP] pick_up_package
        └── ✅ [COMPOUND] TravelToCustomer  via «fuel_then_drive»
            ├── ✅ [OP] fuel_car
            ├── ✅ [OP] drive_to_customer
            ├── ✅ [OP] knock_on_door
            └── ✅ [OP] hand_over_package
```

### Scenario: `no_car` (no car, robot already charged)

**Plan found (4 steps):**
```
01. pick_up_package
02. walk_to_customer
03. knock_on_door
04. hand_over_package
```

**Decomposition Tree:**
```
🎯 ROOT
└── ✅ [COMPOUND] DeliverPackage  via «full_delivery»
    └── ✅ [COMPOUND] GetPackage  via «pick_up_directly»
        ├── ✅ [OP] pick_up_package
        └── ✅ [COMPOUND] TravelToCustomer  via «walk»
            ├── ✅ [OP] walk_to_customer
            ├── ✅ [OP] knock_on_door
            └── ✅ [OP] hand_over_package
```

---

## 🏗 Architecture

### `htn_engine.py` — The Core

```
Operator       – name, precondition(state)→bool, effect(state)→state
Method         – name, precondition(state)→bool, subtasks: [str]
CompoundTask   – name, methods: [Method]
DecompNode     – tree node for visualisation
HTNPlanner     – add_operator(), add_compound_task(), plan()
```

### Recursive Algorithm (`_seek_plan`)

```python
def _seek_plan(tasks, state, result_plan, parent_node):
    if tasks is empty:
        return SUCCESS

    task = tasks[0]
    rest = tasks[1:]

    if task is PRIMITIVE:
        if precondition(state):
            apply effect to state
            append task to plan
            return _seek_plan(rest, state, ...)
        else:
            return FAIL

    if task is COMPOUND:
        for each method:
            if method.precondition(state):
                result = _seek_plan(method.subtasks + rest, copy(state), ...)
                if result is SUCCESS:
                    return SUCCESS   # commit
        return FAIL
```

State is **deep-copied at each branch** so failed attempts don't corrupt the world state (automatic backtracking).

---

## 🎨 Visualisation Modes

| Mode            | How                          | Output                              |
|-----------------|------------------------------|-------------------------------------|
| Text tree       | Always on                    | Printed to console with unicode     |
| Graphviz PNG    | `--graphviz` flag            | `tree_<scenario>.png` files         |
| Step animation  | Always on (disable: `--no-animate`) | Coloured console with state diffs |

---

## 💡 Key Design Decisions

1. **No HTN library** — `HTNPlanner`, `Operator`, `Method`, `CompoundTask`, `DecompNode` all hand-coded.
2. **State as plain dict** — easy to read, copy, and diff.
3. **Lambdas for preconditions/effects** — keeps domain definitions readable.
4. **Backtracking via deep copy** — clean and simple, no undo stack needed.
5. **Separation of concerns** — engine / domain / visualizer / animator are fully decoupled.
