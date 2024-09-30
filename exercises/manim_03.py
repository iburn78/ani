from manim import *

class ZoomAndPan(MovingCameraScene):
    def construct(self):
        # Load the image
        image = ImageMobject("rate_changes.png")  # Replace with your image path
        image.scale_to_fit_height(6)  # Adjust size if needed
        self.add(image)

        # Define camera movements with zoom levels
        camera_movements = [
            {'center': ORIGIN, 'zoom': 6.0},   # Center of the scene
            {'center': image.get_corner(DOWN + LEFT), 'zoom': 4.0},  # Move to bottom-left corner
            {'center': image.get_corner(UP + RIGHT), 'zoom': 3.0},  # Move to top-right corner
            {'center': ORIGIN, 'zoom': 6.0}    # Return to center
        ]

        # Apply camera movements with animations
        for i, movement in enumerate(camera_movements):
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
