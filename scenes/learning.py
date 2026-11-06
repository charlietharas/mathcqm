import math
import numpy as np
from types import SimpleNamespace
from manim import (
    Create,
    Dot,
    FadeIn,
    FadeOut,
    ReplacementTransform,
    Tex,
    Transform,
    UpdateFromAlphaFunc,
    VGroup,
    VMobject,
    linear,
    Arrow,
    Circle,
    MathTex,
    Star,
)
from _helpers import (
    AFFINE,
    NEURON,
    OUTPUT,
    caption,
    paragraph,
    slide_header,
    function_graph,
    NONLINEARITY,
    fit,
)
from scenes._settings import Slide
from scenes.functions import target

SAMPLE = "#DD8FC7"


from scenes.functions import target


class LearningSlide(Slide):
    def construct(self):
        # Target function
        view = self.target_view()
        self.gate()

        # Observed samples
        self.observations(view)
        self.gate()

        # Functions agreeing at the samples
        self.candidate_functions(view)
        self.gate()

        # An additional observation
        self.additional_observation(view)
        self.gate()

        # Possibilities in the unseen gaps
        self.open_possibilities(view)

        # Approximation, optimization and generalization
        self.questions(view)
        if view.repeat:
            self.next_slide(loop=True, notes="learning-loop")
            self.wait(6, frozen_frame=False)
        self.next_slide()
        if self.loopingLevel:
            view.motion.clear_updaters()

        # Population loss and ideal predictor
        errors = self.error_layout()
        labels = self.population(
            errors,
            view.question_title,
            view.question_labels,
            view.question_texts,
            [view.picture, *([view.motion] if self.loopingLevel else [])],
        )
        self.gate(frozen_frame=False)

        # Approximation error
        self.approximation(errors, labels)
        self.gate(frozen_frame=False)

        # Generalization error
        self.generalization(errors, labels)
        self.gate(frozen_frame=False)

        # Optimization error
        self.optimization(errors, labels)
        self.gate(frozen_frame=False)

    def target_view(self):
        repeat = self.loopingLevel in (1.5, 2)
        graph = function_graph(target)
        title = slide_header("Learning from samples")
        top_caption = caption(r"We don't usually know the true $f$.", y=2.05)
        self.add(title, top_caption, graph.axes, graph.endpoints, graph.curve)

        return SimpleNamespace(repeat=repeat, graph=graph, title=title, top_caption=top_caption)

    def observations(self, view):
        graph = view.graph

        points = [0, 0.25, 0.5, 0.75, 1]
        samples = VGroup(
            *(Dot(graph.axes.c2p(x, target(x)), radius=0.055).set_z_index(4) for x in points)
        )
        self.change_caption(view, "We only have samples of $f$.")
        self.play(FadeIn(samples), FadeOut(graph.curve), run_time=0.6)

        view.points = points
        view.samples = samples

    def candidate_functions(self, view):
        graph = view.graph

        self.change_caption(view, "The same samples can fit (infinitely many) different functions.")
        base = graph.curve.copy().set_color(NEURON)
        alternatives = VGroup(
            *(
                graph.axes.plot(
                    lambda x, s=sign: alternative(x, s),
                    x_range=[0, 1, 0.004],
                    color=color,
                    stroke_width=3,
                )
                for sign, color in [(1, AFFINE), (-1, "#C0D3FB")]
            )
        )
        self.play(Create(base), *(Create(curve) for curve in alternatives), run_time=1.8)

        view.base = base
        view.alternatives = alternatives

    def additional_observation(self, view):
        graph = view.graph
        alternatives = view.alternatives
        base = view.base
        samples = view.samples

        self.change_caption(view, "Additional samples help us rule out candidates.")
        x_new = 0.125
        new_sample = Dot(graph.axes.c2p(x_new, target(x_new)), radius=0.065).set_z_index(4)
        self.play(FadeIn(new_sample), run_time=0.4)
        self.wait(0.4)
        self.play(
            *(Transform(curve, base.copy().set_color(curve.get_color())) for curve in alternatives),
            run_time=0.9,
        )
        self.remove(alternatives, *alternatives.submobjects)
        samples.add(new_sample)

        view.x_new = x_new

    def open_possibilities(self, view):
        repeat = view.repeat
        graph = view.graph
        base = view.base
        points = view.points
        x_new = view.x_new

        if repeat:
            self.next_slide(auto_next=True)
        self.change_caption(view, "But there are still other possibilities.")
        remaining = VGroup(
            *(
                graph.axes.plot(
                    lambda x, s=sign: alternative(x, s, local=True),
                    x_range=[0, 1, 0.0025],
                    color=color,
                    stroke_width=3,
                )
                for sign, color in [(1, AFFINE), (-1, "#C0D3FB")]
            )
        )
        alternatives = VGroup(base.copy(), base.copy())
        self.add(alternatives)
        self.play(
            *(Transform(curve, destination) for curve, destination in zip(alternatives, remaining)),
            run_time=1.3,
        )

        if self.loopingLevel:
            # Keep observations fixed so the loop closes
            xs = np.unique(np.r_[np.linspace(0, 1, 501), points, x_new])
            anchors = sorted(points + [x_new])
            colors = [AFFINE, "#C0D3FB"]

            def moving_frame(phase):
                ys = [possibility_values(xs, anchors, phase, v) for v in (0, 1)]
                curves = VGroup(
                    *(
                        VMobject(color=color, stroke_width=3).set_points_as_corners(
                            [graph.axes.c2p(x, y) for x, y in zip(xs, values)]
                        )
                        for color, values in zip(colors, ys)
                    )
                )
                return curves

            self.remove(alternatives, *alternatives.submobjects)
            motion = moving_frame(0)
            self.add(motion)
            self.play(
                UpdateFromAlphaFunc(
                    motion, lambda mob, alpha: mob.become(moving_frame(alpha)), rate_func=linear
                ),
                run_time=6,
            )
            elapsed = 0.0

            def keep_moving(mob, dt):
                nonlocal elapsed
                elapsed += dt
                mob.become(moving_frame((elapsed / 6) % 1))

            motion.add_updater(keep_moving)
        else:
            self.pause()

        view.alternatives = alternatives
        view.motion = motion if self.loopingLevel else None

    def questions(self, view):
        graph = view.graph
        base = view.base
        samples = view.samples
        alternatives = view.alternatives
        title = view.title
        # Live curves follow the axes during resizing
        picture = VGroup(graph.axes, graph.endpoints, base, samples)
        if not self.loopingLevel:
            picture.add(alternatives)
        self.remove(view.top_caption)
        question_title = slide_header("The Big Questions")
        question_labels, question_texts = [], []
        for name, question, color, y in [
            ("Approximation", "Does our network sufficiently approximate $f$?", AFFINE, 1.3),
            ("Optimization", "Can we find suitable weights for our network?", NEURON, -0.15),
            (
                "Generalization",
                "How well does our network generalize to unseen data?",
                OUTPUT,
                -1.6,
            ),
        ]:
            label = Tex(name, font_size=28, color=color).move_to(
                [0.4, y, 0], aligned_edge=[-1, 0, 0]
            )
            text = paragraph(question, width=5.6, font_size=27)
            text.move_to([0.4, y - 0.52, 0], aligned_edge=[-1, 1, 0])
            question_labels.append(label)
            question_texts.append(text)
            if len(question_labels) == 1:
                self.play(
                    ReplacementTransform(title, question_title),
                    picture.animate.scale(0.58).move_to([-3.5, -0.4, 0]),
                    FadeIn(label),
                    FadeIn(text),
                    run_time=0.45,
                )
            else:
                self.play(FadeIn(label), FadeIn(text), run_time=0.25)
            if len(question_labels) < 3:
                self.wait(0.55, frozen_frame=False)

        view.picture = picture
        view.question_title = question_title
        view.question_labels = question_labels
        view.question_texts = question_texts

    def change_caption(self, view, text):
        replacement = caption(text, y=2.05)
        self.remove(view.top_caption)
        self.add(replacement)
        view.top_caption = replacement

    def pause(self):
        self.wait(1.6)

    def population(self, view, title, labels, questions, outgoing):
        heading = slide_header("Sources of error")
        if title is None:
            labels = list(view.names)
            self.add(
                heading, *labels, view.true_contours, view.true_label, view.ideal, view.ideal_label
            )
        else:
            self.play(
                ReplacementTransform(title, heading),
                *(FadeOut(mob) for mob in [*questions, *outgoing]),
                *(
                    Transform(source, destination.copy().set_opacity(0.3))
                    for source, destination in zip(labels, view.names)
                ),
                FadeIn(view.true_contours),
                FadeIn(view.true_label),
                FadeIn(view.ideal),
                FadeIn(view.ideal_label),
                run_time=1.4,
            )
        for label in labels:
            label.set_opacity(0.3)

        return labels

    def approximation(self, view, labels):

        self.play(
            FadeIn(view.model), FadeIn(view.model_label), FadeIn(view.model_best), run_time=0.7
        )
        self.play(Create(view.connectors[0]), labels[0].animate.set_opacity(1), run_time=1)

    def generalization(self, view, labels):

        self.play(FadeIn(view.sample_contours), FadeIn(view.sample_label), run_time=1.4)
        self.play(
            FadeIn(view.sample_best),
            Create(view.connectors[2]),
            labels[2].animate.set_opacity(1),
            run_time=0.9,
        )

    def optimization(self, view, labels):

        self.play(FadeIn(view.actual), run_time=0.4)
        self.play(Create(view.connectors[1]), labels[1].animate.set_opacity(1), run_time=1)

    @staticmethod
    def error_layout():
        center, radius = [-1.2, 0], 1.65
        true = loss_geometry([1.65, 0.25], [[0.45, 0.35], [0.35, 1]])
        sample = loss_geometry(true.center, [[1, -0.85], [-0.85, 1.2]])
        best_true = best_on_model(true, center, radius)
        best_sample = best_on_model(sample, center, radius)
        trained = np.array([-1.75, -0.8])
        p3 = lambda point: np.r_[point, 0]

        def contours(geometry, levels, color):
            # Draw outer contours first so shading builds toward the minimum
            levels = sorted(levels, reverse=True)
            values, vectors = np.linalg.eigh(geometry.matrix)
            angles = np.linspace(0, 2 * np.pi, 241)
            unit = np.array([np.cos(angles), np.sin(angles)])
            paths = []
            for i, level in enumerate(levels):
                points = geometry.center[:, None] + vectors @ (
                    (level / np.sqrt(values))[:, None] * unit
                )
                path = VMobject(
                    color=color, stroke_width=1, stroke_opacity=0.35, fill_opacity=0.03 + 0.015 * i
                )
                path.set_points_smoothly(np.c_[points.T, np.zeros(len(angles))])
                path.close_path()
                paths.append(path)
            return VGroup(*paths)

        true_levels = [0.4, 1.25, 1.75, np.sqrt(true.loss(best_true))]
        sample_levels = [0.3, 0.65, 1.25, np.sqrt(sample.loss(best_sample))]
        true_contours = contours(true, true_levels, AFFINE)
        sample_contours = contours(sample, sample_levels, SAMPLE)
        model = Circle(
            radius=radius, color=NONLINEARITY, stroke_width=2, fill_opacity=0.11
        ).move_to(p3(center))
        model_label = Tex("Model space", font_size=25, color=NONLINEARITY)
        model_label.next_to(model, [0, 1, 0], buff=0.18)
        true_label = Tex("Population loss", font_size=27, color=AFFINE)
        true_label.next_to(true_contours, [0, 1, 0], buff=0.16)
        sample_label = Tex("Empirical loss", font_size=27, color=SAMPLE)
        sample_label.next_to(sample_contours, [1, 0, 0], buff=0.2)
        ideal = (
            Star(n=5, outer_radius=0.14, inner_radius=0.065, color="#FFFFFF", fill_opacity=1)
            .move_to(p3(true.center))
            .set_z_index(4)
        )
        ideal_label = MathTex(r"f^\star", font_size=26).next_to(ideal, [1, 1, 0], buff=0.1)
        model_best = Dot(p3(best_true), radius=0.09, color=AFFINE).set_z_index(4)
        sample_best = Dot(p3(best_sample), radius=0.09, color=SAMPLE).set_z_index(4)
        actual = Dot(p3(trained), radius=0.09, color=NEURON).set_z_index(4)
        connectors = VGroup(
            *(
                Arrow(
                    p3(start),
                    p3(end),
                    buff=0.12,
                    color=color,
                    stroke_width=3,
                    tip_length=0.14,
                    max_tip_length_to_length_ratio=1,
                ).set_z_index(3)
                for start, end, color in [
                    (best_true, true.center, AFFINE),
                    (trained, best_sample, NEURON),
                    (best_sample, best_true, OUTPUT),
                ]
            )
        )
        names = VGroup()
        for name, color, x in [
            ("Approximation", AFFINE, -4.1),
            ("Optimization", NEURON, 0),
            ("Generalization", OUTPUT, 4.1),
        ]:
            names.add(fit(Tex(name, font_size=27, color=color), 3.5).move_to([x, -3.0, 0]))
        return SimpleNamespace(
            true=true,
            sample=sample,
            center=center,
            radius=radius,
            best_true=best_true,
            best_sample=best_sample,
            trained=trained,
            true_contours=true_contours,
            sample_contours=sample_contours,
            model=model,
            model_label=model_label,
            true_label=true_label,
            sample_label=sample_label,
            ideal=ideal,
            ideal_label=ideal_label,
            model_best=model_best,
            sample_best=sample_best,
            actual=actual,
            connectors=connectors,
            names=names,
        )


def alternative(x, sign=1, *, local=False):
    # Oscillating/undulating functions
    if local:
        bump = 0.24 * math.sin(4 * math.pi * (x - 0.5)) ** 2 if 0.5 < x < 0.75 else 0
    else:
        bump = 0.22 * math.sin(4 * math.pi * x)
    return target(x) + sign * bump


def possibility_values(xs, anchors, phase, variant=0):
    # Helper for undulations
    xs, anchors = np.asarray(xs), np.sort(anchors)
    index = np.clip(np.searchsorted(anchors, xs, side="right") - 1, 0, len(anchors) - 2)
    left, right = anchors[index], anchors[index + 1]
    u = (xs - left) / (right - left)
    angle = 2 * np.pi * phase
    seed = (index + 1) * 2.399963 + variant * 1.7
    offset = (1 if variant == 0 else -1) * ((left >= 0.5) & (right <= 0.75))
    motion = (
        0.65 * np.sin(angle) * np.cos(seed)
        + 0.2 * np.sin(2 * angle) * np.sin(seed)
        + 0.25 * np.sin(angle) * np.sin(2 * np.pi * u + variant * np.pi)
    )
    bump = 0.24 * (right - left) / 0.25 * np.sin(np.pi * u) ** 2 * (offset + 1.6 * motion)
    return 0.65 + 0.4 * np.sin(2 * np.pi * xs) + 0.3 * xs + bump


def loss_geometry(center, matrix):
    center = np.array(center)
    matrix = np.array(matrix)

    def loss(points):
        delta = np.asarray(points) - center
        return np.einsum("...i,ij,...j->...", delta, matrix, delta)

    return SimpleNamespace(center=center, matrix=matrix, loss=loss)


def best_on_model(geometry, center, radius):
    # Place the dots
    center = np.asarray(center)
    if np.linalg.norm(geometry.center - center) <= radius:
        return geometry.center.copy()
    rhs = geometry.matrix @ (geometry.center - center)

    def offset(multiplier):
        return np.linalg.solve(geometry.matrix + multiplier * np.eye(2), rhs)

    lo, hi = 0.0, 1.0
    while np.linalg.norm(offset(hi)) > radius:
        hi *= 2
    for _ in range(70):
        mid = (lo + hi) / 2
        if np.linalg.norm(offset(mid)) > radius:
            lo = mid
        else:
            hi = mid
    return center + offset(hi)
