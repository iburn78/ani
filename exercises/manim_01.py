#%% 
# from manim import *


# class MySquare(Square):
#     @override_animation(FadeIn)
#     def _fade_in_override(self, **kwargs):
#         return Create(self, **kwargs)

# class OverrideAnimationExample(Scene):
#     def construct(self):
#         self.play(FadeIn(MySquare()))

# class OverrideAnimationExample(Scene):
#     def construct(self):
#         square = MySquare()
#         square.shift(LEFT + DOWN)  # Move the square to a new position
#         self.play(FadeIn(square))

# # don't remove below command for run button to work
# %manim -qm -v WARNING OverrideAnimationExample


#%% 
from manim import *

class TextScene(Scene):
    def construct(self):
        texts = [
            "첫 번째 단락입니다.",
            "두 번째 단락입니다.",
            "세 번째 단락입니다.",
            "네 번째 단락입니다."
        ]
        
        font = "NanumGothic"  # Use a known default font

        for i, text in enumerate(texts):
            text_mobject = Text(text, font=font, font_size=36, color=WHITE)
            text_mobject.move_to(ORIGIN)
            self.add(text_mobject)
            
            # Print debug information
            print(f"Displaying: {text}")

            # Play animations
            self.play(FadeIn(text_mobject))
            self.wait(10)  # Wait for 10 seconds
            if i < len(texts) - 1:
                self.play(FadeOut(text_mobject))

# Run with:
# manim -pql text_animation.py TextScene
%manim -ql -v WARNING TextScene