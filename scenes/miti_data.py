from manim import ImageMobject, Tex
from _helpers import load_image, slide_header
from scenes._settings import Slide


class MitiDataSlide(Slide):
    def construct(self):
        self.add(slide_header("Data"))
        original = load_image("assets/interview.png")
        # Crop before render
        pixels = original.get_pixel_array()
        h, w = pixels.shape[:2]
        photo = ImageMobject(pixels[int(0.025 * h) : int(0.83 * h), int(0.31 * w) : int(0.85 * w)])
        photo.scale_to_fit_height(4.7)
        photo.move_to([-3.25, 1.4, 0], aligned_edge=[0, 1, 0])
        rlvr = load_image("assets/rlvr.png").scale_to_fit_height(4.7)
        rlvr.move_to([3.25, 1.4, 0], aligned_edge=[0, 1, 0])
        for center, heading in [(-3.25, "Gathered data"), (3.25, "RLVR")]:
            self.add(Tex(heading, font_size=32).move_to([center, 2.15, 0]))
        self.gate(frozen_frame=False)
        self.add(photo)
        self.gate(frozen_frame=False)
        self.add(rlvr)
        self.gate(frozen_frame=False)
