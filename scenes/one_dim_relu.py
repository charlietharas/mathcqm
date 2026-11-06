from types import SimpleNamespace

from functools import partial

import numpy as np
from manim import (
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    MathTex,
    Transform,
    ValueTracker,
    VGroup,
    VMobject,
)
from _helpers import AFFINE, NEURON, OUTPUT, equation, prose, slide_header, plot_axes, vertical_grid
from scenes.functions import target
from scenes._settings import Slide

# Same grid as the interpolation proof
GRID = np.linspace(0, 1, 9)
VALUES = np.array([target(float(t)) for t in GRID])
SLOPES = np.diff(VALUES) / np.diff(GRID)


construction_text = partial(prose, y=2.05, font_size=30)
construction_equation = partial(equation, y=1.1, font_size=39, width=12)


class OneDimReLUSlide(Slide):
    def construct(self):
        # ReLU hinge
        hinge = self.relu_hinge()
        self.gate()

        # Shifted hinge
        self.shift_hinge(hinge)
        self.gate()

        # Initial slope
        view = self.initial_slope()
        self.gate()

        # First two slope corrections
        for knot in (1, 2):
            self.correct_slope(view, knot)
            self.gate()

        # Remaining knots
        self.remaining_slopes(view)
        self.gate()

        # Network formula and error bound
        self.network_formula()
        self.gate()

    def relu_hinge(self):
        self.title = slide_header("Shifted ReLU")
        note = construction_text(
            r"\textit{Construction.} We construct a neural network equivalent to $p$."
        )
        formula = construction_equation(r"\sigma(x)=\operatorname{ReLU}(x)=\max\{0,x\}")
        axes = plot_axes(
            x_range=[-0.2, 1.2, 0.2],
            y_range=[0, 1.3, 0.5],
            x_length=8,
            y_length=3,
            center=[0, -1, 0],
        )
        curve = VMobject(color=NEURON, stroke_width=4).set_points_as_corners(
            [axes.c2p(-0.2, 0), axes.c2p(0, 0), axes.c2p(1.2, 1.2)]
        )
        zero = MathTex("0", font_size=24).move_to(axes.c2p(0, 0) + [0, -0.25, 0])
        self.add(self.title, note, formula, axes, zero)
        self.play(Create(curve), run_time=1.5)

        return SimpleNamespace(axes=axes, formula=formula, curve=curve)

    def shift_hinge(self, view):
        axes = view.axes
        formula = view.formula
        curve = view.curve
        shifted = construction_equation(r"\sigma(x-t)=\begin{cases}0&x\leq t,\\x-t&x>t.\end{cases}")
        t = 0.4
        new_curve = VMobject(color=NEURON, stroke_width=4).set_points_as_corners(
            [axes.c2p(-0.2, 0), axes.c2p(t, 0), axes.c2p(1.2, 1.2 - t)]
        )
        tick = Line(axes.c2p(t, 0) + [0, -0.08, 0], axes.c2p(t, 0) + [0, 0.08, 0], color=NEURON)
        label = MathTex("t", font_size=27, color=NEURON).move_to(axes.c2p(t, 0) + [0, -0.28, 0])
        self.remove(formula)
        self.add(shifted)
        self.play(Transform(curve, new_curve), FadeIn(tick), FadeIn(label), run_time=1.1)

    def initial_slope(self):
        self.clear()
        self.title = slide_header("Correcting the slope")
        note = construction_text(
            r"Begin at height $f(0)$ and follow slope $m_0$. " r"On $[0,1]$, $\sigma(x)=x$."
        )
        formula = construction_equation(r"f(0)+m_0\sigma(x)")
        axes = plot_axes(
            x_range=[0, 1, 0.125], y_range=[0, 1.5, 0.5], x_length=10, y_length=3, center=[0, -1, 0]
        )
        p = VMobject(color=OUTPUT, stroke_width=3, stroke_opacity=0.65).set_points_as_corners(
            [axes.c2p(t, y) for t, y in zip(GRID, VALUES)]
        )
        knots = VGroup(
            *(Dot(axes.c2p(t, y), radius=0.035, color=OUTPUT) for t, y in zip(GRID, VALUES))
        )
        guides = vertical_grid(axes, GRID, 1.4, stroke_opacity=0.25)
        labels = VGroup(
            MathTex("0", font_size=23).move_to(axes.c2p(0, 0) + [0, -0.23, 0]),
            MathTex("1", font_size=23).move_to(axes.c2p(1, 0) + [0, -0.23, 0]),
            MathTex("p", font_size=28, color=OUTPUT).move_to(
                axes.c2p(1, VALUES[-1]) + [0.25, 0, 0]
            ),
        )

        progress = ValueTracker(0)
        network = visible_network(axes, 0)
        self.add(self.title, note, formula, axes, guides, p, knots, labels)
        self.play(Create(network), run_time=1.6)
        network.add_updater(lambda mob: mob.become(visible_network(axes, progress.get_value())))

        return SimpleNamespace(
            axes=axes, note=note, formula=formula, progress=progress, network=network
        )

    def correct_slope(self, view, k):
        axes = view.axes
        note = view.note
        formula = view.formula
        progress = view.progress
        self.remove(note, formula)
        if k == 1:
            note = construction_text(r"At $t_1$, the slope must change by $m_1-m_0$.")
            formula = construction_equation(r"f(0)+m_0\sigma(x)+(m_1-m_0)\sigma(x-t_1)")
        else:
            note = construction_text(r"At $t_2$, the slope must change by $m_2-m_1$.")
            formula = construction_equation(
                r"f(0)+m_0\sigma(x)+(m_1-m_0)\sigma(x-t_1)" r"+(m_2-m_1)\sigma(x-t_2)", font_size=34
            )
        self.add(note, formula)
        mark = MathTex(rf"t_{k}", font_size=24, color=AFFINE).move_to(
            axes.c2p(GRID[k], 0) + [0, -0.25, 0]
        )
        self.add(mark)
        self.play(progress.animate.set_value(k), run_time=1.6)

        view.note = note
        view.formula = formula

    def remaining_slopes(self, view):
        axes = view.axes
        note = view.note
        formula = view.formula
        progress = view.progress
        network = view.network
        self.remove(note, formula)
        note = construction_text(
            r"Repeat s.t. each neuron switches on at its grid point and corrects the slope."
        )
        formula = construction_equation(
            r"N_\theta(x)=f(0)+m_0\sigma(x)+" r"\sum_{i=1}^{n-1}(m_i-m_{i-1})\sigma(x-t_i)",
            font_size=36,
        )
        continuation = MathTex(r"\ldots", font_size=24, color=AFFINE).move_to(
            axes.c2p(GRID[3], 0) + [0, -0.25, 0]
        )
        self.add(note, formula, continuation)
        for k in range(3, 8):
            self.play(progress.animate.set_value(k), run_time=0.45)
        network.clear_updaters()
        self.network_equation = formula

    def network_formula(self):
        # Reuse the live equation in the recap
        formula = self.network_equation
        outgoing = [mob for mob in self.mobjects if mob is not formula and mob is not self.title]
        self.play(*(FadeOut(mob) for mob in outgoing), run_time=0.35)
        destination = formula.copy().scale(38 / 36).move_to([0, 1.1, 0])
        self.play(
            Transform(self.title, slide_header("ReLU approximation")),
            Transform(formula, destination),
            run_time=0.7,
        )
        self.add(
            construction_text("Our final network is thus described by"),
            construction_text(
                "The network starts at $f(0)$, is continuous, and has the same slope as $p$ on every interval.",
                y=-0.1,
            ),
            construction_equation(
                r"N_\theta=p\implies\|f-N_\theta\|_\infty=\|f-p\|_\infty<\varepsilon.\quad\square",
                y=-1.35,
                font_size=38,
            ),
        )


def network_value(x, corrections=7):
    value = VALUES[0] + SLOPES[0] * max(0, x)
    for i in range(1, corrections + 1):
        value += (SLOPES[i] - SLOPES[i - 1]) * max(0, x - GRID[i])
    return value


def visible_network(axes, progress):
    k = min(int(progress), 7)
    weight = progress - k if k < 7 else 0
    ys = [
        network_value(float(x), k)
        + (weight * (SLOPES[k + 1] - SLOPES[k]) * max(0, x - GRID[k + 1]) if k < 7 else 0)
        for x in GRID
    ]
    graph = VMobject(color=AFFINE, stroke_width=5)
    bottom, top = axes.y_range[:2]
    for x0, x1, y0, y1 in zip(GRID[:-1], GRID[1:], ys[:-1], ys[1:]):
        lo, hi = 0.0, 1.0
        if abs(y1 - y0) < 1e-12:
            if not bottom <= y0 <= top:
                continue
        else:
            a, b = sorted(((bottom - y0) / (y1 - y0), (top - y0) / (y1 - y0)))
            lo, hi = max(lo, a), min(hi, b)
            if lo >= hi:
                continue
        graph.start_new_path(axes.c2p(x0 + lo * (x1 - x0), y0 + lo * (y1 - y0)))
        graph.add_line_to(axes.c2p(x0 + hi * (x1 - x0), y0 + hi * (y1 - y0)))
    return graph
