from manim import DOWN, LEFT, UP, VGroup

from _helpers import image_slide, paragraph, quote_layout, slide_header, source_footer
from scenes._settings import Slide


class PerceptronSlide(Slide):
    def construct(self):
        # The original AI hype wave
        title = slide_header("The original AI hype wave")
        view = quote_layout(
            "The perceptron, ``as its name implies, is capable of original thought... it strikes us as the first serious rival to the human brain ever devised.'' (The New Yorker, 1958)",
            author="Frank Rosenblatt",
            portrait="assets/rosenblatt.jpg",
            portrait_square=True,
            portrait_size=(3.2, 3.2),
            source="Mason, Stewart, Gill 1958",
        )
        self.add(title, view.root)
        self.gate()

        # Summer Vision Project
        self.clear()
        self.add(image_slide("assets/aim-100-abstract.png", header=title, source="Papert 1966"))
        self.gate()

        # The first AI winter
        self.clear()
        winter = quote_layout(
            "``In no part of the field have the discoveries made so far produced "
            "the major impact that was then promised.'' (James Lighthill, 1973)",
            portrait="assets/perceptrons-original-cover.jpg",
            portrait_size=(3.2, 4.4),
            source="Lighthill 1973",
        )
        book_caption = paragraph(
            r"\textit{Perceptrons}\\Minsky and Papert 1969", width=3.6, font_size=26
        ).next_to(winter.portrait, DOWN, buff=0.2)
        winter.root.add(book_caption)
        self.add(slide_header("The first AI winter"), winter.root)
        self.gate()

        # Learning and approximation
        self.clear()
        columns = VGroup()
        for x, heading, text in [
            (
                -6,
                r"\textbf{1986: Learning}",
                "``The ability to create useful new features distinguishes "
                "back-propagation from earlier, simpler methods such as the "
                "perceptron-convergence procedure.'' (Rumelhart, Hinton, Williams, 1986)",
            ),
            (
                0.5,
                r"\textbf{1989: Approximation}",
                "``Our results settle an open question about representability "
                "in the class of single hidden layer neural networks.'' (Cybenko, 1989)",
            ),
        ]:
            label = paragraph(heading, width=5.5, font_size=32)
            label.move_to([x, 2.05, 0], aligned_edge=UP + LEFT)
            quote = paragraph(text, width=5.5, font_size=32)
            quote.next_to(label, DOWN, buff=0.55, aligned_edge=LEFT)
            columns.add(VGroup(label, quote))
        self.add(
            slide_header("Learning and approximation"),
            VGroup(columns, source_footer("Rumelhart, Hinton, Williams 1986; Cybenko 1989")),
        )
        self.gate()

        # Universal Function Approximation
        self.clear()
        statement = paragraph(
            r"A neural network$^{*}$ with a single hidden layer can approximate$^{*}$ "
            "any continuous function over a compact domain.",
            width=11.5,
            font_size=36,
        ).move_to([0, 0.2, 0])
        self.add(slide_header("Universal Function Approximation"), statement)
        self.gate()
