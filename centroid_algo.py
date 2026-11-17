from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import sys


@dataclass
class DFSEvent:
    kind: str
    u: int
    v: Optional[int] = None
    size_u: Optional[int] = None


@dataclass
class SearchStep:
    u: int
    parent: int
    checked_children: List[Tuple[int, int, bool]]
    next_node: int


@dataclass
class CentroidTrace:
    n: int
    root: int
    edges: List[Tuple[int, int]]
    adj: Dict[int, List[int]]
    sizes: Dict[int, int]
    parent_map: Dict[int, int]
    dfs_events: List[DFSEvent] = field(default_factory=list)
    greedy_steps: List[SearchStep] = field(default_factory=list)
    centroid: int = -1
    components_after_removal: List[List[int]] = field(default_factory=list)


def find_centroid_with_trace(
    n: int, edges: List[Tuple[int, int]], root: int = 1
) -> CentroidTrace:
    G: List[List[int]] = [[] for _ in range(n + 1)]
    for u, v in edges:
        G[u].append(v)
        G[v].append(u)

    sizes: List[int] = [-1] * (n + 1)
    parent_map: Dict[int, int] = {root: -1}
    dfs_events: List[DFSEvent] = []

    def dfs(u: int) -> int:
        sizes[u] = 1
        dfs_events.append(DFSEvent(kind="enter", u=u))
        for v in G[u]:
            if sizes[v] != -1:
                continue
            parent_map[v] = u
            dfs_events.append(DFSEvent(kind="edge", u=u, v=v))
            sizes[u] += dfs(v)
        dfs_events.append(DFSEvent(kind="size", u=u, size_u=sizes[u]))
        return sizes[u]

    dfs(root)

    u = root
    p = -1
    greedy_steps: List[SearchStep] = []

    while True:
        next_node = -1
        checked: List[Tuple[int, int, bool]] = []
        for v in G[u]:
            if v == p:
                continue
            is_heavy = sizes[v] > n // 2
            checked.append((v, sizes[v], is_heavy))
            if is_heavy and next_node == -1:
                next_node = v
                break

        greedy_steps.append(
            SearchStep(
                u=u,
                parent=p,
                checked_children=checked,
                next_node=next_node,
            )
        )

        if next_node == -1:
            centroid = u
            break
        p = u
        u = next_node

    visited = [False] * (n + 1)
    visited[centroid] = True
    components: List[List[int]] = []

    for neighbor in G[centroid]:
        if not visited[neighbor]:
            comp: List[int] = []
            stack = [neighbor]
            visited[neighbor] = True
            while stack:
                curr = stack.pop()
                comp.append(curr)
                for nxt in G[curr]:
                    if not visited[nxt]:
                        visited[nxt] = True
                        stack.append(nxt)
            components.append(comp)

    return CentroidTrace(
        n=n,
        root=root,
        edges=edges,
        adj={i: list(G[i]) for i in range(1, n + 1)},
        sizes={i: sizes[i] for i in range(1, n + 1)},
        parent_map=parent_map,
        dfs_events=dfs_events,
        greedy_steps=greedy_steps,
        centroid=centroid,
        components_after_removal=components,
    )


def get_subtree_nodes(trace: CentroidTrace, sub_root: int) -> List[int]:
    result: List[int] = []
    stack = [sub_root]
    while stack:
        curr = stack.pop()
        result.append(curr)
        for nxt in trace.adj[curr]:
            if trace.parent_map.get(nxt) == curr:
                stack.append(nxt)
    return result


DEMO_TREE_N = 9
DEMO_TREE_EDGES: List[Tuple[int, int]] = [
    (1, 2),
    (2, 3),
    (2, 4),
    (4, 5),
    (5, 8),
    (5, 9),
    (4, 6),
    (6, 7),
]

STAR_TREE_N = 7
STAR_TREE_EDGES: List[Tuple[int, int]] = [
    (2, 1),
    (2, 3),
    (2, 4),
    (2, 5),
    (2, 6),
    (2, 7),
]


if __name__ == "__main__":
    if not sys.stdin.isatty():
        data = sys.stdin.read().split()
        if data:
            n_in = int(data[0])
            edges_in = []
            idx = 1
            for _ in range(n_in - 1):
                u_in = int(data[idx])
                v_in = int(data[idx + 1])
                edges_in.append((u_in, v_in))
                idx += 2
            tr = find_centroid_with_trace(n_in, edges_in, root=1)
            print(f"Centroide: {tr.centroid}")
            sys.exit(0)

    demo = find_centroid_with_trace(DEMO_TREE_N, DEMO_TREE_EDGES, root=1)
    print(f"Centroide demo: {demo.centroid}")
    star = find_centroid_with_trace(STAR_TREE_N, STAR_TREE_EDGES, root=1)
    print(f"Centroide estrella: {star.centroid}")
