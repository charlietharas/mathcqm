from _helpers import bullet_points, slide_header
from scenes._settings import Slide


class LimitationsSlide(Slide):
    def construct(self):
        title = slide_header("Limitations")
        bullets = bullet_points(
            [
                r"No guarantees on necessary network size",
                r"No instructions on how to construct the network",
                r"No guidance on training dynamics, performance, etc.",
                r"No information about multilayer networks",
                r"Restricted to continuous functions over compact domains",
            ],
            title,
        )

        self.add(title)
        for bullet in bullets:
            self.add(bullet)
            self.gate()
