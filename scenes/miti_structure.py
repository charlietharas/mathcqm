from types import SimpleNamespace

import numpy as np
from manim import (
    Arrow,
    Circle,
    Create,
    Dot,
    FadeIn,
    Line,
    MathTex,
    Rectangle,
    Tex,
    Transform,
    VGroup,
    VMobject,
    WHITE,
)
from _helpers import AFFINE, EDGE, NEURON, fit, dimmed, quote_layout, slide_header
from scenes._settings import Slide


class MitiStructureSlide(Slide):
    def construct(self):
        # Manifold hypothesis
        view = self.manifold_view()
        self.gate(frozen_frame=False)

        # Symmetry
        self.symmetry_quote(view)
        self.gate(frozen_frame=False)

        # Convolutional and graph networks
        self.architectures(view)
        self.gate(frozen_frame=False)

        # Translation
        self.translate_image(view)
        self.gate(frozen_frame=False)

        # Graph highlight
        self.highlight_graph(view)
        self.gate(frozen_frame=False)

        # Permutation
        self.permute_graph(view)
        self.gate(frozen_frame=False)

    def manifold_view(self):
        heading = slide_header("Structure")
        intro = Tex("Manifold hypothesis", font_size=32).move_to([0, 2.05, 0])
        axes, mesh, samples = manifold_picture()
        VGroup(axes, mesh, samples).shift([0, -0.35, 0])
        self.add(heading, intro, axes)
        self.play(Create(mesh), FadeIn(samples), run_time=1.6)

        return SimpleNamespace(heading=heading)

    def symmetry_quote(self, view):
        heading = view.heading

        self.clear()
        weyl = quote_layout(
            "``Symmetry, as wide or as narrow as you may define its meaning, "
            "is one idea by which man through the ages has tried to comprehend "
            "and create order, beauty and perfection.'' "
            r"(\textit{Symmetry}, 1952)",
            author="Hermann Weyl",
            source="Weyl 1952",
            portrait="assets/weyl-portrait.jpg",
            portrait_size=(3.0, 4.2),
        )
        self.add(heading, weyl.root)

    def architectures(self, view):
        heading = view.heading
        self.clear()
        self.add(heading)

        left_title = fit(Tex("Convolutional networks", font_size=31), 5.6).move_to([-3.3, 2.15, 0])
        right_title = fit(Tex("Graph networks", font_size=31), 5.6).move_to([3.3, 2.15, 0])
        left_sub = Tex("Translation invariance", font_size=26, color=AFFINE).move_to([-3.3, 1.3, 0])
        right_sub = Tex("Permutation invariance", font_size=26, color=AFFINE).move_to([3.3, 1.3, 0])
        image, response = convolution_example()
        flow = Arrow(
            [-3.3, -0.20, 0],
            [-3.3, -0.52, 0],
            buff=0,
            color=EDGE,
            stroke_width=2,
            max_tip_length_to_length_ratio=0.3,
        )
        VGroup(image, response, flow).shift([0, -0.5, 0])
        lines, nodes, labels, positions = graph_example()
        VGroup(lines, nodes, labels).scale(1.2, about_point=[3.3, -0.1, 0])
        VGroup(lines, nodes, labels).shift([0, -0.5, 0])
        positions = [node.get_center().copy() for node in nodes]
        left = VGroup(left_title, left_sub, image, response, flow)
        right = VGroup(right_title, right_sub, lines, nodes, labels)
        right_full = right.copy()
        right.become(dimmed(right))
        self.play(FadeIn(left), FadeIn(right), run_time=0.6)

        view.image = image
        view.response = response
        view.left = left
        view.right = right
        view.right_full = right_full
        view.positions = positions
        view.labels = labels

    def translate_image(self, view):
        image = view.image
        response = view.response
        shifted_image, shifted_response = convolution_example(shift=2)
        VGroup(shifted_image, shifted_response).shift([0, -0.5, 0])
        permutation = [2, 4, 1, 0, 3]
        self.play(
            Transform(image, shifted_image), Transform(response, shifted_response), run_time=1.4
        )

        view.permutation = permutation

    def highlight_graph(self, view):
        left = view.left
        right = view.right
        right_full = view.right_full
        self.play(Transform(left, dimmed(left)), Transform(right, right_full), run_time=0.4)

    def permute_graph(self, view):
        labels = view.labels
        positions = view.positions
        permutation = view.permutation
        self.play(
            *(label.animate.move_to(positions[permutation[i]]) for i, label in enumerate(labels)),
            run_time=1.4,
        )


def sheet_point(u, v):
    # Point on the manifold
    z = 0.42 * np.sin(1.5 * u) + 0.23 * v * v
    return np.array([1.8 * u + 0.65 * v, 0.65 * v + 1.4 * z - 0.15, 0.0])


def manifold_picture():
    mesh = VGroup()
    us = np.linspace(-1.55, 1.55, 60)
    vs = np.linspace(-1.15, 1.15, 40)
    for v in np.linspace(-1.15, 1.15, 11):
        mesh.add(
            VMobject(color=AFFINE, stroke_width=1.25, stroke_opacity=0.65).set_points_smoothly(
                [sheet_point(u, v) for u in us]
            )
        )
    for u in np.linspace(-1.55, 1.55, 15):
        mesh.add(
            VMobject(color=AFFINE, stroke_width=1.25, stroke_opacity=0.65).set_points_smoothly(
                [sheet_point(u, v) for v in vs]
            )
        )
    rng = np.random.default_rng(8)
    points = VGroup(
        *(
            Dot(sheet_point(u, v), radius=0.045, color=NEURON)
            for u, v in rng.uniform([-1.5, -1.1], [1.5, 1.1], (80, 2))
        )
    )
    origin = np.array([-3.9, -1.7, 0.0])
    axes = VGroup(
        *(
            Arrow(
                origin,
                origin + direction,
                buff=0,
                color=EDGE,
                stroke_width=1.5,
                max_tip_length_to_length_ratio=0.07,
            )
            for direction in [
                np.array([7.8, 0, 0]),
                np.array([1.5, 1.05, 0]),
                np.array([0, 3.3, 0]),
            ]
        )
    )
    return axes, mesh, points


def pixel_map(values, center, *, color):
    size = 0.29
    rows, cols = values.shape
    cells, active = VGroup(), VGroup()
    for row in range(rows):
        for col in range(cols):
            value = float(values[row, col])
            cell = Rectangle(
                width=size,
                height=size,
                stroke_color=EDGE,
                stroke_width=0.5,
                stroke_opacity=0.6,
                fill_opacity=0,
            )
            cell.move_to(
                np.array(center) + [(col - (cols - 1) / 2) * size, ((rows - 1) / 2 - row) * size, 0]
            )
            cells.add(cell)
            if value > 0:
                active.add(
                    Rectangle(
                        width=size,
                        height=size,
                        stroke_width=0,
                        fill_color=color,
                        fill_opacity=0.85 * value,
                    ).move_to(cell)
                )
    return VGroup(cells, active)


def convolution_example(shift=0):
    image = np.zeros((5, 9))
    image[1:3, 2 + shift] = 1
    image[2, 3 + shift] = 1
    kernel = np.array([[1.0, 0.0], [1.0, 1.0]])
    padded = np.pad(image, ((0, 1), (0, 1)))
    response = np.array(
        [[np.sum(padded[r : r + 2, c : c + 2] * kernel) / 3 for c in range(9)] for r in range(5)]
    )
    return pixel_map(image, [-3.3, 0.65, 0], color=WHITE), pixel_map(
        response, [-3.3, -1.25, 0], color=NEURON
    )


def graph_example():
    center = np.array([3.3, -0.1, 0.0])
    points = [
        center + np.array(p)
        for p in [
            (-1.15, 0.6, 0),
            (0.05, 1.05, 0),
            (1.15, 0.35, 0),
            (0.7, -0.9, 0),
            (-0.8, -0.8, 0),
        ]
    ]
    edges = [(0, 1), (0, 4), (1, 2), (1, 4), (2, 3), (3, 4)]
    lines = VGroup(*(Line(points[a], points[b], color=EDGE, stroke_width=2) for a, b in edges))
    nodes = VGroup(
        *(
            Circle(
                radius=0.20, color=NEURON, stroke_width=2, fill_color="#000000", fill_opacity=1
            ).move_to(p)
            for p in points
        )
    )
    labels = VGroup(*(MathTex(str(i + 1), font_size=23).move_to(p) for i, p in enumerate(points)))
    return lines, nodes, labels, points
