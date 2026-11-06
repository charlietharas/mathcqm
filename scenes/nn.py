from types import SimpleNamespace

import numpy as np
from manim import (
    BLACK,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    WHITE,
    Arrow,
    Axes,
    Brace,
    Circle,
    Create,
    FadeIn,
    FadeOut,
    MathTex,
    ReplacementTransform,
    SurroundingRectangle,
    Tex,
    TransformMatchingTex,
    VGroup,
    Write,
    config,
)
from scenes._settings import Slide
from _helpers import (
    NEURON,
    NONLINEARITY,
    AFFINE,
    OUTPUT,
    MUTED,
    EDGE,
    fit,
    network,
    network_labels,
    strip_network_labels,
    slide_header,
    data_color,
    send_data,
    data_wave,
    flow_during_text,
)


class NeuralNetworkSlide(Slide):
    def construct(self):
        # Configure looping level
        self.next_slide(auto_next=self.loopingLevel in (1.5, 2))
        # Network and parameters
        view = self.introduction()
        # One neuron
        view = self.one_neuron(view)
        # Why nonlinearities?
        view = self.why_nonlinearities(view)
        # ReLU and other activations
        view = self.activation_examples(view)
        # Weighted outputs
        view = self.weighted_outputs(view)
        # Layered network
        view = self.depth(view)
        # Back to a shallow network
        self.back_to_shallow(view)

    # Network diagram and parameters
    def introduction(self):
        view = opening_view()
        diagram = view.diagram
        title = slide_header("But what is a neural network?")
        self.add(title)
        self.play(
            Create(diagram["edges"]),
            FadeIn(diagram["nodes"]),
            FadeIn(diagram["coordinates"]),
            FadeIn(diagram["neuron_labels"]),
            FadeIn(diagram["omissions"]),
            FadeIn(diagram["labels"]),
            run_time=1.4,
        )
        self.play(Create(diagram["entry"]), Write(diagram["input_symbol"]), run_time=0.5, pace=1)
        send_data(self, diagram["connections"][0], AFFINE)
        send_data(self, diagram["connections"][1], data_color(1))
        self.play(Create(diagram["exit"]), Write(diagram["output_symbol"]), run_time=0.6, pace=1)
        self.play(Write(view.input_output), FadeIn(view.parameters_note), run_time=0.8, pace=1)
        self.flow_break(diagram, title, view.input_output, view.parameters_note)
        # Morph the heading with the neuron zoom
        view.root.remove(view.caption)
        view.caption = title
        view.root.add(title)
        self.add(view.root)
        return view

    # One neuron
    def one_neuron(self, start):
        # Keep the reveal and zoom in one clip to avoid a restart
        end = neuron_view()
        self.play(
            FadeOut(network_labels(start.diagram)),
            FadeOut(start.input_output),
            FadeOut(start.parameters_note),
            run_time=0.25,
        )
        strip_network_labels(start.diagram)
        self.play(FadeOut(start.diagram["ports"]), run_time=0.2)
        start.diagram["group"].remove(start.diagram["ports"])
        self.play(
            ReplacementTransform(start.caption, end.caption),
            ReplacementTransform(start.diagram["group"], end.diagram["group"]),
            run_time=0.9,
        )
        start.diagram = end.diagram
        start.caption = end.caption
        self.play(Create(end.ring), run_time=0.45)
        end.neuron[1].set_color(WHITE)
        end.neuron[3].set_color(WHITE)
        with flow_during_text(self, start.diagram, neuron_index=1):
            self.play(Create(end.pointer), Write(end.neuron), run_time=1, pace=1)
            self.play(
                end.neuron[1].animate.set_color(NONLINEARITY),
                FadeIn(end.sigma_label),
                Create(end.sigma_pointer),
                run_time=0.6,
            )
            self.play(
                end.neuron[3].animate.set_color(AFFINE),
                FadeIn(end.affine_brace),
                FadeIn(end.affine_label),
                FadeIn(end.parameters),
                run_time=0.7,
            )
            self.play(Write(end.dot_product), run_time=0.85, pace=1)
            self.play(Write(end.expanded), run_time=0.65, pace=1)
        end.diagram, end.caption = start.diagram, start.caption
        end.root = VGroup(end.diagram["group"], end.caption, end.ring, end.callout)
        return self.hold(end, flow=True, neuron_index=1)

    # Why nonlinearities?
    def why_nonlinearities(self, start):
        end = collapse_view()
        self.remove(start.root)
        self.add(end.root)
        self.hold(end)

        nonlinear_caption = Tex(
            "Compositions of nonlinear maps do not (in general) collapse", font_size=32
        )
        fit(nonlinear_caption, 12).move_to(end.caption)
        nonlinear = MathTex(
            r"A_2(",
            r"\sigma(",
            r"A_1(x)",
            "))",
            "=",
            r"W_2",
            r"\sigma",
            "(",
            r"W_1x+b_1",
            ")",
            "+",
            "b_2",
            font_size=36,
        ).move_to(end.composition)
        nonlinear[1].set_color(NONLINEARITY)
        nonlinear[6].set_color(NONLINEARITY)
        not_affine = MathTex(
            r"\overset{\text{in general}}{\ne}", r"(W_2W_1)x", "+", r"(W_2b_1+b_2)", font_size=36
        ).move_to(end.collapsed)
        not_affine[1].set_color(AFFINE)
        not_affine[3].set_color(OUTPUT)
        self.play(
            ReplacementTransform(end.caption, nonlinear_caption),
            TransformMatchingTex(end.composition, nonlinear),
            TransformMatchingTex(end.collapsed, not_affine),
            run_time=0.75,
        )
        # Drop the parent that still holds the old equations
        self.remove(end.root)
        end.panel = VGroup(nonlinear_caption, nonlinear, not_affine)
        end.root = VGroup(end.title, end.panel)
        return self.hold(end)

    # Activation examples
    def activation_examples(self, start):
        end = relu_view()
        end.title = start.title
        # Remove old glyphs before adding ReLU
        self.play(FadeOut(start.panel), run_time=0.45)
        self.play(FadeIn(end.subtitle), Write(end.formula), run_time=0.8)
        self.play(FadeIn(end.axes), FadeIn(end.labels), run_time=0.6)
        self.play(Create(end.graph), run_time=1.3)
        end.root = VGroup(end.title, end.panel)
        self.hold(end)

        original_relu = end.panel.copy()
        gallery = activation_gallery()
        self.play(end.panel.animate.scale(0.66).move_to([-3.4, 0, 0]), run_time=0.65)
        self.play(FadeIn(gallery), run_time=0.4)
        relu_panel = end.panel
        end.root = VGroup(end.title, relu_panel, gallery)
        self.hold(end)

        self.play(FadeOut(gallery), run_time=0.4)
        self.play(relu_panel.animate.become(original_relu), run_time=0.65)
        end.panel = relu_panel
        end.root = VGroup(end.title, end.panel)
        return self.hold(end)

    # Weighted outputs
    def weighted_outputs(self, start):
        self.next_slide(auto_next=self.loopingLevel == 2)
        end = shallow_view()
        # Leave space between the diagram and equations
        end.diagram["group"].scale(0.9)
        VGroup(end.panel, end.neuron_box).scale(0.94).shift(DOWN * 0.12)
        self.remove(start.root, start.panel, start.title)
        self.add(end.caption, end.diagram["group"])
        with flow_during_text(self, end.diagram):
            self.play(Write(end.formula), run_time=1.2)
            self.play(FadeIn(end.neuron_box), run_time=0.2)
            self.play(Write(end.weighted), run_time=0.9)
            self.play(FadeOut(end.neuron_box), FadeIn(end.output_annotation), run_time=0.4)
        return self.hold(end, flow=True)

    # Layered network
    def depth(self, start):
        self.next_slide(auto_next=self.loopingLevel == 2)
        end = layered_view()
        # Insert “layered” into the existing heading
        self.play(
            *[
                word.animate.match_height(target).move_to(target).set_color(target.get_color())
                for word, target in zip(start.caption, end.caption)
            ],
            FadeIn(end.layered_word),
            run_time=0.45,
        )
        end.caption = start.caption
        end.title = VGroup(end.caption, end.layered_word)
        self.play(
            FadeOut(start.panel),
            ReplacementTransform(start.diagram["group"], end.diagram["group"]),
            run_time=0.9,
        )
        with flow_during_text(self, end.diagram):
            self.play(Write(end.composition), run_time=1.1)
            self.play(Write(end.matrix_map), FadeIn(end.matrix_note), run_time=1.2)
            self.play(FadeIn(end.activation_note), Write(end.activation_example), run_time=0.8)
        end.root = VGroup(end.title, end.diagram["group"], end.panel)
        return self.hold(end, flow=True)

    # Back to shallow
    def back_to_shallow(self, start):
        # Final view has no data flow
        end = return_view()
        self.play(FadeOut(start.title), FadeIn(end.title), run_time=0.6)
        self.play(
            FadeOut(start.panel),
            ReplacementTransform(start.diagram["group"], end.diagram["group"]),
            run_time=0.9,
        )
        self.play(FadeIn(end.panel), run_time=0.7)
        self.hold(end)
        return end

    def play(self, *animations, **kwargs):
        # Slow major equations only
        pace = kwargs.pop("pace", None)
        if pace is None:
            pace = 1.8 if any(isinstance(a, Write) for a in animations) else 1.0
        # Preserve Wait durations so active data waves can finish
        if "run_time" in kwargs or pace != 1:
            kwargs["run_time"] = kwargs.get("run_time", 1) * pace
        return super().play(*animations, **kwargs)

    def hold(self, view, *, flow=False, neuron_index=None, opening=False):
        self.add(view.root)
        self.wait(0.05)
        repeat = self.loopingLevel == 2 or (opening and self.loopingLevel == 1.5)
        if flow and self.loopingLevel and repeat:
            if repeat:
                self.next_slide(loop=True, notes="opening-loop" if opening else "")
            data_wave(self, view.diagram, neuron_index=neuron_index)
            self.wait(0.2)
        self.next_slide()
        return view

    def flow_break(self, diagram, *visible):
        # Hold only the currently revealed objects
        frame = SimpleNamespace(diagram=diagram, root=VGroup(diagram["group"], *visible))
        self.hold(frame, flow=True, opening=True)
        self.next_slide(auto_next=self.loopingLevel == 2)


def heading():
    return slide_header("A neural network is a ", r"\textbf{network}", " of ", r"\textbf{neurons}")


def shallow_formulas():
    formula = MathTex(
        r"N_\theta(x)",
        "=",
        "c",
        "+",
        r"\sum_{j=1}^{m}",
        r"a_j\;",
        r"\sigma(w_j^\top x+b_j)",
        font_size=34,
    )
    fit(formula, 11.5).move_to([0, -1.15, 0])
    formula[2].set_color(OUTPUT)
    formula[5].set_color(OUTPUT)
    formula[6].set_color(NEURON)
    neuron_box = SurroundingRectangle(formula[6], color=NEURON, buff=0.04, stroke_width=2)

    weighted = MathTex("=", "c", "+", r"\sum_{j=1}^{m}", r"a_j", r"h_j(x)", font_size=34)
    # Align the equals signs
    weighted.scale(formula[1].height / weighted[0].height)
    weighted.move_to([0, -2.35, 0])
    weighted.shift(RIGHT * (formula[1].get_x() - weighted[0].get_x()))
    weighted[1].set_color(OUTPUT)
    weighted[4].set_color(OUTPUT)
    weighted[5].set_color(NEURON)
    affine_brace = Brace(VGroup(*weighted[1:]), DOWN, color=OUTPUT, buff=0.18)
    affine_label = Tex(r"affine in $h_1(x),\ldots,h_m(x)$", font_size=24, color=OUTPUT).next_to(
        affine_brace, DOWN, buff=0.15
    )
    return formula, neuron_box, weighted, VGroup(affine_brace, affine_label)


def opening_view():
    diagram = network()
    caption = heading()
    input_output = MathTex("x", r"\longmapsto", r"N_\theta(x)", "=", "y", font_size=36).move_to(
        [0, -2, 0]
    )
    input_output[0].set_color(AFFINE)
    input_output[-1].set_color(OUTPUT)
    parameters_note = Tex(r"($\theta$ parametrizes the network)", font_size=29)
    parameters_note.move_to([0, -2.7, 0])
    return SimpleNamespace(
        diagram=diagram,
        caption=caption,
        input_output=input_output,
        parameters_note=parameters_note,
        root=VGroup(diagram["group"], input_output, parameters_note, caption),
    )


def small_network():
    diagram = network(compact=True)
    strip_network_labels(diagram)
    diagram["group"].remove(diagram["ports"])
    diagram["group"].scale(1.05).move_to([-3.7, 0.45, 0])
    # Ellipsis replaces the omitted neuron and its edges
    hidden = diagram["layers"][1]
    hidden[-1].set_opacity(0)
    for index, edge in enumerate(diagram["connections"][0]):
        if index % len(hidden) == len(hidden) - 1:
            edge.set_opacity(0)
    diagram["connections"][1][-1].set_opacity(0)
    return diagram


def selected_neuron(diagram):
    selected = diagram["layers"][1][1]
    incoming = VGroup(*[diagram["connections"][0][i * 4 + 1] for i in range(3)])
    return selected, incoming


def neuron_view():
    diagram = small_network()
    selected, incoming = selected_neuron(diagram)
    selected.set_stroke(NEURON, width=3).set_fill(NEURON, opacity=0.4)
    incoming.set_stroke(AFFINE, width=2.5, opacity=1)
    caption = heading()
    caption[3].set_color(NEURON)
    ring = Circle(radius=selected.width / 2 + 0.11, color=NEURON, stroke_width=3)
    ring.move_to(selected).set_z_index(4)
    neuron = MathTex(r"x\longmapsto", r"\sigma", r"\bigl(", r"w^\top x+b", r"\bigr)", font_size=42)
    fit(neuron, 5.9).move_to([2.7, 1.3, 0])
    neuron[1].set_color(NONLINEARITY)
    neuron[3].set_color(AFFINE)
    pointer_end = neuron.get_left() + LEFT * 0.18
    direction = pointer_end - ring.get_center()
    direction /= np.linalg.norm(direction)
    pointer = Arrow(
        ring.get_center() + direction * ring.width / 2,
        pointer_end,
        color=NEURON,
        buff=0,
        stroke_width=2.5,
    ).set_z_index(4)
    sigma_label = Tex("nonlinearity", font_size=25, color=NONLINEARITY)
    sigma_label.next_to(neuron[1], UP, buff=0.5)
    sigma_pointer = Arrow(
        sigma_label.get_bottom(),
        neuron[1].get_top(),
        buff=0.08,
        color=NONLINEARITY,
        stroke_width=2,
        max_tip_length_to_length_ratio=0.18,
    )
    affine_brace = Brace(neuron[3], DOWN, color=AFFINE, buff=0.18)
    affine_label = Tex("affine function", font_size=25, color=AFFINE)
    affine_label.next_to(affine_brace, DOWN, buff=0.16)
    parameters = MathTex(
        r"w\in\mathbb{R}^d,\qquad b\in\mathbb{R}", font_size=24, color=MUTED
    ).next_to(affine_label, DOWN, buff=0.16)
    dot_product = MathTex(
        r"w^\top x+b",
        "=",
        r"\begin{bmatrix}w_1&\cdots&w_d\end{bmatrix}",
        r"\begin{bmatrix}x_1\\\vdots\\x_d\end{bmatrix}",
        "+",
        "b",
        font_size=34,
    )
    fit(dot_product, 10.5).move_to([0, -1.85, 0])
    dot_product[0].set_color(AFFINE)
    dot_product[2].set_color(AFFINE)
    dot_product[-1].set_color(OUTPUT)
    expanded = MathTex("=", r"w_1x_1", "+", r"\cdots", "+", r"w_dx_d", "+", "b", font_size=34)
    fit(expanded, 10.5).move_to([0, -3, 0])
    expanded.shift(RIGHT * (dot_product[1].get_x() - expanded[0].get_x()))
    expanded[1].set_color(AFFINE)
    expanded[5].set_color(AFFINE)
    expanded[-1].set_color(OUTPUT)
    callout = VGroup(
        neuron,
        pointer,
        sigma_label,
        sigma_pointer,
        affine_brace,
        affine_label,
        parameters,
        dot_product,
        expanded,
    )
    return SimpleNamespace(
        diagram=diagram,
        caption=caption,
        ring=ring,
        neuron=neuron,
        pointer=pointer,
        sigma_label=sigma_label,
        sigma_pointer=sigma_pointer,
        affine_brace=affine_brace,
        affine_label=affine_label,
        parameters=parameters,
        dot_product=dot_product,
        expanded=expanded,
        callout=callout,
        root=VGroup(diagram["group"], caption, ring, callout),
    )


def shallow_view():
    diagram = network()
    diagram["group"].scale(0.85).move_to([0, 1, 0])
    selected, incoming = selected_neuron(diagram)
    selected.set_stroke(NEURON, width=2.5).set_fill(BLACK, opacity=1)
    incoming.set_stroke(EDGE, width=1.5, opacity=0.65)
    diagram["connections"][-1].set_stroke(OUTPUT, width=2, opacity=1)
    diagram["layers"][-1].set_stroke(OUTPUT)
    caption = heading()
    caption[1].set_color(OUTPUT)
    caption[3].set_color(NEURON)
    formula, neuron_box, weighted, output_annotation = shallow_formulas()
    # Keep the temporary highlight outside the panel
    panel = VGroup(formula, weighted, output_annotation)
    return SimpleNamespace(
        diagram=diagram,
        caption=caption,
        formula=formula,
        neuron_box=neuron_box,
        weighted=weighted,
        output_annotation=output_annotation,
        panel=panel,
        root=VGroup(diagram["group"], caption, panel),
    )


def layered_heading():
    caption = heading()
    caption[1].set_color(OUTPUT)
    caption[3].set_color(WHITE)
    targets = slide_header(
        "A neural network is a ",
        r"\textbf{layered} ",
        r"\textbf{network}",
        " of ",
        r"\textbf{neurons}",
    )
    word = targets[1].copy().set_color(NEURON)
    for part, target in zip(caption, [targets[0], targets[2], targets[3], targets[4]]):
        part.match_height(target).move_to(target)
    return caption, word, VGroup(caption, word)


def layered_view():
    caption, word, title = layered_heading()
    diagram = network(hidden_layers=3)
    diagram["group"].scale(0.9).shift(UP * 0.2)
    template = config.tex_template.copy()
    template.add_to_preamble(r"\usepackage{xcolor}")
    sigma = rf"\textcolor[HTML]{{{NONLINEARITY.lstrip('#')}}}{{\sigma}}"

    def layer(index):
        affine = rf"\textcolor[HTML]{{{AFFINE.lstrip('#')}}}{{A_{index}}}"
        return rf"\underbrace{{{sigma}\circ {affine}}}_{{\text{{layer {index}}}}}"

    composition = MathTex(
        r"N_\theta =",
        r"A_4",
        r"\circ",
        layer(3),
        r"\circ",
        layer(2),
        r"\circ",
        layer(1),
        font_size=32,
        tex_template=template,
    )
    fit(composition, 12.3).move_to([0, -1.35, 0])
    composition[1].set_color(OUTPUT)
    matrix_map = MathTex(
        r"A_k(z)=W_kz+b_k",
        "=",
        r"\begin{bmatrix}w_{11}&\cdots&w_{1q}\\\vdots&\ddots&\vdots\\w_{p1}&\cdots&w_{pq}\end{bmatrix}",
        r"\begin{bmatrix}z_1\\\vdots\\z_q\end{bmatrix}",
        "+",
        r"\begin{bmatrix}b_1\\\vdots\\b_p\end{bmatrix}",
        font_size=27,
    )
    fit(matrix_map, 8.5).move_to([-1.9, -2.75, 0])
    matrix_map.set_color(AFFINE)
    matrix_note = Tex(
        r"$q$ inputs $\longrightarrow$ $p$ outputs", font_size=22, color=MUTED
    ).next_to(matrix_map[2], DOWN, buff=0.13)
    activation_note = Tex(r"$\sigma$ is element-wise", font_size=27, color=NONLINEARITY).move_to(
        [4.45, -2.45, 0]
    )
    activation_example = MathTex(
        r"(u_1,\ldots,u_p)\mapsto",
        r"(\sigma(u_1),\ldots,\sigma(u_p))",
        font_size=23,
        color=NONLINEARITY,
    )
    fit(activation_example, 4).next_to(activation_note, DOWN, buff=0.22)
    panel = VGroup(composition, matrix_map, matrix_note, activation_note, activation_example)
    return SimpleNamespace(
        caption=caption,
        layered_word=word,
        title=title,
        diagram=diagram,
        composition=composition,
        matrix_map=matrix_map,
        matrix_note=matrix_note,
        activation_note=activation_note,
        activation_example=activation_example,
        panel=panel,
        root=VGroup(title, diagram["group"], panel),
    )


def why_title():
    return slide_header("Why nonlinearities?")


def collapse_view():
    title = why_title()
    caption = Tex("Compositions of affine maps are affine.", font_size=34)
    caption.move_to([0, 1.8, 0])
    composition = MathTex(
        r"A_2(", r"A_1(x)", ")", "=", r"W_2", "(", r"W_1x+b_1", ")", "+", "b_2", font_size=36
    ).move_to([0, 0.65, 0])
    collapsed = MathTex("=", r"(W_2W_1)x", "+", r"(W_2b_1+b_2)", font_size=36).move_to([0, -0.5, 0])
    collapsed[1].set_color(AFFINE)
    collapsed[3].set_color(OUTPUT)
    panel = VGroup(caption, composition, collapsed)
    return SimpleNamespace(
        title=title,
        caption=caption,
        composition=composition,
        collapsed=collapsed,
        panel=panel,
        root=VGroup(title, panel),
    )


def relu_view():
    title = why_title()
    subtitle = Tex("ReLU", font_size=30, color=NEURON).move_to([0, 2.35, 0])
    formula = MathTex(r"\sigma(t)=\max\{0,t\}", font_size=37).move_to([0, 1.65, 0])
    axes = Axes(
        x_range=[-3, 3, 1],
        y_range=[-1, 3, 1],
        x_length=7,
        y_length=3,
        tips=False,
        axis_config={"include_numbers": True, "font_size": 23},
    ).shift(DOWN * 0.9)
    labels = axes.get_axis_labels(MathTex("t"), MathTex(r"\sigma(t)"))
    graph = axes.plot_line_graph(
        x_values=[-3, 0, 3],
        y_values=[0, 0, 3],
        line_color=NEURON,
        add_vertex_dots=False,
        stroke_width=5,
    )
    panel = VGroup(subtitle, formula, axes, labels, graph)
    return SimpleNamespace(
        title=title,
        subtitle=subtitle,
        formula=formula,
        axes=axes,
        labels=labels,
        graph=graph,
        panel=panel,
        root=VGroup(title, panel),
    )


def return_view():
    view = shallow_view()
    view.root.remove(view.caption)
    view.panel.remove(view.output_annotation)
    view.caption = slide_header(
        "A shallow network is a ", r"\textbf{single hidden layer}", " of ", r"\textbf{neurons}"
    )
    view.caption[1].set_color(OUTPUT)
    view.caption[3].set_color(NEURON)
    view.title = view.caption
    view.root.add(view.title)
    return view


def activation_gallery():
    cards = VGroup()
    specifications = [
        ("Sigmoid", r"\frac{1}{1+e^{-t}}", lambda t: 1 / (1 + np.exp(-t)), [-0.2, 1.2, 1], AFFINE),
        ("Tanh", r"\tanh(t)", np.tanh, [-1.2, 1.2, 1], NONLINEARITY),
        ("Softplus", r"\log(1+e^t)", lambda t: np.logaddexp(0, t), [-0.2, 4.2, 1], OUTPUT),
    ]
    for y, (name, expression, function, y_range, color) in zip([1.7, 0, -1.7], specifications):
        name_label = Tex(name, font_size=26, color=color).move_to([1.7, y + 0.4, 0])
        formula = MathTex(r"\sigma(t)=", expression, font_size=25)
        fit(formula, 2.9).move_to([1.7, y - 0.22, 0])
        axes = Axes(
            x_range=[-4, 4, 2],
            y_range=y_range,
            x_length=2.3,
            y_length=1.05,
            tips=False,
            axis_config={"include_ticks": False, "stroke_width": 1.5},
        ).move_to([4.8, y, 0])
        graph = axes.plot(function, x_range=[-4, 4], color=color, stroke_width=3)
        cards.add(VGroup(name_label, formula, axes, graph))
    return cards
