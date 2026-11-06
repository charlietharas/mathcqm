"""
Deck settings shared by direct Manim renders and deck.py builds.
Generated with GPT Sol 6.1.
"""

from pathlib import Path
import tomllib

from manim_slides import Slide as ManimSlide

with (Path(__file__).resolve().parents[1] / "deck.toml").open("rb") as source:
    SETTINGS = tomllib.load(source)

if type(SETTINGS.get("skip_reversing", True)) is not bool:
    raise ValueError("deck.toml: skip_reversing must be a boolean")

LOOPING_LEVEL = SETTINGS.get("loopingLevel", 2)
if type(LOOPING_LEVEL) not in (int, float) or LOOPING_LEVEL not in (0, 1, 1.5, 2):
    raise ValueError("deck.toml: loopingLevel must be 0, 1, 1.5, or 2")


class Slide(ManimSlide):
    skip_reversing = SETTINGS.get("skip_reversing", True)
    loopingLevel = LOOPING_LEVEL

    def gate(self, duration=0.1, *, frozen_frame=None, **slide_options):
        """Wait for a settled frame before a presenter break"""
        if frozen_frame is None:
            self.wait(duration)
        else:
            self.wait(duration, frozen_frame=frozen_frame)
        self.next_slide(**slide_options)

    def render(self, *args, **kwargs):
        try:
            return super().render(*args, **kwargs)
        except BaseException:
            # Unblock Manim's writer thread on render failure
            writer = self.renderer.file_writer
            thread = getattr(writer, "writer_thread", None)
            if thread is not None and thread.is_alive():
                writer.queue.put((-1, None))
                thread.join(timeout=5)
                if not thread.is_alive():
                    try:
                        writer.video_container.close()
                    except Exception:
                        pass  # Keep the original exception
            raise
