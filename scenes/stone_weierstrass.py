from manim import MathTex, VGroup
from _helpers import paragraph, slide_header, theorem_layout
from scenes._settings import Slide


class StoneWeierstrassSlide(Slide):
    def construct(self):
        theorem = theorem_layout(
            "Stone-Weierstrass",
            r"Let $K\subseteq\mathbb{R}^d$ be compact and let $\mathcal{A}\subseteq C(K)$. Suppose that",
            top=2.2,
        )
        requirements = VGroup(
            paragraph(
                r"$\bullet$ $\mathcal{A}$ contains every constant function.",
                width=11.2,
                font_size=31,
            ),
            paragraph(
                r"$\bullet$ $\mathcal{A}$ is closed under addition, multiplication by real scalars, and multiplication of functions.",
                width=11.2,
                font_size=31,
            ),
            paragraph(r"$\bullet$ $\mathcal{A}$ separates points:", width=11.2, font_size=31),
        )
        for row, y in zip(requirements, [0.9, 0.2, -0.85]):
            row.move_to([-5.5, y, 0], aligned_edge=[-1, 1, 0])
        separation = MathTex(
            r"x\ne y\quad\Longrightarrow\quad" r"\exists h\in\mathcal{A}:\ h(x)\ne h(y)",
            font_size=32,
        )
        separation.move_to([-4.9, -1.5, 0], aligned_edge=[-1, 0, 0])
        conclusion = paragraph(
            r"Then, for every $f\in C(K)$ and every $\varepsilon>0$, "
            r"there exists $h\in\mathcal{A}$ such that",
            width=11.6,
            font_size=31,
        )
        conclusion.move_to([-5.8, -2.0, 0], aligned_edge=[-1, 1, 0])
        bound = MathTex(r"\|f-h\|_\infty<\varepsilon.", font_size=42).move_to([0, -3.15, 0])
        self.add(
            slide_header("Stone-Weierstrass"),
            theorem.root,
            requirements,
            separation,
            conclusion,
            bound,
        )
        self.gate()
