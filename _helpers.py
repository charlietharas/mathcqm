"""Shared formatting and diagrams for the slides

Palette
    NEURON, NONLINEARITY, AFFINE, OUTPUT, MUTED, EDGE

Text and layout
    load_image, fit, prose, caption, equation, named_group
    slide_header, theorem_layout, bullet_points, paragraph
    source_footer, image_slide, quote_layout

Graphs
    plot_axes, function_graph, tolerance_box
    vertical_grid, curve_band, epsilon_brace

Networks
    neuron_layer, dense_connections, network
    network_labels, strip_network_labels

Animation
    data_color, send_data, wave_stages, data_wave
    flow_during_text, dimmed

Layouts return mobjects or named parts with a .root group.
Scenes control their content, animation sequence and presenter breaks.
Slide.gate() in scenes/_settings.py marks a static presenter stop.

Generated with GPT Sol 6.1 and lots of human input :)
"""

import numpy as np
from types import SimpleNamespace
from pathlib import Path
from manim import (
    WHITE,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    ORIGIN,
    BraceBetweenPoints,
    Group,
    ImageMobject,
    MathTex,
    Tex,
    VGroup,
    config,
    Axes,
    Line,
    Polygon,
    BLACK,
    Arrow,
    Circle,
    Dot,
    LaggedStart,
    UpdateFromAlphaFunc,
    linear,
)
from contextlib import contextmanager

NEURON = "#56C8D8"
NONLINEARITY = "#F5D76E"
AFFINE = "#8FAEFF"
OUTPUT = "#F2A66F"
MUTED = "#A7AFBB"
EDGE = "#687383"


def load_image(path):
    """Load an image from a project-relative or absolute path"""
    return ImageMobject(str(Path(__file__).resolve().parent / path))


def fit(mobject, width):
    if mobject.width > width:
        mobject.scale_to_fit_width(width)
    return mobject


def prose(text, y=2.15, *, width=11.6, font_size=31, x=None, **kwargs):
    """Place a wrapped paragraph at the left margin"""
    return paragraph(text, width=width, font_size=font_size, **kwargs).move_to(
        [-width / 2 if x is None else x, y, 0], aligned_edge=UP + LEFT
    )


def caption(text, y, *, width=12, font_size=30, x=0, baseline=False, **kwargs):
    """Center a fitted text line, optionally aligned by its baseline"""
    if baseline:
        line = fit(Tex(text, "H", font_size=font_size, **kwargs), width)
        line.shift(UP * (y - line[-1].get_y()))
        line.remove(line[-1])
        return line.set_x(x)
    return fit(Tex(text, font_size=font_size, **kwargs), width).move_to([x, y, 0])


def equation(*parts, y=0, width=11.3, font_size=36, x=0, align=ORIGIN, emphasis=(), **kwargs):
    """Place a fitted equation with optional term colors"""
    if emphasis:
        kwargs.setdefault("substrings_to_isolate", [tex for tex, _ in emphasis])
    formula = fit(MathTex(*parts, font_size=font_size, **kwargs), width)
    for tex, color in emphasis:
        formula.set_color_by_tex(tex, color, substring=False)
    return formula.move_to([x, y, 0], aligned_edge=align)


def named_group(**parts):
    """Group named parts and expose the complete layout as .root"""
    return SimpleNamespace(root=VGroup(*parts.values()), **parts)


def slide_header(*parts, **kwargs):
    """Center a 42-point heading on the shared baseline"""
    header = Tex(*parts, "H", font_size=42, **kwargs)
    header.shift(UP * (3.25 - header[-1].get_y()))
    header.remove(header[-1])
    return header.set_x(0)


def theorem_layout(name, statement, *, width=11.6, top=2.05):
    """Stack a theorem label and statement on a shared left margin"""
    label = Tex(r"\textbf{Theorem (" + name + r").}", font_size=32)
    body = paragraph(r"\textit{" + statement + "}", width=width, font_size=32)
    root = VGroup(label, body).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
    root.move_to([-width / 2, top, 0], aligned_edge=UP + LEFT)
    return SimpleNamespace(label=label, statement=body, root=root)


def epsilon_brace(start, end, *, buff=0.06):
    """Make a narrow white brace for a vertical epsilon bound"""
    brace = BraceBetweenPoints(start, end, direction=RIGHT, buff=buff, color=WHITE)
    return brace.stretch_to_fit_width(0.1, about_edge=LEFT)


def bullet_points(
    items, header, *, font_size=36, step=0.72, gap=0.8, side_margin=1.2, bottom_margin=0.5
):
    """Space bullet baselines evenly and shrink the list to fit"""
    rows = VGroup(*(Tex(r"$\bullet$", " " + item, font_size=font_size) for item in items))
    if not items:
        return rows
    anchor = rows[0][0].get_center().copy()
    for index, row in enumerate(rows):
        row.shift(anchor + DOWN * (index * step) - row[0].get_center())
    height = header.get_bottom()[1] - gap + config.frame_height / 2 - bottom_margin
    width = config.frame_width - 2 * side_margin
    if height <= 0 or width <= 0:
        raise ValueError("No room for bullet list with these margins/header")
    rows.scale(min(1, height / rows.height, width / rows.width))
    return rows.to_edge(LEFT, buff=side_margin).next_to(header, DOWN, buff=gap, coor_mask=[0, 1, 0])


def paragraph(text, *, width=10, font_size=32, **kwargs):
    """Wrap TeX text in a left-aligned paragraph"""
    if width <= 0 or font_size <= 0:
        raise ValueError("width and font_size must be positive")
    # Manim scales TeX points by 0.001 * font_size
    points = width / (0.001 * font_size)
    body = rf"\begin{{minipage}}{{{points}pt}}\raggedright {text}\end{{minipage}}"
    return fit(Tex(body, font_size=font_size, **kwargs), width)


def source_footer(text, *, font_size=18, margin=0.4):
    """Place a muted citation at the bottom left"""
    return fit(
        Tex(text, font_size=font_size, color=MUTED, tex_environment="flushleft"),
        config.frame_width - 2 * margin,
    ).to_corner(DOWN + LEFT, buff=margin)


def image_slide(path, *, margin=0.6, header=None, source=None):
    """Fit an image within the slide margins, preserving its aspect ratio"""
    width = config.frame_width - 2 * margin
    top = header.get_bottom()[1] - 0.4 if header is not None else config.frame_height / 2 - margin
    footer = source_footer(source) if source else None
    bottom = footer.get_top()[1] + 0.4 if footer is not None else -config.frame_height / 2 + margin
    height = top - bottom
    if margin < 0 or width <= 0 or height <= 0:
        raise ValueError("Image margins/header/source must leave positive space")
    image = load_image(path)
    image.scale(min(width / image.width, height / image.height))
    image.move_to([0, (top + bottom) / 2, 0])
    if header is None and footer is None:
        return image
    return Group(
        *([header] if header is not None else []), image, *([footer] if footer is not None else [])
    )


def quote_layout(
    text,
    author=None,
    *,
    portrait=None,
    source=None,
    font_size=32,
    portrait_size=(2.4, 2.8),
    portrait_square=False,
):
    """Place a quote on the left with an optional portrait and credit on the right"""
    quote = paragraph(text, width=8, font_size=font_size)
    fit(quote, 8)
    if quote.height > 4:
        quote.scale_to_fit_height(4)
    quote.move_to([-2, 0.2, 0])
    credit = fit(Tex(author, font_size=26), 2.6) if author else None
    photo = None
    if portrait is not None:
        photo = load_image(portrait)
        if portrait_square:
            pixels = photo.get_pixel_array()
            height, width = pixels.shape[:2]
            side = min(height, width)
            # Keep the person at the left of a wide photo
            photo = ImageMobject(pixels[(height - side) // 2 : (height + side) // 2, :side])
        photo.scale(min(portrait_size[0] / photo.width, portrait_size[1] / photo.height))
        photo.move_to([4.5, 0.2, 0])
        if credit is not None:
            credit.next_to(photo, DOWN, buff=0.2)
    elif credit is not None:
        credit.move_to([4.5, 0.2, 0])
    footer = source_footer(source) if source else None
    root = Group(
        quote,
        *([credit] if credit is not None else []),
        *([photo] if photo is not None else []),
        *([footer] if footer is not None else []),
    )
    return SimpleNamespace(quote=quote, portrait=photo, author=credit, source=footer, root=root)


def plot_axes(*, x_range, y_range, x_length, y_length, center, axis_config=None):
    """Build plain axes with the given ranges, size and position"""
    style = {"include_ticks": False, "color": MUTED}
    style.update(axis_config or {})
    return Axes(
        x_range=x_range,
        y_range=y_range,
        x_length=x_length,
        y_length=y_length,
        tips=False,
        axis_config=style,
    ).move_to(center)


def function_graph(f):
    """Build the unit-interval plot used by the function examples"""
    axes = plot_axes(
        x_range=[0, 1, 0.25], y_range=[0, 1.5, 0.5], x_length=10, y_length=3.5, center=[0, -0.5, 0]
    )
    endpoints = VGroup(
        *(MathTex(str(x), font_size=24).move_to(axes.c2p(x, 0) + [0, -0.23, 0]) for x in [0, 1])
    )
    curve = axes.plot(f, x_range=[0, 1, 0.005], color=OUTPUT, stroke_width=4)
    return SimpleNamespace(axes=axes, endpoints=endpoints, curve=curve, f=f)


def tolerance_box(axes, x, y, delta, epsilon, *, x_bounds=None):
    """Draw an epsilon-delta window, optionally clipped to an interval"""
    lo, hi = (
        x_bounds
        if x_bounds is not None
        else (max(axes.x_range[0], x - delta), min(axes.x_range[1], x + delta))
    )
    return Polygon(
        *[
            axes.c2p(a, b)
            for a, b in [(lo, y - epsilon), (hi, y - epsilon), (hi, y + epsilon), (lo, y + epsilon)]
        ],
        color=NONLINEARITY,
        stroke_width=1.5,
        fill_color=NONLINEARITY,
        fill_opacity=0.09,
    )


def vertical_grid(axes, xs, top, *, color=MUTED, stroke_width=1, stroke_opacity=0.3):
    """Draw vertical guides at the supplied x coordinates"""
    return VGroup(
        *(
            Line(
                axes.c2p(x, 0),
                axes.c2p(x, top),
                color=color,
                stroke_width=stroke_width,
                stroke_opacity=stroke_opacity,
            )
            for x in xs
        )
    )


def curve_band(axes, f, epsilon, *, xs=None, color=OUTPUT, opacity=0.13):
    """Shade the epsilon band around a curve"""
    xs = np.linspace(0, 1, 161) if xs is None else list(xs)
    return Polygon(
        *[axes.c2p(x, f(x) + epsilon) for x in xs],
        *[axes.c2p(x, f(x) - epsilon) for x in xs[::-1]],
        stroke_width=0,
        fill_color=color,
        fill_opacity=opacity,
    )


def neuron_layer(x, ys, *, radius=0.25, color=NEURON, stroke_width=2.5):
    """Build a layer of neurons at the supplied positions"""
    return VGroup(
        *(
            Circle(radius=radius, stroke_color=color, stroke_width=stroke_width)
            .set_fill(BLACK, opacity=1)
            .move_to([x, y, 0])
            .set_z_index(2)
            for y in ys
        )
    )


def dense_connections(source, target, *, boundary=True, stroke_width=1.5, stroke_opacity=0.65):
    """Connect every node in one layer to every node in the next"""
    return VGroup(
        *(
            Line(
                start.get_right() if boundary else start.get_center(),
                end.get_left() if boundary else end.get_center(),
                color=EDGE,
                stroke_width=stroke_width,
                stroke_opacity=stroke_opacity,
            )
            for start in source
            for end in target
        )
    )


def network(hidden_layers=1, compact=False):
    """Build a network diagram with ellipses for omitted neurons"""
    span = 1.8 if compact else 3.1
    xs = (
        np.linspace(-span, span, 3) if hidden_layers == 1 else np.linspace(-5, 5, hidden_layers + 2)
    )
    sizes = [3, *([4] * hidden_layers), 1]
    layers = []
    coordinates = VGroup()
    neuron_labels = VGroup()
    omissions = VGroup()
    labels = VGroup()

    for index, (x, size) in enumerate(zip(xs, sizes)):
        ys = np.linspace(1.35, -1.35, size) + 0.55 if size > 1 else [0.55]
        hidden = 0 < index < len(sizes) - 1
        color = NEURON if hidden else WHITE
        layer = neuron_layer(x, ys, color=color)
        layers.append(layer)
        if size > 1:
            dots = MathTex(r"\vdots", font_size=20, color=MUTED)
            dots.move_to((layer[-2].get_center() + layer[-1].get_center()) / 2)
            omissions.add(dots.set_z_index(3))

        if index == 0:
            label = MathTex(r"d\text{ inputs}", font_size=23, color=MUTED)
            for node, symbol in zip(layer, [r"x_1", r"x_2", r"x_d"]):
                coordinates.add(MathTex(symbol, font_size=20).move_to(node).set_z_index(3))
        elif index == len(sizes) - 1:
            label = Tex("output", font_size=23, color=MUTED)
        elif hidden_layers == 1:
            label = MathTex(r"m\text{ neurons}", font_size=23, color=MUTED)
        else:
            label = Tex(f"hidden layer {index}", font_size=23, color=MUTED)
        if hidden:
            for node, subscript in zip(layer, ["1", "2", "3", "m"]):
                symbol = (
                    rf"h_{{{subscript}}}"
                    if hidden_layers == 1
                    else rf"h^{{({index})}}_{{{subscript}}}"
                )
                neuron_labels.add(
                    MathTex(symbol, font_size=20 if hidden_layers == 1 else 15)
                    .move_to(node)
                    .set_z_index(3)
                )
        labels.add(label.move_to([x, 2.45, 0]))

    connections = [dense_connections(source, target) for source, target in zip(layers, layers[1:])]
    edges = VGroup(*connections)
    nodes = VGroup(*layers)
    entry = Arrow(
        [xs[0] - 1.4, 0.55, 0], [xs[0] - 0.25, 0.55, 0], buff=0, color=AFFINE, stroke_width=3
    )
    exit_arrow = Arrow(
        [xs[-1] + 0.25, 0.55, 0], [xs[-1] + 1.4, 0.55, 0], buff=0, color=OUTPUT, stroke_width=3
    )
    input_symbol = MathTex(r"x\in\mathbb{R}^d", font_size=28, color=AFFINE)
    input_symbol.next_to(entry, UP, buff=0.16)
    output_symbol = MathTex(r"y\in\mathbb{R}", font_size=28, color=OUTPUT).next_to(
        exit_arrow, UP, buff=0.16
    )
    ports = VGroup(entry, exit_arrow, input_symbol, output_symbol)
    return {
        "group": VGroup(edges, nodes, coordinates, neuron_labels, omissions, labels, ports),
        "layers": layers,
        "connections": connections,
        "edges": edges,
        "nodes": nodes,
        "coordinates": coordinates,
        "neuron_labels": neuron_labels,
        "omissions": omissions,
        "labels": labels,
        "ports": ports,
        "entry": entry,
        "exit": exit_arrow,
        "input_symbol": input_symbol,
        "output_symbol": output_symbol,
    }


def network_labels(diagram):
    return VGroup(diagram["coordinates"], diagram["neuron_labels"], diagram["labels"])


def strip_network_labels(diagram):
    """Remove labels from the group before transforming the network"""
    diagram["group"].remove(diagram["coordinates"], diagram["neuron_labels"], diagram["labels"])


def data_color(depth):
    # Shift toward pale blue at each layer
    palette = [AFFINE, "#A0B9F3", "#B1C4E9", "#C2CFDF", "#D3DAD5"]
    return palette[min(depth, len(palette) - 1)]


def send_data(scene, connections, color, run_time=1):
    if scene.loopingLevel == 0:
        return
    pulses = [
        Dot(edge.get_start(), radius=0.055, color=color).set_z_index(4) for edge in connections
    ]
    animations = []
    for pulse, edge in zip(pulses, connections):

        def travel(dot, alpha, path=edge):
            dot.move_to(path.point_from_proportion(alpha))
            dot.set_opacity(0 if alpha >= 1 else 1)

        animations.append(UpdateFromAlphaFunc(pulse, travel, rate_func=linear, remover=True))
    scene.add(*pulses)
    scene.play(LaggedStart(*animations, lag_ratio=0.03), run_time=run_time)
    scene.remove(*pulses)


def wave_stages(diagram, neuron_index=None):
    """List the paths and durations for one data wave"""
    connections = diagram["connections"]
    if neuron_index is not None:
        input_count = len(diagram["layers"][0])
        hidden_count = len(diagram["layers"][1])
        output_count = len(diagram["layers"][2])
        connections = [
            VGroup(*[connections[0][i * hidden_count + neuron_index] for i in range(input_count)]),
            VGroup(*[connections[1][neuron_index * output_count + i] for i in range(output_count)]),
        ]
    stages = []
    if diagram["ports"] in diagram["group"].submobjects:
        stages.append((VGroup(diagram["entry"]), 0.3))
    stages.extend((edges, 1.0) for edges in connections)
    # Stop a highlighted neuron’s wave at the output node
    if neuron_index is None and diagram["ports"] in diagram["group"].submobjects:
        stages.append((VGroup(diagram["exit"]), 0.3))
    return stages


def data_wave(scene, diagram, neuron_index=None):
    """Send one data wave through the network"""
    port_offset = int(diagram["ports"] in diagram["group"].submobjects)
    for index, (edges, duration) in enumerate(wave_stages(diagram, neuron_index)):
        send_data(scene, edges, data_color(max(0, index - port_offset)), run_time=duration)


@contextmanager
def flow_during_text(scene, diagram, neuron_index=None):
    """Keep data moving during text reveals and finish the active wave on exit"""
    if scene.loopingLevel == 0:
        yield
        return
    repeat = scene.loopingLevel == 2
    stages = wave_stages(diagram, neuron_index)
    active_duration = sum(duration for _, duration in stages)
    period = active_duration + 0.2
    elapsed = 0.0
    draining = False
    particles = VGroup()
    schedule = []
    offset = 0.0
    port_offset = int(diagram["ports"] in diagram["group"].submobjects)
    for stage_index, (edges, duration) in enumerate(stages):
        # Match send_data's LaggedStart timing
        travel_time = duration / (1 + 0.03 * (len(edges) - 1))
        for index, edge in enumerate(edges):
            dot = Dot(
                edge.get_start(), radius=0.055, color=data_color(max(0, stage_index - port_offset))
            )
            dot.set_z_index(4).set_opacity(0)
            particles.add(dot)
            schedule.append((dot, edge, offset + index * 0.03 * travel_time, travel_time))
        offset += duration

    def update(_particles, dt):
        nonlocal elapsed
        elapsed += dt
        if not repeat and elapsed >= active_duration:
            # Stop updating hidden particles after a single wave
            particles.remove_updater(update)
            particles.set_opacity(0)
            scene.remove(particles, *particles.submobjects)
            return
        # Drain the current wave before leaving the view
        phase = elapsed % period if repeat and not draining else elapsed
        for dot, edge, start, duration in schedule:
            alpha = (phase - start) / duration
            dot.set_opacity(1 if 0 <= alpha < 1 else 0)
            if 0 <= alpha < 1:
                dot.move_to(edge.point_from_proportion(alpha))

    # Use a mobject updater so Cairo keeps waits animating
    particles.add_updater(update)
    scene.add(particles)
    try:
        yield
    finally:
        if repeat:
            elapsed %= period
        draining = True
        try:
            remaining = max(0.0, active_duration - elapsed)
            if remaining:
                scene.wait(remaining, frozen_frame=False)
            # Hide particles at the clip boundary despite frame rounding
            particles.remove_updater(update)
            particles.set_opacity(0)
            scene.wait(0.2)
        finally:
            particles.remove_updater(update)
            scene.remove(particles, *particles.submobjects)


def dimmed(mobject, opacity=0.22):
    """Copy a diagram and reduce its existing fill and stroke opacities"""
    result = mobject.copy()
    for part in result.family_members_with_points():
        part.set_stroke(opacity=part.get_stroke_opacity() * opacity)
        part.set_fill(opacity=part.get_fill_opacity() * opacity)
    return result
