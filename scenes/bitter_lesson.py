from _helpers import quote_layout, slide_header
from scenes._settings import Slide


class BitterLessonSlide(Slide):
    def construct(self):
        view = quote_layout(
            "``General methods that leverage computation are ultimately the most "
            "effective, and by a large margin.''",
            author="Rich Sutton",
            source="Sutton 2019",
            portrait="assets/sutton-portrait.jpg",
            portrait_size=(2.7, 3.3),
        )
        self.add(slide_header("The Bitter Lesson"), view.root)
        self.gate(frozen_frame=False)
