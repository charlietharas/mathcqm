from types import SimpleNamespace

from functools import partial

from manim import Arrow, Create, FadeIn, FadeOut, MathTex, Tex, Transform, VGroup, Write
from _helpers import AFFINE, MUTED, OUTPUT, equation, prose, slide_header
from scenes._settings import Slide

relu_equation = partial(equation, font_size=37)


class ExponentialReLUSlide(Slide):
    def construct(self):
        # Exponential neuron on a bounded interval
        self.approximate_neuron()
        self.gate()

        # One-dimensional ReLU approximation
        neuron = self.substitution_setup()
        self.gate()

        # Substitute the affine input
        self.substitute_input(neuron)
        self.gate()

        # Original exponential network
        network = self.network_setup()
        self.gate()

        # Replace its neurons with ReLU networks
        self.replace_neurons(network)
        self.gate()

        # Replacement-error assumption
        self.error_assumption()
        self.gate()

        # Weighted error
        self.weighted_error()
        self.gate()

        # Choose the tolerance
        self.choose_tolerance()
        self.gate()

        # Final error budget
        self.error_budget()
        self.gate()

    def approximate_neuron(self):
        self.add(
            slide_header("ReLU approximation"),
            prose("Recall that our exponential network is described by"),
            relu_equation(r"H(x)=\sum_{j=1}^{m}a_j e^{w_j^\top x}.", y=1.25),
            prose(
                r"Although $x$ has many coordinates, this neuron uses them only to "
                r"calculate one real number, $t=w^\top x$.",
                y=0.5,
            ),
            relu_equation(
                r"x\mapsto e^{w^\top x}=e^t,\qquad t=w^\top x.",
                y=-0.55,
                emphasis=[(r"e^{w^\top x}", AFFINE), ("e^t", AFFINE)],
            ),
            prose(r"Because $K$ is compact, $w^\top x$ stays in a bounded interval.", y=-1.4),
            relu_equation(r"w^\top x\in[A,B]\qquad(x\in K).", y=-2.3),
        )

    def substitution_setup(self):
        self.clear()
        title = slide_header("ReLU approximation")
        note = prose(r"By one-dimensional approximation, construct a ReLU network $q$ such that")
        bound = relu_equation(
            r"|e^t-q(t)|<\eta\qquad\forall t\in[A,B].",
            y=1.2,
            emphasis=[("q(t)", AFFINE), (r"\eta", OUTPUT)],
        )
        rescaling = prose(
            "Our earlier construction applies to any finite interval by rescaling.", y=0.35
        )
        setup = prose(r"\vphantom{$q\,w^\top$}If a neuron in $q$ is", y=-0.5)
        before = relu_equation(r"t\mapsto\sigma(\alpha t+\beta),", y=-1.4)
        self.add(title, note, bound, rescaling, setup, before)

        return SimpleNamespace(setup=setup, before=before)

    def substitute_input(self, view):
        setup = view.setup
        before = view.before
        then_note = prose(
            r"\vphantom{$q\,w^\top$}then after substituting $t=w^\top x$, the neuron becomes",
            y=-0.5,
        )
        substituted = relu_equation(r"x\mapsto\sigma(\alpha(w^\top x)+\beta),", y=-1.4)
        after = relu_equation(r"x\mapsto\sigma((\alpha w)^\top x+\beta).", y=-1.4)
        self.play(FadeOut(setup), run_time=0.3)
        self.play(FadeIn(then_note), Transform(before, substituted), run_time=1.2)
        self.wait(0.5)
        self.play(Transform(before, after), run_time=0.9)

    def network_setup(self):
        self.clear()
        title = slide_header("ReLU approximation")
        note = prose(
            r"For each $j$, construct $q_j$ on an interval containing "
            r"all values of $w_j^\top x$ for $x\in K$."
        )
        # Ignore superscripts when aligning the prose
        note.shift([0, note.get_top()[1] - note[0][0].get_top()[1], 0])
        source = relu_equation(
            r"H(x)=\sum_{j=1}^{m}a_j e^{w_j^\top x}.",
            y=0.95,
            font_size=39,
            emphasis=[(r"e^{w_j^\top x}", AFFINE)],
        )
        self.add(title, note, source)

        return SimpleNamespace(source=source)

    def replace_neurons(self, view):
        source = view.source
        target = relu_equation(
            r"N_\theta(x)=\sum_{j=1}^{m}a_j q_j(w_j^\top x).",
            y=0.95,
            font_size=39,
            emphasis=[(r"q_j(w_j^\top x)", AFFINE)],
        )
        combining = prose(
            r"Combining the hidden neurons and collecting the weighted output "
            r"biases gives one finite shallow ReLU network.",
            y=-0.65,
        )
        self.play(Transform(source, target), FadeIn(combining, run_time=0.6), run_time=1.3)

    def error_assumption(self):
        self.clear()
        assumption = relu_equation(
            r"|e^{w_j^\top x}-q_j(w_j^\top x)|\leq\eta" r"\qquad(x\in K,\ j=1,\ldots,m).",
            y=1.1,
            font_size=35,
            emphasis=[(r"\eta", OUTPUT)],
        )
        self.add(
            slide_header("ReLU approximation"),
            prose(r"Each replacement error is multiplied by its original output weight $a_j$."),
        )
        self.add(assumption)

    def weighted_error(self):
        estimate = relu_equation(
            r"\begin{aligned}|H(x)-N_\theta(x)|"
            r"&\leq\sum_{j=1}^{m}|a_j|\,"
            r"|e^{w_j^\top x}-q_j(w_j^\top x)|\\"
            r"&\leq\eta\sum_{j=1}^{m}|a_j|.\end{aligned}",
            y=-0.65,
            font_size=36,
            emphasis=[(r"\eta", OUTPUT)],
        )
        self.play(Write(estimate), run_time=4.1)

    def choose_tolerance(self):
        tolerance = relu_equation(
            r"\eta=\frac{\varepsilon}{2(1+\sum_{j=1}^{m}|a_j|)}"
            r"\quad\Longrightarrow\quad "
            r"\|H-N_\theta\|_\infty<\frac{\varepsilon}{2}.",
            y=-2.65,
            font_size=36,
            emphasis=[(r"\eta", OUTPUT)],
        )
        self.play(Write(tolerance), run_time=3.8)

    def error_budget(self):
        self.clear()
        self.add(slide_header("Universal approximation"))
        symbols = VGroup(
            *(
                MathTex(tex, font_size=58).move_to([x, 1.1, 0])
                for tex, x in [("f", -4), ("H", 0), (r"N_\theta", 4)]
            )
        )
        arrows = VGroup(
            *(
                Arrow([a, 1.1, 0], [b, 1.1, 0], buff=0, color=MUTED)
                for a, b in [(-3.3, -0.6), (0.7, 3.1)]
            )
        )
        bounds = VGroup(
            *(
                MathTex(r"<\varepsilon/2", font_size=32, color=OUTPUT).move_to([x, 1.65, 0])
                for x in [-2, 2]
            )
        )
        self.add(symbols)
        self.play(Create(arrows), FadeIn(bounds), run_time=0.6)
        conclusion = relu_equation(
            r"\begin{aligned}\|f-N_\theta\|_\infty"
            r"&\leq\|f-H\|_\infty+\|H-N_\theta\|_\infty\\"
            r"&<\frac{\varepsilon}{2}+\frac{\varepsilon}{2}=\varepsilon."
            r"\qquad\square\end{aligned}",
            y=-0.8,
            font_size=40,
        )
        self.play(Write(conclusion), run_time=2.3)
        self.wait(0.4)
        closing = Tex("This completes our conversion back to ReLU.", font_size=31)
        closing.move_to([0, -2.05, 0])
        self.play(FadeIn(closing), run_time=0.9)
