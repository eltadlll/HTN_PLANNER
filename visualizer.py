"""
Two visualisation modes:
  1. print_tree()   – pretty text tree printed to stdout
  2. save_graphviz() – saves a .png decomposition tree via Graphviz (if installed)
"""

from htn_engine import DecompNode


# ─────────────────────────────────────────────
# 1. Text tree
# ─────────────────────────────────────────────

_BRANCH = "├── "
_LAST   = "└── "
_PIPE   = "│   "
_BLANK  = "    "

def _node_label(node: DecompNode) -> str:
    if node.task == "ROOT":
        return "🎯 ROOT"
    if node.method == "primitive":
        mark = "✅" if node.success else "❌"
        return f"{mark} [OP] {node.task}"
    method_str = f"  via «{node.method}»" if node.method else ""
    mark = "✅" if node.success else "❌"
    return f"{mark} [COMPOUND] {node.task}{method_str}"


def _print_subtree(node: DecompNode, prefix: str, is_last: bool):
    connector = _LAST if is_last else _BRANCH
    print(prefix + connector + _node_label(node))
    child_prefix = prefix + (_BLANK if is_last else _PIPE)
    for i, child in enumerate(node.children):
        _print_subtree(child, child_prefix, i == len(node.children) - 1)


def print_tree(root: DecompNode):
    """Print the decomposition tree to the console."""
    print("\n" + "=" * 60)
    print("  HTN DECOMPOSITION TREE")
    print("=" * 60)
    print(_node_label(root))
    for i, child in enumerate(root.children):
        _print_subtree(child, "", i == len(root.children) - 1)
    print("=" * 60 + "\n")


# ─────────────────────────────────────────────
# 2. Graphviz PNG
# ─────────────────────────────────────────────

def save_graphviz(root: DecompNode, filename: str = "decomp_tree"):
    """
    It save a .png decomposition tree.
    Requires the 'graphviz' Python package:  pip install graphviz
    AND the Graphviz system binary:          apt install graphviz
    It falls back to a text message if unavailable.
    """
    try:
        from graphviz import Digraph
    except ImportError:
        print("[visualizer] graphviz package not installed – skipping PNG export.")
        return

    dot = Digraph(
        name="HTN",
        graph_attr={"rankdir": "TB", "fontname": "Helvetica", "bgcolor": "#1a1a2e"},
        node_attr={"fontname": "Helvetica", "fontsize": "12", "style": "filled"},
        edge_attr={"color": "#aaaaaa"},
    )

    _counter = [0]

    def add_nodes(node: DecompNode, parent_id: str | None):
        node_id = f"n{_counter[0]}"
        _counter[0] += 1

        if node.task == "ROOT":
            dot.node(node_id, "ROOT", shape="diamond",
                     fillcolor="#e94560", fontcolor="white")
        elif node.method == "primitive":
            color = "#16213e" if node.success else "#c0392b"
            label = f"⚙ {node.task}"
            dot.node(node_id, label, shape="box",
                     fillcolor=color, fontcolor="#00d4ff")
        else:
            color = "#0f3460" if node.success else "#c0392b"
            method_line = f"\\n({node.method})" if node.method else ""
            label = f"◆ {node.task}{method_line}"
            dot.node(node_id, label, shape="ellipse",
                     fillcolor=color, fontcolor="#ffd460")

        if parent_id:
            dot.edge(parent_id, node_id)

        for child in node.children:
            add_nodes(child, node_id)

    add_nodes(root, None)

    try:
        dot.render(filename, format="png", cleanup=True)
        print(f"[visualizer] Saved decomposition tree → {filename}.png")
    except Exception as e:
        print(f"[visualizer] Could not render PNG: {e}")
