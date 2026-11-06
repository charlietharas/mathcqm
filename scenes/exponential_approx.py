from functools import partial
from types import SimpleNamespace

from manim import LEFT, VGroup, Write, config
from _helpers import AFFINE, OUTPUT, equation, prose, slide_header
from scenes._settings import Slide

exponential_equation = partial(equation, x=-5.3, align=LEFT)


class ExponentialApproxSlide(Slide):
    def construct(self):
        views = self.sections()

        # Exponential family
        self.add(views.family_intro)
        self.gate()
        # Continuity and constants
        self.clear()
        self.add(views.family_checks)
        self.gate()

        # Addition and scalar multiplication
        self.clear()
        self.add(views.algebra_setup)
        self.gate()
        self.play(Write(views.addition), run_time=2.7)
        self.gate()
        self.play(Write(views.scaling), run_time=2.7)
        self.gate()

        # Multiplication
        self.clear()
        self.add(views.product_setup)
        self.play(Write(views.product_first), run_time=2.7)
        self.gate()
        self.play(Write(views.product_second), run_time=2.7)
        self.gate()

        # Separation of points
        self.clear()
        self.add(views.separation_setup)
        self.gate()
        self.add(views.separation_check)
        self.gate()

        # Stone-Weierstrass conclusion
        self.clear()
        self.add(views.conclusion)
        self.gate()

    def sections(self):
        product_template = config.tex_template.copy()
        product_template.add_to_preamble(r"\usepackage{xcolor}")
        colored_equation = partial(equation, x=-5.3, align=LEFT, tex_template=product_template)
        family_intro = VGroup(
            slide_header("Exponential approximation"),
            prose(r"Let $K\subseteq\mathbb{R}^d$ be compact. Define", y=2.45),
            exponential_equation(
                r"\mathcal{E}=\left\{x\mapsto\sum_{j=1}^{m}a_j e^{w_j^\top x}"
                r"\;\middle|\;m\geq1,\ a_j\in\mathbb{R},\ w_j\in\mathbb{R}^d\right\}.",
                y=1.25,
            ),
            prose(
                r"Claim: for every $f\in C(K)$ and $\varepsilon>0$, there exists $H\in\mathcal E$ with $\|f-H\|_\infty<\varepsilon/2$.",
                y=-0.15,
            ),
            prose("We show by applying Stone-Weierstrass.", y=-1.35),
        )
        family_checks = VGroup(
            slide_header("Exponential approximation"),
            prose(r"\textit{Proof.}", y=2.45),
            prose(
                r"1. $\mathcal{E}\subseteq C(K)$ and $\mathcal{E}$ contains all constants.", y=1.65
            ),
            prose(r"Each neuron is continuous; finite weighted sums preserve continuity.", y=0.9),
            exponential_equation(r"\mathcal{E}\subseteq C(K).", y=0.1),
            prose(r"Choosing $w=\mathbf{0}$ produces every constant function:", y=-0.75),
            exponential_equation(
                r"x\mapsto c e^{\mathbf{0}^\top x}=c,\qquad c\in\mathbb{R}.", y=-1.8
            ),
        )
        algebra_setup = VGroup(
            slide_header("Exponential approximation"),
            prose("2. Closure under addition and real scalar multiplication.", y=2.3),
            prose(r"Let $F,G\in\mathcal{E}$, with", y=1.6),
            colored_equation(
                product_colors(
                    r"F(x)=\sum_{j=1}^{r}a_j e^{u_j^\top x},\qquad "
                    r"G(x)=\sum_{k=1}^{s}b_k e^{v_k^\top x}."
                ),
                y=0.7,
            ),
        )
        addition = colored_equation(
            product_colors(
                r"(\textcolor[HTML]{8FAEFF}{F}+\textcolor[HTML]{F2A66F}{G})(x)="
                r"\sum_{j=1}^{r}a_j e^{u_j^\top x}+\sum_{k=1}^{s}b_k e^{v_k^\top x}\in\mathcal{E}."
            ),
            y=-0.5,
        )
        scaling = colored_equation(
            product_colors(
                r"(c\textcolor[HTML]{8FAEFF}{F})(x)="
                r"\sum_{j=1}^{r}(ca_j)e^{u_j^\top x}\in\mathcal{E},"
                r"\qquad c\in\mathbb{R}."
            ),
            y=-1.8,
        )
        product_first = colored_equation(
            product_colors(r"F(x)G(x)"),
            "=",
            product_colors(r"\sum_{j=1}^{r}\sum_{k=1}^{s}a_jb_k e^{u_j^\top x}e^{v_k^\top x}"),
            y=-0.5,
        )
        product_second = colored_equation(
            product_colors(
                r"=\sum_{j=1}^{r}\sum_{k=1}^{s}a_jb_k e^{(u_j+v_k)^\top x}\in\mathcal{E}."
            ),
            y=-1.8,
        )
        product_second.set_x(product_first[1].get_left()[0], direction=LEFT)
        product_setup = VGroup(
            algebra_setup[0],
            algebra_setup[2],
            algebra_setup[3],
            prose("3. Closure under multiplication.", y=2.3),
        )
        separation_setup = VGroup(
            slide_header("Exponential approximation"),
            prose(r"4. $\mathcal{E}$ separates points of $K$.", y=2.3),
            prose(
                r"Take $x,y\in K$ with $x\ne y$. Choose a coordinate $k$ with $x_k\ne y_k$.", y=1.6
            ),
            prose(r"Choose the $k$th coordinate unit vector:", y=0.7),
            colored_equation(
                r"w=\textcolor[HTML]{56C8D8}{\mathbf{e}_k},\qquad "
                r"w^\top x=\textcolor[HTML]{8FAEFF}{x_k},\quad "
                r"w^\top y=\textcolor[HTML]{F2A66F}{y_k}.",
                y=-0.15,
            ),
        )
        separation_check = VGroup(
            prose("Because the exponential is strictly increasing,", y=-1.0),
            colored_equation(
                r"e^{w^\top x}=e^{\textcolor[HTML]{8FAEFF}{x_k}}\ne "
                r"e^{\textcolor[HTML]{F2A66F}{y_k}}=e^{w^\top y}.",
                y=-1.85,
            ),
            prose(r"Thus $\mathcal{E}$ separates points.", y=-2.9),
        )
        conclusion = VGroup(
            slide_header("Exponential approximation"),
            prose(
                r"By Stone-Weierstrass, for every $f\in C(K)$ and every "
                r"$\varepsilon>0$, there exists a finite exponential network",
                y=2.2,
            ),
            exponential_equation(r"H(x)=\sum_{j=1}^{m}a_j e^{w_j^\top x}", y=0.85),
            prose("such that", y=-0.05),
            exponential_equation(r"\|f-H\|_\infty<\frac{\varepsilon}{2}.\qquad\square", y=-0.9),
        )
        return SimpleNamespace(
            family_intro=family_intro,
            family_checks=family_checks,
            algebra_setup=algebra_setup,
            addition=addition,
            scaling=scaling,
            product_setup=product_setup,
            product_first=product_first,
            product_second=product_second,
            separation_setup=separation_setup,
            separation_check=separation_check,
            conclusion=conclusion,
        )


def product_colors(body):
    for terms, color in [(("F(x)", "a_j", "u_j"), AFFINE), (("G(x)", "b_k", "v_k"), OUTPUT)]:
        for term in terms:
            body = body.replace(term, r"\textcolor[HTML]{" + color.lstrip("#") + "}{" + term + "}")
    return body
