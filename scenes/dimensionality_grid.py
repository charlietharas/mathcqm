from types import SimpleNamespace

import numpy as np
from manim import Line, Polygon, VGroup, ValueTracker, always_redraw
from _helpers import AFFINE, MUTED, slide_header
from scenes._settings import Slide


class DimensionalityGridSlide(Slide):
    def construct(self):
        view = self.grid_view()

        # Interval
        self.add(view.interval, view.ticks, view.highlight)
        self.gate()

        # Square
        self.remove(view.interval, view.ticks)
        lattice = always_redraw(view.grid)
        self.add(lattice)
        self.play(view.height.animate.set_value(1), run_time=1.8)
        self.gate()

        # Cube
        self.play(view.depth.animate.set_value(1), run_time=2.2)
        lattice.clear_updaters()
        view.highlight.clear_updaters()
        self.gate()

        # Curse of dimensionality
        self.add(slide_header("The Curse of Dimensionality"))
        self.gate()

    def grid_view(self):
        origin = np.array([-2.6, -2.25, 0.0])
        ex = np.array([4.0, 0, 0])
        ey = np.array([0, 3.6, 0])
        ez = np.array([1.25, 0.95, 0])
        height = ValueTracker(0)
        depth = ValueTracker(0)

        def grid():
            h, d = height.get_value(), depth.get_value()
            base = origin + (1 - h) * ey / 2
            lines = VGroup()
            for i in range(11):
                t = i / 10
                for k in range(11 if d > 0 else 1):
                    offset = ez * d * k / 10
                    if h > 0:
                        lines.add(
                            Line(
                                base + ex * t + offset,
                                base + ex * t + ey * h + offset,
                                color=MUTED,
                                stroke_width=1,
                                stroke_opacity=0.5,
                            )
                        )
                    lines.add(
                        Line(
                            base + ey * h * t + offset,
                            base + ex + ey * h * t + offset,
                            color=MUTED,
                            stroke_width=1,
                            stroke_opacity=0.5,
                        )
                    )
                if d > 0:
                    for j in range(11):
                        start = base + ex * t + ey * h * j / 10
                        lines.add(
                            Line(
                                start,
                                start + ez * d,
                                color=MUTED,
                                stroke_width=0.7,
                                stroke_opacity=0.3,
                            )
                        )
            return lines

        def region():
            h, d = height.get_value(), depth.get_value()
            base = origin + (1 - h) * ey / 2 + ex * 0.6 + ey * h * 0.4 + ez * d * 0.4
            dx, dy, dz = ex / 10, ey * h / 10, ez * d / 10
            if h == 0:
                return VGroup(Line(base, base + dx, color=AFFINE, stroke_width=5))
            front = [base, base + dx, base + dx + dy, base + dy]
            faces = VGroup(
                Polygon(*front, color=AFFINE, stroke_width=2, fill_color=AFFINE, fill_opacity=0.35)
            )
            if d > 0:
                faces.add(
                    Polygon(
                        *(p + dz for p in front),
                        color=AFFINE,
                        stroke_width=2,
                        fill_color=AFFINE,
                        fill_opacity=0.25,
                    )
                )
                for a, b in zip(front, front[1:] + front[:1]):
                    faces.add(
                        Polygon(
                            a,
                            b,
                            b + dz,
                            a + dz,
                            color=AFFINE,
                            stroke_width=1.5,
                            fill_color=AFFINE,
                            fill_opacity=0.2,
                        )
                    )
            return faces.set_z_index(3)

        highlight = always_redraw(region)
        interval = Line(origin + ey / 2, origin + ey / 2 + ex, color=MUTED, stroke_width=1.5)
        ticks = VGroup(
            *(
                Line(
                    origin + ey / 2 + ex * i / 10 + [0, -0.07, 0],
                    origin + ey / 2 + ex * i / 10 + [0, 0.07, 0],
                    color=MUTED,
                    stroke_width=1,
                )
                for i in range(11)
            )
        )

        return SimpleNamespace(
            interval=interval,
            ticks=ticks,
            highlight=highlight,
            height=height,
            depth=depth,
            grid=grid,
        )
