from manim import *

class ZoomAndPanWithPoints(MovingCameraScene):
    def construct(self):
        # Load the image
        image = ImageMobject("rate_changes.png")  # Replace with your image path
        image.scale_to_fit_height(6)  # Adjust size if needed
        self.add(image)

        # Define specific points to highlight (these coordinates are relative to the image)
        points_to_mark = [
            {'point': [1, 1, 0], 'label': 'Point A'},
            {'point': [-1, -1, 0], 'label': 'Point B'},
            {'point': [2, -1, 0], 'label': 'Point C'}
        ]

        # Mark the points with Dots and Labels
        for item in points_to_mark:
            point = item['point']
            label = item['label']
            
            # Add a dot at the point
            dot = Dot(point, color=RED)
            self.add(dot)
            
            # Add a label next to the dot
            label = Text(label).next_to(dot, UP)
            self.add(label)

        # Define camera movements with zoom levels
        camera_movements = [
            {'center': points_to_mark[0]['point'], 'zoom': 2.0},  # Zoom in on Point A
            {'center': points_to_mark[1]['point'], 'zoom': 2.0},  # Zoom in on Point B
            {'center': points_to_mark[2]['point'], 'zoom': 2.0},  # Zoom in on Point C
            {'center': ORIGIN, 'zoom': 6.0}    # Zoom out to show the whole image
        ]

        # Apply camera movements with animations
        for movement in camera_movements:
            center = movement['center']
            zoom_scale = movement['zoom']

            # Move the camera to the specified center and zoom in/out
            self.play(
                self.camera.frame.animate.move_to(center).set(width=zoom_scale),
                run_time=2
            )
            self.wait(2)

        # At the end, zoom out and show the full image
        self.play(
            self.camera.frame.animate.move_to(ORIGIN).set(width=6.0),
            run_time=3
        )
        # Keep the full image visible for 5 seconds
        self.wait(5)
