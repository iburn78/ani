#%%
from moviepy.editor import ImageClip, concatenate_videoclips
from moviepy.video.fx.all import crop, resize, fadein
import PIL
PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

# Parameters
image_path = 'rate_changes.png'  # Replace with your image path
output_path = 'outvideo.mp4'  # Path to save the output video

# Parameters
zoom_duration = 2  # Duration of each zoom in seconds
transition_duration = 1  # Duration of transition between zooms in seconds

# Load the image
image = ImageClip(image_path).set_duration(zoom_duration + transition_duration).resize(height=720)  # Resize for better handling

# Define zoom positions and sizes
zoom_positions = [
    {'center': (0.5, 0.5), 'zoom': 1.0},  # Full image (no zoom)
    {'center': (0.3, 0.3), 'zoom': 2.0},  # Example zoom region
    {'center': (0.7, 0.7), 'zoom': 2.5},  # Another example zoom region
    {'center': (0.5, 0.5), 'zoom': 3.0}   # Another example zoom region
]

# Create clips with zoom effect
clips = []
for i, pos in enumerate(zoom_positions):
    center_x, center_y = pos['center']
    zoom_scale = pos['zoom']
    
    # Calculate cropping box
    w, h = image.size
    new_w, new_h = w / zoom_scale, h / zoom_scale
    crop_x1 = int(center_x * w - new_w / 2)
    crop_y1 = int(center_y * h - new_h / 2)
    crop_x2 = crop_x1 + int(new_w)
    crop_y2 = crop_y1 + int(new_h)
    
    # Define zoom effect
    zoom_effect = crop(image, x1=crop_x1, y1=crop_y1, x2=crop_x2, y2=crop_y2).resize(image.size)
    
    # Apply transition effect if it's not the first clip
    if i > 0:
        transition = fadein(zoom_effect, transition_duration)
        clips.append(transition)
    
    clips.append(zoom_effect)

# Concatenate clips
final_video = concatenate_videoclips(clips, method="compose")

# Write the video file
final_video.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=24)
