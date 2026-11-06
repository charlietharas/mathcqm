from types import SimpleNamespace

import numpy as np
from manim import (
    Create,
    Dot,
    FadeOut,
    Line,
    SurroundingRectangle,
    Tex,
    Transform,
    UpdateFromAlphaFunc,
    VGroup,
    VMobject,
)

from _helpers import (
    AFFINE,
    EDGE,
    NEURON,
    OUTPUT,
    fit,
    slide_header,
    neuron_layer,
    dense_connections,
)
from scenes._settings import Slide


class MitiDepthSlide(Slide):
    def construct(self):
        # Input representation
        view = self.input_view()
        self.gate(frozen_frame=False)

        # First hidden layer
        self.first_fold(view)

        # Second hidden layer
        self.second_fold(view)

        # Linear separator
        self.readout(view)
        self.gate(frozen_frame=False)

    def input_view(self):
        title = slide_header("Depth")
        intro = Tex("Intermediate layers form intermediate representations.", font_size=31)
        fit(intro, 11.8).move_to([0, 2.25, 0])

        # Recenter each fold and enlarge the final quadrant
        origin = np.array([-1.05, -0.65, 0.0])
        scale = 1.15

        def screen(point, stage=0, alpha=1.0):
            center = np.array(
                [alpha if stage == 1 else float(stage >= 2), alpha if stage == 2 else 0.0]
            )
            zoom = scale + (0.7 * alpha if stage == 2 else 0.0)
            return origin + zoom * np.array([*(point - center), 0.0])

        grid_samples = []
        for v in np.arange(-2.0, 2.01, 0.4):
            grid_samples.append(np.array([[v, t] for t in np.linspace(-2, 2, 81)]))
            grid_samples.append(np.array([[t, v] for t in np.linspace(-2, 2, 81)]))
        observations = example_points()

        def coordinates(point, stage, alpha=1.0):
            point = point.copy()
            if stage >= 1:
                point[0] = (
                    (1 - alpha) * point[0] + alpha * abs(point[0]) if stage == 1 else abs(point[0])
                )
            if stage >= 2:
                point[1] = (1 - alpha) * point[1] + alpha * abs(point[1])
            return point

        def picture(stage=0, alpha=1.0):
            grid = VGroup()
            for samples in grid_samples:
                path = VMobject(stroke_color=EDGE, stroke_width=1, stroke_opacity=0.28)
                path.set_points_as_corners(
                    [screen(coordinates(p, stage, alpha), stage, alpha) for p in samples]
                )
                grid.add(path)
            dots = VGroup(
                *(
                    Dot(
                        screen(coordinates(p, stage, alpha), stage, alpha),
                        radius=0.055,
                        color=NEURON if group == 0 else OUTPUT,
                    )
                    for p, group in observations
                )
            )
            return VGroup(grid, dots)

        plot = picture()
        layers = VGroup()
        for x, count in [(2.3, 2), (3.55, 4), (4.85, 4), (6.1, 1)]:
            ys = np.linspace(0.95, -1.15, count) if count > 1 else [-0.1]
            layers.add(neuron_layer(x, ys, radius=0.13, stroke_width=2))
        edges = VGroup(
            *(
                edge
                for first, second in zip(layers, layers[1:])
                for edge in dense_connections(
                    first, second, boundary=False, stroke_width=1, stroke_opacity=0.4
                )
            )
        )
        stages = VGroup(
            *(
                Tex(label, font_size=22).move_to([x, 1.55, 0])
                for label, x in [("Input", 2.3), ("Layer 1", 3.55), ("Layer 2", 4.85)]
            )
        )
        self.add(title, intro, plot, edges, layers, stages)

        return SimpleNamespace(
            screen=screen, picture=picture, plot=plot, layers=layers, stages=stages
        )

    def first_fold(self, view):
        screen = view.screen
        picture = view.picture
        plot = view.plot
        layers = view.layers
        stages = view.stages

        highlight = SurroundingRectangle(layers[1], buff=0.18, color=AFFINE, stroke_width=2)
        crease = Line(
            screen(np.array([0, -2.0])), screen(np.array([0, 2.0])), color=AFFINE, stroke_width=3
        )
        self.play(
            Create(crease), Create(highlight), stages[1].animate.set_color(AFFINE), run_time=0.65
        )
        self.wait(0.35, frozen_frame=False)

        def crease_frame(stage, alpha):
            points = (
                [np.array([0, -2.0]), np.array([0, 2.0])]
                if stage == 1
                else [np.array([0.0, 0]), np.array([2.0, 0])]
            )
            return Line(*(screen(p, stage, alpha) for p in points), color=AFFINE, stroke_width=3)

        self.play(
            UpdateFromAlphaFunc(plot, lambda m, a: m.become(picture(1, a))),
            UpdateFromAlphaFunc(crease, lambda m, a: m.become(crease_frame(1, a))),
            run_time=2.2,
        )
        self.play(FadeOut(crease), run_time=0.2)
        self.wait(0.35, frozen_frame=False)

        view.crease_frame = crease_frame
        view.highlight = highlight

    def second_fold(self, view):
        crease_frame = view.crease_frame
        highlight = view.highlight
        layers = view.layers
        stages = view.stages
        plot = view.plot
        picture = view.picture
        crease = crease_frame(2, 0)
        self.play(
            Create(crease),
            Transform(
                highlight, SurroundingRectangle(layers[2], buff=0.18, color=AFFINE, stroke_width=2)
            ),
            stages[1].animate.set_color("#FFFFFF"),
            stages[2].animate.set_color(AFFINE),
            run_time=0.65,
        )
        self.wait(0.35, frozen_frame=False)
        self.play(
            UpdateFromAlphaFunc(plot, lambda m, a: m.become(picture(2, a))),
            UpdateFromAlphaFunc(crease, lambda m, a: m.become(crease_frame(2, a))),
            run_time=2.2,
        )
        self.play(FadeOut(crease), FadeOut(highlight), run_time=0.2)

    def readout(self, view):
        screen = view.screen
        separator = Line(
            screen(np.array([0, 1.34]), 2),
            screen(np.array([1.34, 0]), 2),
            color="#FFFFFF",
            stroke_width=3,
        )
        self.play(Create(separator), run_time=0.65)


def example_points():
    # Helper for sample points
    samples = []
    for group, base in enumerate((0.91, 1.76)):
        for i in range(28):
            angle = (i + 0.22 + 0.17 * group) * 2 * np.pi / 28
            direction = np.array([np.cos(angle), np.sin(angle)])
            radius = base + 0.07 * np.sin(2.399963 * (i + 1))
            samples.append((radius * direction / np.abs(direction).sum(), group))
    return samples
