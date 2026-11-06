from _helpers import bullet_points, slide_header

from scenes._settings import Slide


class AgendaSlide(Slide):
    def construct(self):
        title = slide_header("Agenda")

        bullets = bullet_points(
            [
                r"AI hype",  # history
                r"But what is a neural network?",  # preamble
                r"Approximation in one dimension",  # math
                r"Universal Function Approximation",  # math
                r"The Curse of Dimensionality",  # math (lite)
                r"Breaking the Curse",  # math (lite)
            ],
            title,
        )

        self.add(title, bullets)
        self.gate()
