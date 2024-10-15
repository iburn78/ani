#%% 
from manim import *

class HelloWorld(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        text = Text('Hello 한글', font_size=72)
        text.to_edge(UP)

        self.add(circle)
        self.add(square)
        self.play(
            Transform(text[0], circle), 
            run_time=1, 
            rate_function=linear,
            )
        square.to_edge(UP)
        self.add(ThreeDAxes())

class Interactive3DScene(ThreeDScene):
    def construct(self):
        # Create 3D axes
        axes = ThreeDAxes()
        
        # Create a simple graph
        graph = axes.plot(lambda x: np.sin(x), x_range=[-3, 3], color=BLUE)
        
        # Add axes and graph to the scene
        self.add(axes, graph)

        # Rotate the scene
        self.move_camera(phi=75 * DEGREES, theta=30 * DEGREES, run_time=2)

        # Allow mouse input to interact with the axes
        self.add(axes)

        # Keep the scene displayed
        self.wait(3)