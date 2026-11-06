from types import SimpleNamespace

import math

from manim import (
    DoubleArrow,
    BLACK,
    GrowFromCenter,
    Dot,
    ManimColor,
    FadeIn,
    MathTex,
    Rectangle,
    Square,
    Transform,
    VGroup,
    interpolate_color,
)

from _helpers import AFFINE, MUTED, NEURON, OUTPUT, fit, caption, slide_header, plot_axes
from scenes._settings import Slide


class ExponentialsSlide(Slide):
    def construct(self):
        # One input coordinate
        self.interval_view()
        self.gate()

        # Two input coordinates
        self.second_coordinate()
        self.gate()

        # Coordinate restrictions
        self.clear()
        view = self.coordinate_restrictions()
        self.gate()

        # Sum
        self.play(FadeIn(view.result), run_time=0.6)
        self.gate()

        # Product
        self.multiply_restrictions(view)
        self.gate()

        # ReLU obstruction
        self.clear()
        self.relu_obstruction()
        self.gate()

        # Exponential activation
        self.exponential_activation()
        self.gate()

        # Closure under multiplication
        self.exponential_product()
        self.gate()

    def interval_view(self):
        title = slide_header("Mixing information")
        segment = DoubleArrow(
            [-4.5, 0, 0], [4.5, 0, 0], buff=0, stroke_width=1.5, tip_length=0.12, color=MUTED
        )
        point = Dot([1.6, 0, 0], radius=0.09, color=NEURON)
        self.add(title, segment, point)

    def second_coordinate(self):
        second_axis = DoubleArrow(
            [0, -2.5, 0], [0, 2.5, 0], buff=0, stroke_width=1.5, tip_length=0.12, color=MUTED
        )
        self.play(GrowFromCenter(VGroup(second_axis)), run_time=0.8)

    def coordinate_restrictions(self):
        title = slide_header("Mixing information")
        note = caption(
            "Consider restricting a function to a small rectangle.", y=2.45, font_size=29
        )
        centers = [(-4.7, -0.5), (-1.35, -0.5), (3.5, -0.5)]
        sizes = [2.5, 2.5, 3.5]
        frames = VGroup(
            *(
                Square(side_length=size, color=MUTED, stroke_width=1.5).move_to([*center, 0])
                for center, size in zip(centers, sizes)
            )
        )
        frames.set_z_index(2)
        inputs = VGroup(field("u", centers[0], sizes[0]), field("v", centers[1], sizes[1]))
        input_labels = VGroup(
            MathTex(r"u(x_1)", font_size=33, color=AFFINE).move_to([-4.7, 1.15, 0]),
            MathTex(r"v(x_2)", font_size=33, color=OUTPUT).move_to([-1.35, 1.15, 0]),
        )
        axis_labels = VGroup()
        for center, size in zip(centers, sizes):
            axis_labels.add(
                MathTex("x_1", font_size=22).move_to([center[0], center[1] - size / 2 - 0.23, 0]),
                MathTex("x_2", font_size=22).move_to([center[0] - size / 2 - 0.25, center[1], 0]),
            )
        formula = MathTex(r"u(x_1)+v(x_2)", font_size=37).move_to([3.5, 1.85, 0])
        result = field("sum", centers[2], sizes[2])
        self.add(title, note, inputs, frames, input_labels, axis_labels, formula)

        return SimpleNamespace(result=result, formula=formula, centers=centers, sizes=sizes)

    def multiply_restrictions(self, view):
        result = view.result
        formula = view.formula
        centers = view.centers
        sizes = view.sizes
        product_formula = MathTex(r"u(x_1)v(x_2)", font_size=37).move_to(formula)
        self.play(
            Transform(result, field("product", centers[2], sizes[2])),
            Transform(formula, product_formula),
            run_time=1,
        )

    def relu_obstruction(self):
        title = slide_header("Mixing information")
        obstruction = caption("ReLU sums are not closed under multiplication.", 2.3, font_size=29)
        relu_product = MathTex(
            r"\operatorname{ReLU}(x)^2=x^2\quad(x\geq0)" r"\qquad\text{is not piecewise-linear.}",
            font_size=32,
        )
        fit(relu_product, 11.6).move_to([0, 1.6, 0])
        self.add(title, obstruction, relu_product)

    def exponential_activation(self):

        neuron = MathTex(r"\sigma(t)=\exp(t)=e^t", font_size=36, color=NEURON).move_to(
            [-2.8, 0.35, 0]
        )
        explanation = MathTex(r"x\longmapsto\sigma(w^\top x)=e^{w^\top x}", font_size=32).move_to(
            [-2.8, -0.45, 0]
        )
        axes = plot_axes(
            x_range=[-2, 1.5, 1],
            y_range=[0, 5, 1],
            x_length=3.1,
            y_length=1.85,
            center=[3.6, -0.05, 0],
        )
        curve = axes.plot(math.exp, x_range=[-2, 1.5], color=NEURON, stroke_width=3)
        labels = VGroup(
            MathTex("t", font_size=24).next_to(axes.x_axis.get_end(), [1, 0, 0], buff=0.1),
            MathTex("e^t", font_size=27, color=NEURON).move_to([4.35, 0.9, 0]),
        )
        self.add(neuron, explanation, axes, curve, labels)

    def exponential_product(self):

        payoff = caption(
            "Exponential neurons are closed under multiplication.", -1.85, font_size=29
        )
        product = MathTex(
            r"e^{u^\top x}", r"e^{v^\top x}", "=", r"e^{(u+v)^\top x}", font_size=40
        ).move_to([0, -2.65, 0])
        product[0].set_color(AFFINE)
        product[1].set_color(OUTPUT)
        product[3].set_color(NEURON)
        self.add(payoff, fit(product, 11.6))


def restriction(t, center):
    return max(0, 1 - abs(t - center) / 0.2)


def field(kind, center, size):
    cells = VGroup()
    n = 24
    for j in range(n):
        for i in range(n):
            u = restriction((i + 0.5) / n, 0.4)
            v = restriction((j + 0.5) / n, 0.6)
            value = {"u": u, "v": v, "sum": (u + v) / 2, "product": u * v}[kind]
            color = {"u": AFFINE, "v": OUTPUT}.get(kind, NEURON)
            cell = Rectangle(
                width=size / n + 0.003,
                height=size / n + 0.003,
                stroke_width=0,
                fill_color=interpolate_color(BLACK, ManimColor(color), value),
                fill_opacity=1,
            )
            cell.move_to(
                [
                    center[0] + size * ((i + 0.5) / n - 0.5),
                    center[1] + size * ((j + 0.5) / n - 0.5),
                    0,
                ]
            )
            cells.add(cell)
    return cells
