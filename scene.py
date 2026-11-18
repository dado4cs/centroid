from typing import Dict, List, Tuple
import numpy as np
from manim import *

from centroid_algo import (
    DEMO_TREE_EDGES,
    DEMO_TREE_N,
    STAR_TREE_EDGES,
    STAR_TREE_N,
    CentroidTrace,
    find_centroid_with_trace,
    get_subtree_nodes,
)

# Paleta de colores editorial
DESK_BG = "#F3B391"
PAPER_BG = "#FAF6F0"
PAPER_SHADOW = "#D99B79"
CARD_BG = "#F2ECE1"
CARD_BORDER = "#DFD5C5"

INK_DARK = "#3D3834"
INK_MUTED = "#7A7267"
EDGE_COLOR = "#6E665E"

TOKEN_BLUE = ("#2E90E8", "#1B62A8")
TOKEN_RED = ("#D94826", "#962B12")
TOKEN_GREEN = ("#2A9D6F", "#196646")
TOKEN_AMBER = ("#E58E26", "#9E5B0D")
TOKEN_FADED = ("#CFC7BC", "#ABA296")

config.background_color = PAPER_BG

# Plantilla LaTeX con article.cls
_custom_tex_template = TexTemplate(
    documentclass=r"\documentclass{article}",
    preamble=(
        r"\pagestyle{empty}"
        "\n"
        r"\usepackage[utf8]{inputenc}"
        "\n"
        r"\usepackage[T1]{fontenc}"
        "\n"
        r"\usepackage{amsmath}"
        "\n"
        r"\usepackage{amssymb}"
    ),
)
config.tex_template = _custom_tex_template


# Lienzo base con estética de papel
def create_paper_stage(
    scene: Scene, header_text: str = r"\infty\;\text{cs2023}\cdot\text{utec}"
) -> VGroup:
    config.tex_template = _custom_tex_template
    desk = FullScreenRectangle(
        fill_color=DESK_BG, fill_opacity=1.0, stroke_width=0)
    shadow = RoundedRectangle(
        width=13.5,
        height=7.35,
        corner_radius=0.12,
        fill_color=PAPER_SHADOW,
        fill_opacity=0.65,
        stroke_width=0,
    ).shift(0.08 * DOWN + 0.08 * RIGHT)

    sheet = RoundedRectangle(
        width=13.5,
        height=7.35,
        corner_radius=0.12,
        fill_color=PAPER_BG,
        fill_opacity=1.0,
        stroke_color="#E8DFD1",
        stroke_width=2.0,
    )

    header = MathTex(header_text, color=INK_MUTED, font_size=22)
    header.move_to(sheet.get_top() + 0.28 * DOWN)

    stage = VGroup(desk, shadow, sheet, header)
    stage.set_z_index(-10)
    scene.add(stage)
    return stage


# Nodo del árbol con relieve 2.5D
class TokenNode(VGroup):
    def __init__(
        self,
        node_id: int,
        pos: np.ndarray,
        radius: float = 0.30,
        palette: Tuple[str, str] = TOKEN_BLUE,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.node_id = node_id
        self.radius = radius
        top_col, base_col = palette

        self.base_disk = Circle(
            radius=radius,
            fill_color=base_col,
            fill_opacity=1.0,
            stroke_color=base_col,
            stroke_width=1.5,
        ).shift(0.065 * DOWN + 0.015 * RIGHT)

        self.top_disk = Circle(
            radius=radius,
            fill_color=top_col,
            fill_opacity=1.0,
            stroke_color=base_col,
            stroke_width=2.5,
        )

        self.label = MathTex(str(node_id), color=PAPER_BG,
                             font_size=int(radius * 92))
        self.label.move_to(self.top_disk.get_center())

        self.add(self.base_disk, self.top_disk, self.label)
        self.move_to(pos)
        self.set_z_index(5)

    def recolor_anim(self, palette: Tuple[str, str], label_color: str = PAPER_BG):
        top_col, base_col = palette
        return AnimationGroup(
            self.base_disk.animate.set_fill(
                base_col, opacity=1.0).set_stroke(base_col),
            self.top_disk.animate.set_fill(
                top_col, opacity=1.0).set_stroke(base_col),
            self.label.animate.set_color(label_color),
        )


# Estructura visual del árbol y sus componentes
class TreeVisual(VGroup):
    def __init__(
        self,
        n: int,
        edges: List[Tuple[int, int]],
        positions: Dict[int, np.ndarray],
        node_radius: float = 0.29,
    ):
        super().__init__()
        self.n = n
        self.edges_list = edges
        self.positions = positions
        self.nodes: Dict[int, TokenNode] = {}
        self.edges: Dict[Tuple[int, int], Line] = {}
        self.size_badges: Dict[int, VGroup] = {}

        edges_group = VGroup()
        for u, v in edges:
            line = Line(
                positions[u],
                positions[v],
                color=EDGE_COLOR,
                stroke_width=4.0,
            )
            line.set_z_index(1)
            self.edges[(u, v)] = line
            self.edges[(v, u)] = line
            edges_group.add(line)

        nodes_group = VGroup()
        for i in range(1, n + 1):
            tok = TokenNode(
                i, positions[i], radius=node_radius, palette=TOKEN_BLUE)
            self.nodes[i] = tok
            nodes_group.add(tok)

        self.edges_group = edges_group
        self.nodes_group = nodes_group
        self.add(edges_group, nodes_group)

    def create_size_badge(
        self, u: int, size_val: int, direction: np.ndarray = UP + RIGHT
    ) -> VGroup:
        badge_bg = RoundedRectangle(
            width=0.52,
            height=0.34,
            corner_radius=0.08,
            fill_color=CARD_BG,
            fill_opacity=0.95,
            stroke_color=CARD_BORDER,
            stroke_width=1.5,
        )
        badge_txt = MathTex(str(size_val), color=INK_DARK, font_size=22)
        badge_txt.move_to(badge_bg.get_center())
        badge = VGroup(badge_bg, badge_txt)
        badge.next_to(self.nodes[u], direction, buff=0.06)
        badge.set_z_index(8)
        self.size_badges[u] = badge
        return badge

    def create_component_region(
        self,
        comp_nodes: List[int],
        color: str,
        pad: float = 0.46,
        fill_opacity: float = 0.16,
    ) -> VMobject:
        sample_angles = np.linspace(0, 2 * np.pi, 28, endpoint=False)
        pts_2d: List[Tuple[float, float]] = []
        for u in comp_nodes:
            center = self.positions[u]
            for ang in sample_angles:
                pts_2d.append(
                    (
                        float(center[0] + pad * np.cos(ang)),
                        float(center[1] + pad * np.sin(ang)),
                    )
                )

        pts_sorted = sorted(set(pts_2d))

        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        lower = []
        for p in pts_sorted:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)
        upper = []
        for p in reversed(pts_sorted):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)

        hull_2d = lower[:-1] + upper[:-1]
        hull_3d = [np.array([x, y, 0.0]) for x, y in hull_2d]

        region = Polygon(
            *hull_3d,
            fill_color=color,
            fill_opacity=fill_opacity,
            stroke_color=color,
            stroke_width=2.6,
        )
        region.set_z_index(0)
        return region


# Coordenadas del árbol principal de 9 nodos
def get_demo_tree_positions(
    offset: np.ndarray = np.array([-2.2, -0.15, 0.0]),
) -> Dict[int, np.ndarray]:
    raw = {
        1: np.array([-3.8, 1.75, 0.0]),
        2: np.array([-2.1, 1.15, 0.0]),
        3: np.array([-2.5, -0.55, 0.0]),
        4: np.array([-0.3, 0.45, 0.0]),
        5: np.array([1.45, 1.35, 0.0]),
        8: np.array([2.95, 1.95, 0.0]),
        9: np.array([2.95, 0.65, 0.0]),
        6: np.array([1.25, -0.85, 0.0]),
        7: np.array([2.85, -1.35, 0.0]),
    }
    return {k: v + offset for k, v in raw.items()}


# Coordenadas radiales del árbol estrella de 7 nodos
def get_star_tree_positions(
    center: np.ndarray = np.array([-2.1, -0.25, 0.0]), radius: float = 2.05
) -> Dict[int, np.ndarray]:
    pos: Dict[int, np.ndarray] = {2: center}
    leaves = [1, 3, 4, 5, 6, 7]
    for idx, leaf in enumerate(leaves):
        angle = np.pi / 2 + idx * (2 * np.pi / len(leaves))
        pos[leaf] = center + radius * \
            np.array([np.cos(angle), np.sin(angle), 0.0])
    return pos


# Parte 1: Portada e introducción conceptual
def play_scene_1_intro(scene: Scene):
    title = Tex(r"\textbf{Centroide de un Árbol}",
                color=INK_DARK, font_size=56)
    subtitle = Tex(
        r"División equilibrada de árboles en tiempo lineal $O(n)$",
        color=INK_MUTED,
        font_size=30,
    ).next_to(title, DOWN, buff=0.3)

    authors_preview = Tex(
        r"M. Lupus Collazos $\cdot$ R. Cuba Zari $\cdot$ J. Villalobos Jiménez",
        color=INK_MUTED,
        font_size=23,
    ).next_to(subtitle, DOWN, buff=0.55)

    cover_group = VGroup(title, subtitle, authors_preview).move_to(ORIGIN)

    scene.play(FadeIn(title, shift=0.15 * UP), run_time=1.1)
    scene.play(FadeIn(subtitle), FadeIn(authors_preview), run_time=1.0)
    scene.wait(1.8)
    scene.play(FadeOut(cover_group, shift=0.2 * UP), run_time=0.9)

    sec_title = Tex(
        r"\textbf{¿Qué es el Centroide de un Árbol?}", color=INK_DARK, font_size=36
    ).to_edge(UP, buff=0.92)

    positions = get_demo_tree_positions(offset=np.array([-1.95, -0.45, 0.0]))
    tree = TreeVisual(DEMO_TREE_N, DEMO_TREE_EDGES,
                      positions, node_radius=0.28)

    rule_card = RoundedRectangle(
        width=4.5,
        height=3.9,
        corner_radius=0.12,
        fill_color=CARD_BG,
        fill_opacity=1.0,
        stroke_color=CARD_BORDER,
        stroke_width=2.0,
    ).move_to(np.array([4.15, -0.35, 0.0]))

    n_formula = MathTex(
        r"n = 9 \quad\Rightarrow\quad \left\lfloor \frac{n}{2} \right\rfloor = 4",
        color=INK_DARK,
        font_size=32,
    ).move_to(rule_card.get_top() + 0.65 * DOWN)

    def_text = Tex(
        r"Al eliminar el \textbf{centroide},\\"
        r"toda componente conexa tiene\\"
        r"tamaño a lo más $\lfloor n/2 \rfloor$:",
        color=INK_DARK,
        font_size=25,
    ).next_to(n_formula, DOWN, buff=0.35)

    ineq_formula = MathTex(
        r"\max(\text{componente}) \le 4",
        color=TOKEN_GREEN[0],
        font_size=34,
    ).next_to(def_text, DOWN, buff=0.35)

    scene.play(
        FadeIn(sec_title),
        Create(tree.edges_group),
        LaggedStart(
            *[FadeIn(tree.nodes[i], scale=0.85)
              for i in range(1, DEMO_TREE_N + 1)],
            lag_ratio=0.06,
        ),
        FadeIn(rule_card),
        Write(n_formula),
        run_time=1.8,
    )
    scene.play(FadeIn(def_text), Write(ineq_formula), run_time=1.4)
    scene.wait(1.2)

    bad_banner = Tex(
        r"Si quitamos el nodo $1$: queda un bloque de $8 > 4$ (desbalanceado)",
        color=TOKEN_RED[0],
        font_size=26,
    ).to_edge(DOWN, buff=0.55)

    bad_comp_region = tree.create_component_region(
        list(range(2, 10)), color=TOKEN_RED[0], pad=0.45, fill_opacity=0.14
    )

    scene.play(
        tree.nodes[1].recolor_anim(TOKEN_FADED, label_color=INK_MUTED),
        tree.edges[(1, 2)].animate.set_stroke(opacity=0.2),
        FadeIn(bad_comp_region),
        *[tree.nodes[i].recolor_anim(TOKEN_RED) for i in range(2, 10)],
        FadeIn(bad_banner, shift=0.1 * UP),
        run_time=1.4,
    )
    scene.wait(1.8)

    good_banner = Tex(
        r"Si quitamos el nodo $4$: componentes de tamaños $3, 3, 2 \le 4$ (\textbf{Centroide})",
        color=TOKEN_GREEN[0],
        font_size=26,
    ).to_edge(DOWN, buff=0.55)

    intro_trace = find_centroid_with_trace(
        DEMO_TREE_N, DEMO_TREE_EDGES, root=1)
    good_comp_regions = VGroup(
        *[
            tree.create_component_region(
                comp, color=TOKEN_GREEN[0], pad=0.45, fill_opacity=0.16
            )
            for comp in intro_trace.components_after_removal
        ]
    )

    scene.play(
        FadeOut(bad_banner),
        FadeOut(bad_comp_region),
        tree.nodes[1].recolor_anim(TOKEN_BLUE),
        tree.edges[(1, 2)].animate.set_stroke(opacity=1.0),
        *[tree.nodes[i].recolor_anim(TOKEN_BLUE) for i in range(2, 10)],
        run_time=0.9,
    )

    scene.play(
        tree.nodes[4].recolor_anim(TOKEN_GREEN),
        tree.edges[(2, 4)].animate.set_stroke(opacity=0.2),
        tree.edges[(4, 5)].animate.set_stroke(opacity=0.2),
        tree.edges[(4, 6)].animate.set_stroke(opacity=0.2),
        LaggedStart(
            *[FadeIn(reg, scale=0.96) for reg in good_comp_regions], lag_ratio=0.12
        ),
        FadeIn(good_banner, shift=0.1 * UP),
        run_time=1.4,
    )
    scene.wait(2.2)

    scene.play(
        FadeOut(sec_title),
        FadeOut(good_comp_regions),
        FadeOut(tree),
        FadeOut(rule_card),
        FadeOut(n_formula),
        FadeOut(def_text),
        FadeOut(ineq_formula),
        FadeOut(good_banner),
        run_time=0.9,
    )


# Parte 2: Ejecución del algoritmo en dos fases
def play_scene_2_execution(scene: Scene):
    trace: CentroidTrace = find_centroid_with_trace(
        DEMO_TREE_N, DEMO_TREE_EDGES, root=1
    )
    half_n = trace.n // 2

    sec_title = Tex(
        r"\textbf{Algoritmo en Dos Fases} ($n = 9,\; \lfloor n/2 \rfloor = 4$)",
        color=INK_DARK,
        font_size=35,
    ).to_edge(UP, buff=0.92)

    positions = get_demo_tree_positions(offset=np.array([-2.05, -0.45, 0.0]))
    tree = TreeVisual(trace.n, trace.edges, positions, node_radius=0.28)

    status_card = RoundedRectangle(
        width=4.85,
        height=4.85,
        corner_radius=0.12,
        fill_color=CARD_BG,
        fill_opacity=1.0,
        stroke_color=CARD_BORDER,
        stroke_width=2.0,
    ).move_to(np.array([4.05, -0.45, 0.0]))

    phase_title = Tex(
        r"\textbf{Fase 1: DFS de tamaños}", color=INK_DARK, font_size=26
    ).move_to(status_card.get_top() + 0.45 * DOWN)

    dfs_pseudo_lines = [
        r"\texttt{dfs(u):}",
        r"\texttt{\ \ sizes[u] = 1}",
        r"\texttt{\ \ for v in G[u]:}",
        r"\texttt{\ \ \ \ if sizes[v] == -1:}",
        r"\texttt{\ \ \ \ \ \ sizes[u] += dfs(v)}",
        r"\texttt{\ \ return sizes[u]}",
    ]
    code_formula = VGroup(
        *[Tex(line, color=INK_DARK, font_size=20) for line in dfs_pseudo_lines]
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.07)
    code_formula.next_to(phase_title, DOWN, buff=0.25)

    step_status = Tex(
        r"Enraizando en $u = 1$...", color=INK_MUTED, font_size=22
    ).move_to(status_card.get_bottom() + 0.95 * UP)

    scene.play(
        FadeIn(sec_title),
        Create(tree.edges_group),
        FadeIn(tree.nodes_group),
        FadeIn(status_card),
        FadeIn(phase_title),
        Write(code_formula),
        FadeIn(step_status),
        run_time=1.8,
    )
    scene.wait(2.6)

    badge_dirs = {
        1: DOWN + LEFT,
        2: DOWN + RIGHT,
        3: DOWN + LEFT,
        4: DOWN,
        5: UP + LEFT,
        8: UP,
        9: DOWN,
        6: DOWN + LEFT,
        7: DOWN,
    }

    badges_group = VGroup()
    for ev in trace.dfs_events:
        if ev.kind == "enter":
            scene.play(
                tree.nodes[ev.u].recolor_anim(TOKEN_AMBER),
                run_time=0.22,
            )
        elif ev.kind == "edge" and ev.v is not None:
            edge_mob = tree.edges[(ev.u, ev.v)]
            scene.play(
                edge_mob.animate.set_stroke(color=TOKEN_AMBER[0], width=5.5),
                run_time=0.16,
            )
        elif ev.kind == "size" and ev.size_u is not None:
            badge = tree.create_size_badge(
                ev.u, ev.size_u, direction=badge_dirs.get(ev.u, UP + RIGHT)
            )
            badges_group.add(badge)
            scene.play(
                FadeIn(badge, scale=0.8),
                tree.nodes[ev.u].recolor_anim(TOKEN_BLUE),
                run_time=0.26,
            )

    scene.play(
        *[
            line.animate.set_stroke(color=EDGE_COLOR, width=4.0)
            for line in tree.edges_group
        ],
        run_time=0.6,
    )
    scene.wait(3.0)

    new_phase_title = Tex(
        r"\textbf{Fase 2: Búsqueda del Centroide}", color=INK_DARK, font_size=25
    ).move_to(phase_title.get_center())

    search_pseudo_lines = [
        r"\texttt{u = 1, p = -1}",
        r"\texttt{while True:}",
        r"\texttt{\ \ next = -1}",
        r"\texttt{\ \ for v in G[u]:}",
        r"\texttt{\ \ \ \ if v != p and sizes[v] > n/2:}",
        r"\texttt{\ \ \ \ \ \ next = v; break}",
        r"\texttt{\ \ if next == -1: return u}",
        r"\texttt{\ \ p = u; u = next}",
    ]
    new_code_formula = VGroup(
        *[Tex(line, color=INK_DARK, font_size=18) for line in search_pseudo_lines]
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
    new_code_formula.next_to(new_phase_title, DOWN, buff=0.22)

    pointer = Triangle(
        fill_color=TOKEN_AMBER[0],
        fill_opacity=1.0,
        stroke_color=TOKEN_AMBER[1],
        stroke_width=2,
    )
    pointer.scale(0.18).rotate(PI)
    pointer.next_to(tree.nodes[trace.root], UP, buff=0.14)
    pointer.set_z_index(10)

    scene.play(
        ReplacementTransform(phase_title, new_phase_title),
        ReplacementTransform(code_formula, new_code_formula),
        FadeIn(pointer, shift=0.15 * DOWN),
        run_time=1.2,
    )
    scene.wait(1.8)

    final_comp_regions = VGroup()
    for step in trace.greedy_steps:
        u = step.u
        scene.play(
            pointer.animate.next_to(tree.nodes[u], UP, buff=0.14),
            tree.nodes[u].recolor_anim(TOKEN_AMBER),
            run_time=0.65,
        )
        scene.wait(0.6)

        for v, sz_v, is_heavy in step.checked_children:
            cmp_symbol = ">" if is_heavy else r"\le"
            cmp_color = TOKEN_RED[0] if is_heavy else TOKEN_GREEN[0]
            msg = MathTex(
                rf"\text{{Hijo }} {v}:\; \text{{sizes}}[{v}] = {
                    sz_v} {cmp_symbol} {half_n}",
                color=cmp_color,
                font_size=27,
            ).move_to(step_status.get_center())

            if is_heavy:
                heavy_nodes = get_subtree_nodes(trace, v)
                heavy_region = tree.create_component_region(
                    heavy_nodes, color=TOKEN_RED[0], pad=0.44, fill_opacity=0.13
                )
                scene.play(
                    ReplacementTransform(step_status, msg),
                    FadeIn(heavy_region),
                    *[tree.nodes[x].recolor_anim(TOKEN_RED)
                      for x in heavy_nodes],
                    run_time=1.0,
                )
                step_status = msg
                scene.wait(1.8)
                scene.play(
                    FadeOut(heavy_region),
                    *[
                        tree.nodes[x].recolor_anim(TOKEN_BLUE)
                        for x in heavy_nodes
                        if x != v
                    ],
                    tree.nodes[u].recolor_anim(TOKEN_BLUE),
                    tree.edges[(u, v)].animate.set_stroke(
                        color=TOKEN_AMBER[0], width=6.0
                    ),
                    run_time=0.75,
                )
            else:
                scene.play(
                    ReplacementTransform(step_status, msg),
                    Indicate(
                        tree.size_badges[v], color=TOKEN_GREEN[0], scale_factor=1.2
                    ),
                    run_time=0.75,
                )
                step_status = msg
                scene.wait(0.8)

        if step.next_node == -1:
            found_msg = Tex(
                rf"Ningún vecino supera $4$.\\"
                rf"\textbf{{¡Centroide encontrado: nodo {u}!}}",
                color=TOKEN_GREEN[0],
                font_size=25,
            ).move_to(step_status.get_center())

            comp_sizes = [len(c) for c in trace.components_after_removal]
            comp_formula = MathTex(
                rf"\text{{Componentes: }} {', '.join(map(str, comp_sizes))} \le {
                    half_n}",
                color=TOKEN_GREEN[0],
                font_size=26,
            ).next_to(found_msg, DOWN, buff=0.22)

            scene.play(
                ReplacementTransform(step_status, found_msg),
                FadeIn(comp_formula, shift=0.1 * UP),
                tree.nodes[u].recolor_anim(TOKEN_GREEN),
                Flash(tree.nodes[u], color=TOKEN_GREEN[0], line_length=0.25),
                run_time=1.2,
            )
            step_status = VGroup(found_msg, comp_formula)

            incident_edges = [tree.edges[(u, nb)] for nb in trace.adj[u]]
            final_comp_regions = VGroup(
                *[
                    tree.create_component_region(
                        comp, color=TOKEN_GREEN[0], pad=0.45, fill_opacity=0.16
                    )
                    for comp in trace.components_after_removal
                ]
            )
            scene.play(
                *[e.animate.set_stroke(opacity=0.22) for e in incident_edges],
                LaggedStart(
                    *[FadeIn(reg, scale=0.96) for reg in final_comp_regions],
                    lag_ratio=0.12,
                ),
                run_time=1.2,
            )
            scene.wait(4.2)

    scene.play(
        FadeOut(sec_title),
        FadeOut(final_comp_regions),
        FadeOut(tree),
        FadeOut(badges_group),
        FadeOut(status_card),
        FadeOut(new_phase_title),
        FadeOut(new_code_formula),
        FadeOut(step_status),
        FadeOut(pointer),
        run_time=1.0,
    )
    scene.wait(0.6)


# Caso borde: árbol estrella
def play_scene_3_star_edge_case(scene: Scene):
    trace: CentroidTrace = find_centroid_with_trace(
        STAR_TREE_N, STAR_TREE_EDGES, root=1
    )

    sec_title = Tex(
        r"\textbf{Caso Borde: Árbol Estrella} ($n = 7,\; \lfloor n/2 \rfloor = 3$)",
        color=INK_DARK,
        font_size=35,
    ).to_edge(UP, buff=0.92)

    positions = get_star_tree_positions(
        center=np.array([-2.15, -0.5, 0.0]), radius=1.85
    )
    tree = TreeVisual(trace.n, trace.edges, positions, node_radius=0.28)

    info_card = RoundedRectangle(
        width=4.7,
        height=4.3,
        corner_radius=0.12,
        fill_color=CARD_BG,
        fill_opacity=1.0,
        stroke_color=CARD_BORDER,
        stroke_width=2.0,
    ).move_to(np.array([3.95, -0.4, 0.0]))

    card_heading = Tex(
        r"\textbf{Inicio desde una hoja ($u = 1$)}", color=INK_DARK, font_size=26
    ).move_to(info_card.get_top() + 0.55 * DOWN)

    card_body = Tex(
        r"1. El DFS asigna $\text{sizes}[2] = 6$\\y $\text{sizes}[\text{hoja}] = 1$.",
        color=INK_DARK,
        font_size=24,
    ).next_to(card_heading, DOWN, buff=0.35)

    scene.play(
        FadeIn(sec_title),
        Create(tree.edges_group),
        FadeIn(tree.nodes_group),
        FadeIn(info_card),
        FadeIn(card_heading),
        FadeIn(card_body),
        run_time=1.8,
    )
    scene.wait(3.8)

    badges = VGroup()
    for node_id, sz in trace.sizes.items():
        if node_id == 2:
            direction = UP + RIGHT
        elif node_id == 1:
            direction = LEFT
        else:
            direction = positions[node_id] - positions[2]
            norm = np.linalg.norm(direction)
            if norm > 0:
                direction = direction / norm
        badge = tree.create_size_badge(node_id, sz, direction=direction)
        badges.add(badge)

    scene.play(
        LaggedStart(*[FadeIn(b, scale=0.85) for b in badges], lag_ratio=0.08),
        run_time=1.4,
    )
    scene.wait(3.2)

    step1_txt = MathTex(
        r"\text{Desde } 1:\; \text{sizes}[2] = 6 > 3 \;\Rightarrow\; \text{salta a } 2",
        color=TOKEN_RED[0],
        font_size=24,
    ).next_to(card_body, DOWN, buff=0.38)

    scene.play(
        tree.nodes[1].recolor_anim(TOKEN_AMBER),
        Write(step1_txt),
        tree.nodes[2].recolor_anim(TOKEN_RED),
        run_time=1.3,
    )
    scene.wait(2.5)

    step2_txt = Tex(
        r"En $u = 2$: las $6$ hojas quedan con\\"
        r"tamaño $1 \le 3$ $\Rightarrow$ \textbf{Centroide = 2}",
        color=TOKEN_GREEN[0],
        font_size=24,
    ).next_to(step1_txt, DOWN, buff=0.35)

    star_comp_regions = VGroup(
        *[
            tree.create_component_region(
                comp, color=TOKEN_GREEN[0], pad=0.44, fill_opacity=0.16
            )
            for comp in trace.components_after_removal
        ]
    )

    scene.play(
        tree.nodes[1].recolor_anim(TOKEN_BLUE),
        tree.nodes[2].recolor_anim(TOKEN_GREEN),
        Flash(tree.nodes[2], color=TOKEN_GREEN[0], line_length=0.25),
        FadeIn(step2_txt, shift=0.1 * UP),
        *[e.animate.set_stroke(opacity=0.22) for e in tree.edges_group],
        LaggedStart(
            *[FadeIn(reg, scale=0.92) for reg in star_comp_regions], lag_ratio=0.08
        ),
        run_time=1.5,
    )
    scene.wait(4.0)

    scene.play(
        FadeOut(sec_title),
        FadeOut(star_comp_regions),
        FadeOut(tree),
        FadeOut(badges),
        FadeOut(info_card),
        FadeOut(card_heading),
        FadeOut(card_body),
        FadeOut(step1_txt),
        FadeOut(step2_txt),
        run_time=1.0,
    )
    scene.wait(0.5)


# Caso borde mínimo: árbol de un solo nodo (n = 1)
def play_scene_3b_single_node_edge_case(scene: Scene):
    trace: CentroidTrace = find_centroid_with_trace(1, [], root=1)

    sec_title = Tex(
        r"\textbf{Caso Borde Mínimo: Un Solo Nodo} ($n = 1,\; \lfloor n/2 \rfloor = 0$)",
        color=INK_DARK,
        font_size=34,
    ).to_edge(UP, buff=0.92)

    positions = {1: np.array([-2.15, -0.45, 0.0])}
    tree = TreeVisual(trace.n, trace.edges, positions, node_radius=0.38)

    info_card = RoundedRectangle(
        width=5.1,
        height=4.1,
        corner_radius=0.12,
        fill_color=CARD_BG,
        fill_opacity=1.0,
        stroke_color=CARD_BORDER,
        stroke_width=2.0,
    ).move_to(np.array([3.85, -0.4, 0.0]))

    card_heading = Tex(
        r"\textbf{Árbol trivial ($n = 1$)}", color=INK_DARK, font_size=26
    ).move_to(info_card.get_top() + 0.55 * DOWN)

    step1_txt = Tex(
        r"1. $\text{sizes}[1] = 1$, y no existen\\"
        r"vecinos por visitar.",
        color=INK_DARK,
        font_size=24,
    ).next_to(card_heading, DOWN, buff=0.38)

    step2_txt = Tex(
        r"2. Al quitar el nodo $1$, no quedan\\"
        r"componentes conexas ($\emptyset$).",
        color=INK_DARK,
        font_size=24,
    ).next_to(step1_txt, DOWN, buff=0.32)

    vacuity_txt = Tex(
        r"Por \textbf{vacuidad}, toda componente\\"
        r"tiene tamaño $\le 0$ $\Rightarrow$ \textbf{Centroide = 1}",
        color=TOKEN_GREEN[0],
        font_size=24,
    ).next_to(step2_txt, DOWN, buff=0.35)

    badge = tree.create_size_badge(1, trace.sizes[1], direction=UP + RIGHT)

    scene.play(
        FadeIn(sec_title),
        FadeIn(tree.nodes_group, scale=0.85),
        FadeIn(badge, scale=0.85),
        FadeIn(info_card),
        FadeIn(card_heading),
        FadeIn(step1_txt),
        run_time=1.4,
    )
    scene.wait(2.2)

    scene.play(FadeIn(step2_txt), run_time=1.0)
    scene.wait(1.6)

    halo = Circle(
        radius=0.62,
        color=TOKEN_GREEN[0],
        stroke_width=2.6,
        fill_color=TOKEN_GREEN[0],
        fill_opacity=0.14,
    ).move_to(positions[1]).set_z_index(0)

    scene.play(
        tree.nodes[1].recolor_anim(TOKEN_GREEN),
        FadeIn(halo, scale=0.9),
        Flash(tree.nodes[1], color=TOKEN_GREEN[0], line_length=0.25),
        FadeIn(vacuity_txt, shift=0.1 * UP),
        run_time=1.3,
    )
    scene.wait(3.2)

    scene.play(
        FadeOut(sec_title),
        FadeOut(halo),
        FadeOut(tree),
        FadeOut(badge),
        FadeOut(info_card),
        FadeOut(card_heading),
        FadeOut(step1_txt),
        FadeOut(step2_txt),
        FadeOut(vacuity_txt),
        run_time=0.9,
    )
    scene.wait(0.5)


# Complejidad temporal y créditos finales
def play_scene_4_complexity_and_credits(scene: Scene):
    sec_title = Tex(
        r"\textbf{Análisis de Complejidad Temporal}", color=INK_DARK, font_size=36
    ).to_edge(UP, buff=0.92)

    eq_complexity = MathTex(
        r"\underbrace{\mathcal{O}(n)}_{\text{Fase 1: DFS}}",
        r"\;+\;",
        r"\underbrace{\mathcal{O}(n)}_{\text{Fase 2: Búsqueda}}",
        r"\;=\;",
        r"\mathcal{O}(n)",
        font_size=46,
        color=INK_DARK,
    ).move_to(np.array([0.0, 1.15, 0.0]))
    eq_complexity[0].set_color(TOKEN_BLUE[0])
    eq_complexity[2].set_color(TOKEN_RED[0])
    eq_complexity[4].set_color(TOKEN_GREEN[0])

    card_left = RoundedRectangle(
        width=5.4,
        height=2.3,
        corner_radius=0.12,
        fill_color=CARD_BG,
        fill_opacity=1.0,
        stroke_color=CARD_BORDER,
        stroke_width=2.0,
    ).move_to(np.array([-3.0, -0.95, 0.0]))

    txt_left = Tex(
        r"\textbf{1. Recorrido DFS:}\\"
        r"Visita cada uno de los $n$ nodos y\\"
        r"$n-1$ aristas exactamente una vez.",
        color=INK_DARK,
        font_size=24,
    ).move_to(card_left.get_center())

    card_right = RoundedRectangle(
        width=5.4,
        height=2.3,
        corner_radius=0.12,
        fill_color=CARD_BG,
        fill_opacity=1.0,
        stroke_color=CARD_BORDER,
        stroke_width=2.0,
    ).move_to(np.array([3.0, -0.95, 0.0]))

    txt_right = Tex(
        r"\textbf{2. Búsqueda del Centroide:}\\"
        r"Solo existe a lo más un hijo $> \lfloor n/2 \rfloor$;\\"
        r"avanza sin retroceder jamás ($\le n$ pasos).",
        color=INK_DARK,
        font_size=24,
    ).move_to(card_right.get_center())

    space_note = Tex(
        r"Complejidad Espacial: $\mathcal{O}(n)$ para almacenar el árbol y el arreglo \texttt{sizes}.",
        color=INK_MUTED,
        font_size=24,
    ).to_edge(DOWN, buff=0.65)

    scene.play(FadeIn(sec_title), Write(eq_complexity), run_time=1.8)
    scene.wait(2.2)
    scene.play(
        FadeIn(card_left, shift=0.1 * UP),
        FadeIn(txt_left),
        FadeIn(card_right, shift=0.1 * UP),
        FadeIn(txt_right),
        FadeIn(space_note),
        run_time=1.6,
    )
    scene.wait(11.2)

    scene.play(
        FadeOut(sec_title),
        FadeOut(eq_complexity),
        FadeOut(card_left),
        FadeOut(txt_left),
        FadeOut(card_right),
        FadeOut(txt_right),
        FadeOut(space_note),
        run_time=1.0,
    )
    scene.wait(0.6)

    credits_title = Tex(
        r"\textbf{Centroide de un Árbol}", color=INK_DARK, font_size=44
    ).move_to(np.array([0.0, 2.0, 0.0]))

    course_lbl = Tex(
        r"CS2023 — Algoritmos y Estructuras de Datos (UTEC)",
        color=INK_MUTED,
        font_size=26,
    ).next_to(credits_title, DOWN, buff=0.22)

    members_card = RoundedRectangle(
        width=8.6,
        height=2.55,
        corner_radius=0.12,
        fill_color=CARD_BG,
        fill_opacity=1.0,
        stroke_color=CARD_BORDER,
        stroke_width=2.0,
    ).move_to(np.array([0.0, -0.15, 0.0]))

    members_txt = Tex(
        r"\textbf{Integrantes:}\\[6pt]"
        r"Maxwell Gregorio Lupus Collazos Solis\\[3pt]"
        r"Renzo Vladimir Cuba Zari\\[3pt]"
        r"José Luis Villalobos Jiménez",
        color=INK_DARK,
        font_size=26,
    ).move_to(members_card.get_center())

    ref_txt = Tex(
        r"\textbf{Referencia:} \texttt{https://www.geeksforgeeks.org/dsa/centroid-decomposition-of-tree/}",
        color=INK_MUTED,
        font_size=20,
    ).to_edge(DOWN, buff=0.65)

    scene.play(
        FadeIn(credits_title, shift=0.1 * UP),
        FadeIn(course_lbl),
        FadeIn(members_card),
        FadeIn(members_txt),
        FadeIn(ref_txt),
        run_time=1.4,
    )
    scene.wait(3.6)


# Parte 1 : Portada e introducción conceptual
class Parte1(Scene):
    def construct(self):
        create_paper_stage(self)
        play_scene_1_intro(self)


# Parte 2 : Ejecución del algoritmo en dos fases
class Parte2(Scene):
    def construct(self):
        create_paper_stage(self)
        play_scene_2_execution(self)


# Parte 3 : Casos borde, complejidad y créditos
class Parte3(Scene):
    def construct(self):
        create_paper_stage(self)
        play_scene_3_star_edge_case(self)
        play_scene_3b_single_node_edge_case(self)
        play_scene_4_complexity_and_credits(self)


# Video completo uniendo las 3 partes
class CentroidFullVideo(Scene):
    def construct(self):
        create_paper_stage(self)
        play_scene_1_intro(self)
        play_scene_2_execution(self)
        play_scene_3_star_edge_case(self)
        play_scene_3b_single_node_edge_case(self)
        play_scene_4_complexity_and_credits(self)
