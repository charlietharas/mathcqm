import math
import numpy as np
from functools import partial
from types import SimpleNamespace
from manim import (
    Create,
    RIGHT,
    FadeIn,
    FadeOut,
    Line,
    MathTex,
    DOWN,
    ReplacementTransform,
    Tex,
    Transform,
    VGroup,
    WHITE,
    Write,
    Dot,
    DoubleArrow,
    Polygon,
    Uncreate,
    Unwrite,
    UpdateFromAlphaFunc,
    ValueTracker,
    always_redraw,
    BraceBetweenPoints,
    DashedLine,
)
from _helpers import (
    AFFINE,
    NONLINEARITY,
    OUTPUT,
    slide_header,
    theorem_layout,
    epsilon_brace,
    equation,
    caption,
    named_group,
    curve_band,
    function_graph,
    vertical_grid,
    tolerance_box,
    NEURON,
    prose,
    plot_axes,
)
from scenes._settings import Slide

preamble_equation = partial(
    equation,
    width=12,
    font_size=44,
    substrings_to_isolate=[r"\varepsilon", r"\delta", r"\|x-y\|_2"],
)
bottom_caption = partial(caption, y=-3.25, width=12.4, font_size=29)
proof_text = partial(prose, font_size=32)
proof_equation = partial(equation, width=11, font_size=40, x=-5.2, align=[-1, 0, 0])


class FunctionsSlide(Slide):
    def construct(self):
        views = self.views()
        compact, continuity, classes = views.compact, views.continuity, views.classes
        norm, error = views.norm, views.error

        # Targets
        self.add(views.targets)
        self.gate()

        # Compactness theorem
        self.clear()
        self.add(compact.heading, compact.theorem)
        self.gate()

        # Compactness of the input cube
        self.add(compact.application, compact.closed, compact.bounded)
        self.gate()

        # Uniform continuity
        self.clear()
        self.add(continuity.heading, continuity.theorem)
        self.gate()
        self.play(Write(continuity.quantifiers), run_time=2)
        self.play(Write(continuity.implication), run_time=2)
        self.gate()
        self.play(FadeIn(continuity.comparison), run_time=0.4)
        self.gate()

        # Function classes
        self.clear()
        self.add(
            classes.heading,
            classes.target_text,
            classes.target_class,
            classes.network_text,
            classes.network_class,
            classes.inclusion,
        )
        self.gate()
        self.add(classes.question)
        self.gate()

        # Uniform norm
        self.clear()
        self.add(norm.heading, norm.caption)
        self.play(Write(norm.formula), run_time=2)
        self.gate()

        # Approximation error on the same graph
        centered_error = self.approximation_error(norm, error)
        self.gate()

        # Persistent target graph
        illustration = self.continuity_graph(
            self.function_graph, (norm.heading, self.norm_decorations(error, centered_error))
        )
        self.gate(0.15)

        # Epsilon-delta window
        self.tolerance_window(illustration)
        self.gate(0.15)

        # One tolerance across the domain
        self.sweep_window(illustration)
        self.gate(0.15)

        # Finite partition
        self.partition(illustration)
        self.gate(0.15)

        # Representative point
        self.representative(illustration)
        self.gate(0.15)

        # Piecewise-constant approximation
        self.staircase(illustration)
        self.gate(0.15)

        # Finer partition
        self.refine(illustration)
        self.gate(0.15)

        # One-dimensional proof
        self.begin_proof(illustration.heading)
        proof = self.proof_views()

        # Uniform continuity
        self.clear()
        self.add(proof.continuity.root)
        self.gate()

        # Grid, interpolation and endpoint bounds
        self.clear()
        self.proof_grid(proof.grid, proof.interpolant, proof.endpoints)

        # Approximation estimate
        self.clear()
        self.add(proof.estimate.heading, proof.estimate.intro)
        rows = [
            proof.estimate.equality,
            proof.estimate.triangle,
            proof.estimate.bound,
            proof.estimate.simplified,
        ]
        for step, row in enumerate(rows):
            # Highlight the current step; leave the completed estimate white
            for previous in rows:
                previous.set_color(WHITE)
            if step == 1:
                for part in (3, 8):
                    row[part].set_color(NEURON)
            elif step == 2:
                for part in (1, 4):
                    row[part].set_color(OUTPUT)
            self.add(row)
            self.gate()

        # Uniform bound
        self.clear()
        self.add(proof.conclusion.root)
        self.gate()

    def approximation_error(self, norm, error):
        # Keep the norm and supremum fixed while replacing f
        centered_error = error.formula.copy().move_to(norm.formula)
        self.play(
            *(
                ReplacementTransform(source, target)
                for source, target in zip(norm.formula, centered_error[:-1])
            ),
            Write(centered_error[-1]),
            run_time=1.4,
        )
        self.remove(norm.formula)
        self.add(centered_error)
        self.play(
            FadeOut(norm.caption),
            centered_error.animate.move_to(error.formula),
            FadeIn(error.axes),
            FadeIn(error.labels[:2]),
            run_time=0.7,
        )
        self.play(Create(error.target), run_time=2)
        self.play(FadeIn(error.labels[2]), run_time=0.25)
        self.play(Create(error.approximation), run_time=2)
        self.play(FadeIn(error.labels[3]), run_time=0.25)
        self.play(Create(error.bounds), run_time=1.2)
        self.play(FadeIn(error.band), FadeIn(error.epsilon), run_time=0.45)

        return centered_error

    def begin_proof(self, proof_heading):
        # Keep the heading for the proof transition
        for mobject in list(self.mobjects):
            if mobject is not proof_heading:
                self.remove(mobject)
        self.add(*self.proof_views().continuity.root[1:])
        self.play(
            Transform(proof_heading, slide_header("One-dimensional approximation")), run_time=0.7
        )
        self.clear()

    def views(self):
        inputs = VGroup(
            slide_header("Targets"),
            caption("An input is a list of $d$ numbers", 1.9, font_size=28).move_to([-3.2, 1.9, 0]),
            preamble_equation(r"x\in K=[0,1]^d", y=0.45, color=AFFINE).move_to([-3.2, 0.45, 0]),
            Tex(r"The target is the rule we want\\the network to imitate.", font_size=28).move_to(
                [3.2, 1.75, 0]
            ),
            preamble_equation(
                r"f:K\longrightarrow\mathbb{R}", y=0.45, color=OUTPUT, font_size=44
            ).move_to([3.2, 0.45, 0]),
            caption("We assume $f$ is continuous.", -0.85, color=OUTPUT, font_size=30).move_to(
                [3.2, -0.85, 0]
            ),
        )
        borel = theorem_layout(
            "Heine-Borel",
            r"A subset $A\subseteq\mathbb{R}^d$ is \textbf{compact} iff. it is closed and bounded.",
        )
        compact = named_group(
            heading=slide_header("Compactness"),
            theorem=borel.root,
            application=caption(
                r"Claim: $K=[0,1]^d\subseteq\mathbb{R}^d$ is compact:", 0.25, font_size=32
            ).align_to(borel.root, [-1, 0, 0]),
            closed=preamble_equation(
                r"\text{Closed: }\quad x_n\in K,\ x_n\to x"
                r"\ \Longrightarrow\ 0\leq x_i\leq1\ \Longrightarrow\ x\in K",
                y=-0.8,
                font_size=32,
            )
            .align_to(borel.root, [-1, 0, 0])
            .shift([0.6, 0, 0]),
            bounded=preamble_equation(
                r"\text{Bounded: }\quad \forall x\in K,\quad "
                r"\|x\|_2=\sqrt{\sum_{i=1}^d x_i^2}\leq\sqrt{d}",
                y=-2.0,
                font_size=34,
            )
            .align_to(borel.root, [-1, 0, 0])
            .shift([0.6, 0, 0]),
        )
        cantor = theorem_layout(
            "Heine-Cantor",
            r"Let $K\subseteq\mathbb{R}^d$ be compact. If $f:K\to\mathbb{R}$ is continuous, then $f$ is \textbf{uniformly continuous}:",
        )
        continuity = named_group(
            heading=slide_header("Uniform Continuity"),
            theorem=cantor.root,
            quantifiers=preamble_equation(
                r"\forall\varepsilon>0.\;\exists\delta>0.\;\forall x,y\in K:", y=0.75, font_size=38
            ).align_to(cantor.root, [-1, 0, 0]),
            implication=preamble_equation(
                r"\|x-y\|_2<\delta\quad\Longrightarrow\quad " r"|f(x)-f(y)|<\varepsilon",
                y=-0.05,
                font_size=38,
            )
            .align_to(cantor.root, [-1, 0, 0])
            .shift([0.6, 0, 0]),
        )
        continuity.quantifiers.next_to(cantor.root, DOWN, buff=0.32).align_to(
            cantor.root, [-1, 0, 0]
        )
        continuity.implication.next_to(continuity.quantifiers, DOWN, buff=0.3).align_to(
            cantor.root, [-1, 0, 0]
        ).shift([0.6, 0, 0])
        for formula in (continuity.quantifiers, continuity.implication):
            formula.set_color_by_tex(r"\varepsilon", OUTPUT)
            formula.set_color_by_tex(r"\delta", NONLINEARITY)
        comparison_rows = VGroup()
        for label, parts, y in [
            (
                "Ordinary:",
                [r"\forall x\in K", r"\forall\varepsilon>0", r"\exists\delta>0", r"\forall y\in K"],
                -1.85,
            ),
            ("Uniform:", [r"\forall\varepsilon>0", r"\exists\delta>0", r"\forall x,y\in K"], -2.65),
        ]:
            formula = MathTex(*parts, font_size=30, arg_separator=r"\; ")
            for part in formula:
                if r"\varepsilon" in part.tex_string:
                    part.set_color(OUTPUT)
                elif r"\delta" in part.tex_string:
                    part.set_color(NONLINEARITY)
                elif "x" in part.tex_string:
                    part.set_color(AFFINE)
            row = VGroup(Tex(label, font_size=29), formula).arrange(RIGHT, buff=0.3)
            row.move_to([-5.8, y, 0], aligned_edge=[-1, 0, 0])
            comparison_rows.add(row)
        continuity.comparison = comparison_rows
        continuity.root.add(comparison_rows)
        classes = named_group(
            heading=slide_header("Function Classes"),
            target_text=VGroup(
                caption("Our targets live in the", 2.0, x=-3.25, baseline=True),
                caption("continuous function class", 1.6, x=-3.25, baseline=True),
            ),
            target_class=MathTex(
                r"\begin{gathered}\mathstrut C(K)=\{f:K\to\mathbb{R}\mid\\"
                r"\mathstrut f\text{ is continuous}\}\end{gathered}",
                font_size=32,
                color=OUTPUT,
            ).move_to([-3.25, 0.4, 0]),
            network_text=VGroup(
                caption("Our approximations come from", 2.0, x=3.25, baseline=True),
                caption("a family of networks", 1.6, x=3.25, baseline=True),
            ),
            network_class=MathTex(
                r"\begin{gathered}\mathstrut\mathcal{N}=\{N_\theta:K\to\mathbb{R}\mid\\"
                r"\mathstrut N_\theta\text{ is a finite ReLU network}\}\end{gathered}",
                font_size=32,
                color=AFFINE,
            ).move_to([3.25, 0.4, 0]),
            inclusion=MathTex(r"\mathcal{N}\subseteq C(K)", font_size=32, color=AFFINE),
            question=caption(
                "How do we compare our approximations to our targets?", -1.65, font_size=30
            ),
        )
        classes.inclusion.next_to(classes.network_class, DOWN, buff=0.4)
        # Separate chunks for the f-to-error substitution
        norm_formula = MathTex(
            r"\|", "f", r"\|_\infty", "=", r"\sup_{x\in K}", "|", "f(x)", "|", font_size=56
        ).move_to([0, 0.45, 0])
        norm = named_group(
            heading=slide_header("Uniform Norm"),
            caption=caption("To compare functions, we use the uniform norm.", 1.8),
            formula=norm_formula,
        )

        graph = function_graph(target)
        self.function_graph = graph
        axes, f = graph.axes, graph.f
        approx = lambda x: f(x) + 0.075 * math.sin(9 * x)
        samples = [i / 80 for i in range(81)]
        band = curve_band(axes, f, 0.16, xs=samples, opacity=0.16)
        target_curve = graph.curve
        network_curve = axes.plot(approx, x_range=[0, 1], color=AFFINE, stroke_width=3)
        bounds = VGroup(
            *(
                axes.plot(
                    lambda x, sign=s: f(x) + sign * 0.16,
                    x_range=[0, 1],
                    color=OUTPUT,
                    stroke_width=1,
                    stroke_opacity=0.5,
                )
                for s in [-1, 1]
            )
        )
        target_label = MathTex("f", color=OUTPUT, font_size=30)
        target_label.move_to(axes.c2p(1, f(1)) + [0.5, -0.25, 0])
        network_label = MathTex(r"N_\theta", color=AFFINE, font_size=30)
        network_label.move_to(axes.c2p(1, approx(1)) + [0.6, 0.28, 0])
        labels = VGroup(
            *graph.endpoints,
            VGroup(
                Line(axes.c2p(1, f(1)), target_label.get_left(), color=OUTPUT, stroke_width=1.3),
                target_label,
            ),
            VGroup(
                Line(
                    axes.c2p(1, approx(1)), network_label.get_left(), color=AFFINE, stroke_width=1.3
                ),
                network_label,
            ),
        )
        epsilon_mark = epsilon_brace(
            axes.c2p(0.88, f(0.88) - 0.16), axes.c2p(0.88, f(0.88)), buff=0.06
        )
        epsilon_label = MathTex(r"\varepsilon", font_size=32, color=WHITE)
        epsilon_label.next_to(epsilon_mark, RIGHT, buff=0.12)
        error = named_group(
            formula=MathTex(
                r"\|",
                r"f-N_\theta",
                r"\|_\infty",
                "=",
                r"\sup_{x\in K}",
                "|",
                r"f(x)-N_\theta(x)",
                "|",
                r"<\varepsilon",
                font_size=42,
            ).move_to([0, 1.9, 0]),
            axes=axes,
            band=band,
            bounds=bounds,
            target=target_curve,
            approximation=network_curve,
            labels=labels,
            epsilon=VGroup(epsilon_mark, epsilon_label),
        )
        return SimpleNamespace(
            targets=inputs,
            compact=compact,
            continuity=continuity,
            classes=classes,
            norm=norm,
            error=error,
        )

    def norm_decorations(self, error, centered_error):
        return VGroup(
            centered_error,
            error.band,
            error.bounds,
            error.approximation,
            error.labels[2:],
            error.epsilon,
        )

    def continuity_graph(self, graph, previous):
        shared = graph or function_graph(target)
        f, axes, endpoints, curve = shared.f, shared.axes, shared.endpoints, shared.curve
        title = slide_header("What's the point?")
        if previous is None:
            self.add(title, axes, endpoints)
            self.play(Create(curve), run_time=1.8)
        else:
            old_title, decorations = previous
            self.play(Transform(old_title, title), run_time=0.7)
            self.wait(0.4)
            formula, band, bounds, network, labels, epsilon = decorations

            def rewind_band(mobject, alpha):
                # Erase from the right without closing a partial polygon
                cutoff = max(0.00001, 1 - alpha)
                xs = np.linspace(0, cutoff, 81)
                mobject.become(curve_band(axes, f, 0.16, xs=xs, opacity=0.16))

            self.play(
                Uncreate(epsilon[0]),
                Unwrite(epsilon[1]),
                Unwrite(labels[1][1]),
                Uncreate(labels[1][0]),
                Uncreate(network),
                Unwrite(labels[0][1]),
                Uncreate(labels[0][0]),
                Unwrite(formula),
                UpdateFromAlphaFunc(band, rewind_band),
                *(Uncreate(bound) for bound in bounds),
                run_time=1.3,
            )
            self.remove(decorations, band, bounds, network, formula, labels, epsilon)

        heading = old_title if previous is not None else title

        return SimpleNamespace(f=f, axes=axes, heading=heading)

    def tolerance_window(self, view):
        f = view.f
        axes = view.axes
        eps = ValueTracker(0.24)
        delta = ValueTracker(0.08)
        center = ValueTracker(0.38)

        def window():
            x, e, d = center.get_value(), eps.get_value(), delta.get_value()
            lo, hi = max(0, x - d), min(1, x + d)
            y = f(x)
            box = tolerance_box(axes, x, y, d, e)
            point = Dot(axes.c2p(x, y), radius=0.055, color=OUTPUT)
            nearby_x = min(1, x + 0.9 * d)
            nearby_y = f(nearby_x)
            nearby_point = Dot(axes.c2p(nearby_x, nearby_y), radius=0.06, color=AFFINE)
            baseline = Line(
                axes.c2p(x, y),
                axes.c2p(nearby_x, y),
                color=WHITE,
                stroke_width=1.2,
                stroke_opacity=0.65,
            )
            gap = Line(
                axes.c2p(nearby_x, y), axes.c2p(nearby_x, nearby_y), color=AFFINE, stroke_width=5
            )
            side = 1 if nearby_y >= y else -1
            vertical = epsilon_brace(axes.c2p(hi, y), axes.c2p(hi, y + side * e), buff=0.08)
            elabel = MathTex(r"\varepsilon", font_size=28, color=WHITE)
            elabel.next_to(vertical, RIGHT, buff=0.12)
            horizontal = DoubleArrow(
                axes.c2p(x, 0) + [0, -0.32, 0],
                axes.c2p(hi, 0) + [0, -0.32, 0],
                buff=0,
                tip_length=0.06,
                color=NONLINEARITY,
                stroke_width=2,
            )
            dlabel = MathTex(r"\delta", font_size=27, color=NONLINEARITY)
            dlabel.move_to(horizontal.get_center() + [0, -0.2, 0])
            guides = VGroup()
            for a in [x, hi]:
                start, end = axes.c2p(a, 0), axes.c2p(a, y - e)
                for j in range(10):
                    guides.add(
                        Line(
                            start + (end - start) * j / 10,
                            start + (end - start) * (j + 0.55) / 10,
                            color=NONLINEARITY,
                            stroke_width=1,
                            stroke_opacity=0.5,
                        )
                    )
            return VGroup(
                box,
                guides,
                baseline,
                point,
                nearby_point,
                gap,
                vertical,
                elabel,
                horizontal,
                dlabel,
            )

        moving = always_redraw(window)
        note = bottom_caption(
            r"Points less than $\delta$ apart have function values differing by less than $\varepsilon$."
        )
        comparison = MathTex(
            r"|y-x|<\delta", r"\quad\Longrightarrow\quad", r"|f(y)-f(x)|<\varepsilon", font_size=32
        )
        comparison[0].set_color(NONLINEARITY)
        comparison[2].set_color(AFFINE)
        comparison.move_to([0, 2.15, 0])
        self.play(Write(comparison), run_time=1.4)
        initial_window = window()
        self.play(Create(initial_window[0]), run_time=0.7)
        self.play(*(FadeIn(part) for part in initial_window[1:]), run_time=0.35)
        # Attach the updater after drawing so it cannot overwrite the reveal
        self.remove(*initial_window)
        self.add(moving)
        self.play(FadeIn(note), run_time=0.5)

        view.center = center
        view.moving = moving
        view.note = note
        view.comparison = comparison

    def sweep_window(self, view):
        center = view.center
        self.play(center.animate.set_value(0.9), run_time=4)
        self.play(center.animate.set_value(0.5), run_time=2)

    def partition(self, view):
        axes = view.axes
        f = view.f
        moving = view.moving
        comparison = view.comparison
        note = view.note

        def grid(n):
            return vertical_grid(axes, (i / n for i in range(n + 1)), 1.45)

        def error_region(n):
            regions = VGroup()
            whiskers = VGroup()
            for i in range(n):
                lo, hi = i / n, (i + 1) / n
                height = f((i + 0.5) / n)
                xs = np.linspace(lo, hi, 12)
                regions.add(
                    Polygon(
                        *[axes.c2p(x, f(x)) for x in xs],
                        axes.c2p(hi, height),
                        axes.c2p(lo, height),
                        stroke_width=0,
                        fill_color=WHITE,
                        fill_opacity=0.3,
                    )
                )
                for t in [0.18, 0.82]:
                    x = lo + t * (hi - lo)
                    whiskers.add(
                        Line(axes.c2p(x, height), axes.c2p(x, f(x)), color=WHITE, stroke_width=1.5)
                    )
            return VGroup(regions, whiskers)

        def steps(n):
            return VGroup(
                *(
                    Line(
                        axes.c2p(i / n, f((i + 0.5) / n)),
                        axes.c2p((i + 1) / n, f((i + 0.5) / n)),
                        color=AFFINE,
                        stroke_width=4,
                    )
                    for i in range(n)
                )
            )

        def band(e):
            return curve_band(axes, f, e).set_z_index(-1)

        coarse = grid(16)
        staircase = steps(16)
        envelope = band(0.24)
        new_note = bottom_caption(
            r"Partition $[0,1]$ into finitely many intervals, each with diameter $<\delta$."
        )
        self.play(
            FadeOut(moving),
            FadeOut(comparison),
            Transform(note, new_note),
            Create(coarse),
            run_time=1.3,
        )

        view.grid = grid
        view.error_region = error_region
        view.steps = steps
        view.band = band
        view.coarse = coarse
        view.staircase = staircase
        view.envelope = envelope

    def representative(self, view):
        axes = view.axes
        f = view.f
        note = view.note
        staircase = view.staircase
        sample = Dot(axes.c2p(8.5 / 16, f(8.5 / 16)), color=AFFINE, radius=0.055)
        self.play(
            FadeIn(sample),
            Transform(
                note, bottom_caption("Use the value at a representative point in the interval.")
            ),
            run_time=0.4,
        )
        self.play(Create(staircase[8]), run_time=0.8)

        view.sample = sample

    def staircase(self, view):
        error_region = view.error_region
        sample = view.sample
        envelope = view.envelope
        staircase = view.staircase
        note = view.note
        errors = error_region(16)
        self.play(
            FadeOut(sample),
            FadeIn(envelope),
            FadeIn(errors),
            *(Create(staircase[i]) for i in range(16) if i != 8),
            Transform(
                note,
                bottom_caption(
                    r"Within each interval, the function differs from its sampled value by less than $\varepsilon$."
                ),
            ),
            run_time=1.6,
        )
        self.remove(*staircase)
        self.add(staircase)

        view.errors = errors

    def refine(self, view):
        errors = view.errors
        error_region = view.error_region
        coarse = view.coarse
        grid = view.grid
        staircase = view.staircase
        steps = view.steps
        envelope = view.envelope
        band = view.band
        note = view.note
        self.play(
            Transform(errors, error_region(32)),
            Transform(coarse, grid(32)),
            Transform(staircase, steps(32)),
            Transform(envelope, band(0.12)),
            Transform(note, bottom_caption(r"This gives us a piecewise-constant approximation.")),
            run_time=2.3,
        )

    def proof_views(self):
        def page(**parts):
            return named_group(heading=slide_header("One-dimensional approximation"), **parts)

        continuity = page(
            setting=proof_text(r"Let $f:[0,1]\to\mathbb{R}$ be continuous.", y=2.15),
            proof=proof_text(
                r"\textit{Proof.} Fix arbitrary $\varepsilon>0$. "
                r"By uniform continuity, choose $\delta>0$ such that",
                y=1.25,
            ),
            bound=proof_equation(
                r"|x-y|<\delta\quad\Longrightarrow\quad" r"|f(x)-f(y)|<\frac{\varepsilon}{2}",
                y=-0.35,
            ),
        )
        grid = page(
            choice=proof_text(
                r"By the Archimedean property, we choose $n\in\mathbb{N}$ with $1/n<\delta$.",
                y=2.15,
            ),
            intro=proof_text("Consider the evenly spaced grid", y=1.4),
            coordinates=proof_equation(r"t_i=\frac{i}{n},\qquad i=0,\ldots,n.", y=0.55),
        )
        interpolant = page(
            choose=proof_text(
                r"Take any $i\in\{0,\ldots,n-1\}$ and $x\in[t_i,t_{i+1}]$, and let", y=2.15
            ),
            fraction=proof_equation(r"\lambda=\frac{x-t_i}{t_{i+1}-t_i}\in[0,1].", y=1.25),
            intro=proof_text("Then, define the linear interpolant", y=0.65),
            formula=proof_equation(r"p(x)=(1-\lambda)f(t_i)+\lambda f(t_{i+1}).", y=0.05),
        )
        endpoints = page(
            intro=proof_text("We have", y=2.15),
            distances=proof_equation(r"|x-t_i|<\delta,\qquad |x-t_{i+1}|<\delta,", y=1.05),
            so=proof_text("so", y=-0.05),
            errors=proof_equation(
                r"|f(x)-f(t_i)|<\frac{\varepsilon}{2},\qquad"
                r"|f(x)-f(t_{i+1})|<\frac{\varepsilon}{2}.",
                y=-1.3,
                font_size=38,
            ),
        )
        estimate = page(
            intro=proof_text("Thus we have", y=2.15),
            equality=proof_equation(
                *[
                    r"|f(x)-p(x)|",
                    "=",
                    r"\bigl|",
                    r"(1-\lambda)(",
                    r"f(x)-f(t_i)",
                    ")",
                    "+",
                    r"\lambda(",
                    r"f(x)-f(t_{i+1})",
                    ")",
                    r"\bigr|",
                ],
                y=1.05,
                font_size=34,
            ),
            triangle=proof_equation(
                *[
                    r"\leq",
                    r"(1-\lambda)",
                    "|",
                    r"f(x)-f(t_i)",
                    "|",
                    "+",
                    r"\lambda",
                    "|",
                    r"f(x)-f(t_{i+1})",
                    "|",
                ],
                y=-0.05,
                font_size=36,
            ),
            bound=proof_equation(
                *[
                    r"\leq",
                    r"(1-\lambda)",
                    r"\frac{\varepsilon}{2}",
                    "+",
                    r"\lambda",
                    r"\frac{\varepsilon}{2}",
                ],
                y=-1.2,
                font_size=38,
            ),
            simplified=proof_equation(r"=\frac{\varepsilon}{2}.", y=-2.35, font_size=40),
        )
        sign_x = estimate.equality[1].get_left()[0]
        for row in (estimate.triangle, estimate.bound, estimate.simplified):
            row.set_x(sign_x, direction=[-1, 0, 0])
        conclusion = page(
            statement=proof_text(
                r"This holds throughout every interval $[t_i,t_{i+1}]$, "
                r"so $p$ is continuous and piecewise-linear, with",
                y=2.15,
            ),
            bound=proof_equation(
                r"\|f-p\|_\infty\leq\frac{\varepsilon}{2}" r"<\varepsilon.\qquad\square",
                y=0.35,
                font_size=48,
            ),
        )
        return SimpleNamespace(
            continuity=continuity,
            grid=grid,
            interpolant=interpolant,
            endpoints=endpoints,
            estimate=estimate,
            conclusion=conclusion,
        )

    def proof_grid(self, grid_text, interpolation_text, endpoint_text):
        axes = plot_axes(
            x_range=[0, 1, 0.125],
            y_range=[0, 1.5, 0.5],
            x_length=10,
            y_length=2.2,
            center=[0, -1.6, 0],
        )
        curve = axes.plot(target, x_range=[0, 1, 0.005], color=OUTPUT, stroke_width=3)
        n, i = 8, 3
        left, right = i / n, (i + 1) / n
        guides = vertical_grid(axes, (k / n for k in range(n + 1)), 1.3, stroke_opacity=0.45)
        labels = VGroup(
            MathTex(r"t_0=0", font_size=24).move_to(axes.c2p(0, 0) + [0, -0.3, 0]),
            MathTex(r"t_n=1", font_size=24).move_to(axes.c2p(1, 0) + [0, -0.3, 0]),
        )
        self.add(grid_text.root, axes, labels, curve)
        f_label = MathTex("f", font_size=27, color=OUTPUT).move_to(
            axes.c2p(1, target(1)) + [0.3, 0, 0]
        )
        self.add(f_label)
        self.gate()
        self.play(Create(guides), run_time=1.2)
        self.gate()

        self.remove(grid_text.root)
        self.add(interpolation_text.heading, interpolation_text.choose, interpolation_text.fraction)
        interval = Line(axes.c2p(left, 0), axes.c2p(right, 0), color=NEURON, stroke_width=5)
        ends = VGroup(
            *(
                MathTex(tex, font_size=26).move_to(axes.c2p(x, 0) + [0, -0.3, 0])
                for x, tex in [(left, r"t_i"), (right, r"t_{i+1}")]
            )
        )
        fraction = ValueTracker(0.65)

        def x_marker():
            x = left + fraction.get_value() * (right - left)
            dot = Dot(axes.c2p(x, 0), radius=0.045, color=AFFINE)
            label = MathTex("x", font_size=25, color=AFFINE).move_to(axes.c2p(x, 0) + [0, 0.28, 0])
            return VGroup(dot, label)

        marker = always_redraw(x_marker)
        self.play(Create(interval), FadeIn(ends), run_time=0.6)
        self.play(FadeIn(marker), run_time=0.35)
        self.gate()

        self.remove(
            interpolation_text.heading, interpolation_text.choose, interpolation_text.fraction
        )
        interpolation_text.intro.move_to([-5.8, 2.15, 0], aligned_edge=[-1, 1, 0])
        interpolation_text.formula.move_to([-5.2, 1.25, 0], aligned_edge=[-1, 0, 0])
        self.add(interpolation_text.heading, interpolation_text.intro, interpolation_text.formula)
        samples = VGroup(
            *(Dot(axes.c2p(x, target(x)), radius=0.055, color=OUTPUT) for x in [left, right])
        )
        chord = Line(
            axes.c2p(left, target(left)),
            axes.c2p(right, target(right)),
            color=AFFINE,
            stroke_width=4,
        )
        self.play(FadeIn(samples), run_time=0.4)
        self.play(Create(chord), run_time=1)

        def p_marker():
            lam = fraction.get_value()
            x = left + lam * (right - left)
            value = (1 - lam) * target(left) + lam * target(right)
            point = axes.c2p(x, value)
            return VGroup(
                DashedLine(axes.c2p(x, 0), point, color=AFFINE, stroke_width=1.5),
                Dot(point, radius=0.05, color=AFFINE),
                MathTex("p(x)", font_size=24, color=AFFINE).move_to(point + [0.6, -0.48, 0]),
            )

        marker.clear_updaters()
        x_label = marker[1]
        self.remove(marker)
        self.add(x_label)
        x = left + fraction.get_value() * (right - left)
        baseline_dot = Dot(axes.c2p(x, 0), radius=0.045, color=AFFINE)
        self.add(baseline_dot)
        value_marker = p_marker()
        self.play(
            ReplacementTransform(x_label, value_marker[2]),
            Create(value_marker[0]),
            FadeIn(value_marker[1]),
            run_time=0.75,
        )
        self.add(value_marker)
        self.gate()

        self.remove(*interpolation_text.root)
        endpoint_text.distances.move_to([-5.2, 1.45, 0], aligned_edge=[-1, 0, 0])
        self.add(endpoint_text.heading, endpoint_text.intro, endpoint_text.distances)
        chord.set_opacity(0.2)
        guides.set_opacity(0.2)
        plot = VGroup(
            axes, curve, guides, labels, interval, ends, samples, chord, f_label, baseline_dot
        )
        self.add(plot)
        self.play(FadeOut(value_marker), run_time=0.35)
        self.play(plot.animate.scale(1.25).shift([0, 0.45, 0]), run_time=0.85)
        brace = BraceBetweenPoints(
            axes.c2p(left, 0) + [0, -0.4, 0], axes.c2p(right, 0) + [0, -0.4, 0], direction=DOWN
        )
        bound_label = MathTex(r"<\delta", font_size=26)
        bound_label.next_to(brace, DOWN, buff=0.08)
        self.play(FadeIn(brace), FadeIn(bound_label), run_time=0.45)
        self.gate()

        # (0.3 + 0.8*pi)*0.14 < 0.4 bounds the endpoint differences
        self.remove(endpoint_text.intro, endpoint_text.distances)
        endpoint_text.so.move_to([-5.8, 2.15, 0], aligned_edge=[-1, 1, 0])
        endpoint_text.errors.move_to([-5.2, 1.25, 0], aligned_edge=[-1, 0, 0])
        self.add(endpoint_text.so, endpoint_text.errors)
        base = axes.c2p(x, target(x))
        box = tolerance_box(axes, x, target(x), 0.14, 0.4, x_bounds=(left, right))
        actual = Dot(base, radius=0.06, color=NEURON)
        differences = VGroup(
            *(
                Line(base, axes.c2p(x, target(t)), color=NEURON, stroke_width=4)
                for t in [left, right]
            )
        )
        allowance = epsilon_brace(axes.c2p(right, target(x)), axes.c2p(right, target(x) + 0.4))
        epsilon_label = MathTex(r"\varepsilon/2", font_size=26)
        epsilon_label.next_to(allowance, RIGHT, buff=0.12)
        self.play(Create(box), run_time=0.7)
        self.play(
            FadeIn(actual),
            FadeIn(differences),
            FadeIn(allowance),
            FadeIn(epsilon_label),
            run_time=0.35,
        )
        self.gate()


def target(x):
    return 0.65 + 0.4 * math.sin(2 * math.pi * x) + 0.3 * x
