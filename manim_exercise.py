# #%% 
# from manim import *

# class HelloWorld(Scene):
#     def construct(self):
#         circle = Circle()
#         square = Square()
#         text = Text('Hello 한글', font_size=72)
#         text.to_edge(UP)

#         self.add(circle)
#         self.add(square)
#         self.play(
#             Transform(text[0], circle), 
#             run_time=1, 
#             rate_function=linear,
#             )
#         square.to_edge(UP)
#         self.add(ThreeDAxes())

# class Interactive3DScene(ThreeDScene):
#     def construct(self):
#         # Create 3D axes
#         axes = ThreeDAxes()
        
#         # Create a simple graph
#         graph = axes.plot(lambda x: np.sin(x), x_range=[-3, 3], color=BLUE)
        
#         # Add axes and graph to the scene
#         self.add(axes, graph)

#         # Rotate the scene
#         self.move_camera(phi=75 * DEGREES, theta=30 * DEGREES, run_time=2)

#         # Allow mouse input to interact with the axes
#         self.add(axes)

#         # Keep the scene displayed
#         self.wait(3)


from manim import *
import numpy as np
import pandas as pd
import yfinance as yf

apple_data = yf.download("AAPL", period="3mo", interval="1d")
apple_prices = apple_data['Close']  # We'll animate closing prices


class StockPriceAnimation(Scene):
    def construct(self):
        # Set up axes
        axes = Axes(
            x_range=[0, len(apple_prices), 1],  # Number of days
            y_range=[min(apple_prices), max(apple_prices), 10],  # Price range
            axis_config={"color": WHITE}
        ).add_coordinates()

        # Add labels for axes
        labels = axes.get_axis_labels(x_label="Days", y_label="Price")

        # Initial empty graph
        price_graph = VGroup()

        # Add the graph to the scene
        self.play(Create(axes), Write(labels))

        # Add points and line segments sequentially
        for i in range(1, len(apple_prices)):
            # Get the price point
            point = axes.c2p(i, apple_prices[i])  # convert to manim coordinates

            # Draw point
            dot = Dot(point, color=BLUE)
            price_graph.add(dot)

            # Draw line connecting the previous point to this one
            if i > 1:
                line = Line(axes.c2p(i-1, apple_prices[i-1]), point, color=GREEN)
                price_graph.add(line)
                self.play(Create(line), run_time=0.2)  # Animate line creation

            self.play(Create(dot), run_time=0.1)

        # Hold the final frame for a few seconds
        self.wait(2)

# To render, run the command# manim -pql script.py StockPriceAnimation

import yfinance as yf
from manim import *

class StockPriceScene(Scene):
    def construct(self):
        # Fetch historical stock data
        stock_data = yf.download("AAPL", start="2023-01-01", end="2023-10-01")
        
        # Prepare data for plotting
        time_series = stock_data.index.tolist()
        prices = stock_data['Close'].tolist()

        # Create axes
        axes = Axes(
            x_range=[0, len(time_series)-1, 1],
            y_range=[min(prices)-10, max(prices)+10, 10],
            axis_config={"color": BLUE},
        )
        self.play(Create(axes))

        # Create the graph
        graph = axes.plot_line_graph(
            x_values=range(len(time_series)), 
            y_values=prices, 
            line_color=YELLOW
        )
        self.play(Create(graph))

        # Add a title using Text instead of LaTeX
        title = Text("Apple Stock Prices", font_size=24)
        title.to_edge(UP)
        self.play(Write(title))

        # Wait before ending the scene
        self.wait(2)

# To render this animation, run:
# manim -pql your_file.py StockPriceScene
#%% 
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Fetch historical stock data
stock_data = yf.download("AAPL", start="2023-01-01", end="2023-10-01")

# Prepare data for plotting
time_series = stock_data.index
prices = stock_data['Close'].values

# Create the figure and axis
fig, ax = plt.subplots()
ax.set_facecolor('black')
line, = ax.plot([], [], lw=2, color='yellow')
ax.set_xlim(0, len(prices)-1)
ax.set_ylim(np.min(prices)-10, np.max(prices)+10)
ax.set_xlabel('Days')
ax.set_ylabel('Stock Price (USD)')
ax.set_title('Apple Stock Prices Over Time')

# Function to initialize the background of the animation
def init():
    line.set_data([], [])
    return line,


# Function to animate each frame (two points at a time)
def animate(i):
    # Calculate the index by multiplying i by 2, so two points are added per frame
    idx = i * 4
    # Set x-data and y-data to include two more points
    line.set_data(range(idx + 1), prices[:idx + 1])
    return line,

# Create the animation
frames = len(prices) // 4  # Adjust the number of frames, since we add two points per frame
ani = animation.FuncAnimation(fig, animate, frames=frames, init_func=init, blit=True, interval=20)

# To save the animation as a video (optional)
ani.save('stock_prices_animation.mp4', writer='ffmpeg', fps=24)

# Display the animation
plt.show()
