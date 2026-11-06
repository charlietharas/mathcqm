import numpy as np
from manim import DOWN, Tex, UpdateFromAlphaFunc, VGroup, VMobject, linear

from _helpers import AFFINE, NEURON, OUTPUT
from scenes._settings import Slide


class ThanksSlide(Slide):
    def construct(self):
        ring = closing_ring(0)
        thanks = Tex("Thank you for coming!", font_size=48)
        sources = Tex(
            r"(sources etc. at \underline{charliemax.dev/projects/cqm26})", font_size=23
        ).next_to(thanks, DOWN, buff=0.4)
        self.add(ring, thanks, sources)
        if not self.loopingLevel:
            self.gate(frozen_frame=False)
            return

        # Configure looping level
        if self.loopingLevel in (1.5, 2):
            self.next_slide(loop=True, notes="thanks-loop")
        self.play(
            UpdateFromAlphaFunc(
                ring, lambda mob, phase: mob.become(closing_ring(phase)), rate_func=linear
            ),
            run_time=8,
        )
        self.next_slide()


def closing_ring(phase):
    theta = np.linspace(0, 2 * np.pi, 401)
    angle = 2 * np.pi * phase
    contours = VGroup()
    for index, color in enumerate((AFFINE, NEURON, OUTPUT)):
        offset = index * 0.8
        ripple = 0.035 * np.sin(5 * theta + angle + offset) + 0.018 * np.sin(
            9 * theta - 2 * angle - offset
        )
        radius = 1 + ripple - index * 0.025
        points = np.column_stack(
            (6.25 * radius * np.cos(theta), 3.25 * radius * np.sin(theta), np.zeros_like(theta))
        )
        contour = VMobject(
            stroke_color=color, stroke_width=1.7, stroke_opacity=(0.55, 0.8, 0.4)[index]
        )
        contour.set_points_smoothly(points)
        contours.add(contour)
    return contours
