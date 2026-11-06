from manim import DOWN, Tex, VGroup

from scenes._settings import Slide


class TitleSlide(Slide):
    def construct(self):
        title = Tex("The Cure and The Cause", font_size=60)
        subtitle = Tex(
            "Universal Function Approximation and the Curse of Dimensionality", font_size=32
        )
        VGroup(title, subtitle).arrange(DOWN, buff=0.5)
        self.add(title, subtitle)
        self.gate()
