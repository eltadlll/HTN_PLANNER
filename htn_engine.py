"""
─────────────
Hand-built Hierarchical Task Network (HTN) planner.
No HTN library is used – every data-structure and algorithm is written here.
"""

from dataclasses import dataclass, field
from typing import Callable, Any



@dataclass
class Operator:
    """A primitive action the planner can execute directly."""
    name: str
    precondition: Callable[[dict], bool]   # state → bool
    effect:       Callable[[dict], dict]   # state → new_state


@dataclass
class Method:
    """
    One way to decompose a compound task.
    precondition : state guard – if False this method is skipped.
    subtasks     : ordered list of task names (string) to attempt next.
    """
    name:         str
    precondition: Callable[[dict], bool]
    subtasks:     list[str]


@dataclass
class CompoundTask:
    """A high-level task that must be decomposed via one of its methods."""
    name:    str
    methods: list[Method]


@dataclass
class DecompNode:
    """One node in the decomposition tree (for visualisation)."""
    task:     str
    method:   str | None          # None for primitive operators
    children: list["DecompNode"] = field(default_factory=list)
    success:  bool = True


# ─────────────────────────────────────────────
# The HTN Planner
# ─────────────────────────────────────────────

class HTNPlanner:
    """
    Recursive HTN planner.

    Algorithm (simplified SHOP-style):
      plan(tasks, state):
        if tasks is empty → return []
        t = tasks[0]
        if t is primitive:
            if precondition(state): apply effect; plan(rest, new_state)
            else: FAIL
        if t is compound:
            for each method of t (in order):
                if method.precondition(state):
                    result = plan(method.subtasks + rest, state)
                    if result is not FAIL: return result
            FAIL
    """

    def __init__(self):
        self.operators:       dict[str, Operator]      = {}
        self.compound_tasks:  dict[str, CompoundTask]  = {}
        self._decomp_log:     list[DecompNode]         = []   # internal trace

    # ── Registration helpers ──────────────────

    def add_operator(self, op: Operator):
        self.operators[op.name] = op

    def add_compound_task(self, ct: CompoundTask):
        self.compound_tasks[ct.name] = ct

    # ── Public entry point ────────────────────

    def plan(self, tasks: list[str], state: dict) -> tuple[list[str] | None, DecompNode]:
        """
        Returns (plan, tree_root).
        plan is None if planning failed.
        """
        root = DecompNode(task="ROOT", method=None)
        result_plan: list[str] = []
        ok = self._seek_plan(tasks, dict(state), result_plan, root)
        if not ok:
            root.success = False
            return None, root
        return result_plan, root

    # ── Recursive core ────────────────────────

    def _seek_plan(
        self,
        tasks:       list[str],
        state:       dict,
        result_plan: list[str],
        parent_node: DecompNode,
    ) -> bool:
        """
        Mutates result_plan in-place; returns True on success.
        state is copied at each branch so backtracking is automatic.
        """
        if not tasks:
            return True

        task_name = tasks[0]
        remaining = tasks[1:]

        # ── Primitive operator ────────────────
        if task_name in self.operators:
            op = self.operators[task_name]
            node = DecompNode(task=task_name, method="primitive")
            parent_node.children.append(node)

            if not op.precondition(state):
                node.success = False
                return False

            new_state = op.effect(dict(state))
            state.update(new_state)
            result_plan.append(task_name)
            return self._seek_plan(remaining, state, result_plan, parent_node)

        # ── Compound task ─────────────────────
        if task_name in self.compound_tasks:
            ct = self.compound_tasks[task_name]
            node = DecompNode(task=task_name, method=None)
            parent_node.children.append(node)

            for method in ct.methods:
                if method.precondition(state):
                    node.method = method.name
                    # Try this decomposition (deep-copy state for backtracking)
                    branch_state  = dict(state)
                    branch_plan:  list[str] = []
                    branch_node = DecompNode(task=task_name, method=method.name)

                    ok = self._seek_plan(
                        method.subtasks + remaining,
                        branch_state,
                        branch_plan,
                        branch_node,
                    )
                    if ok:
                        # Commit
                        node.method   = method.name
                        node.children = branch_node.children
                        state.update(branch_state)
                        result_plan.extend(branch_plan)
                        return True

            node.success = False
            return False

        raise ValueError(f"Unknown task: '{task_name}'")
