#%%

from moviepy.editor import ImageClip, VideoClip
from moviepy.video.fx.all import crop, resize
import numpy as np
import PIL
PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

# Parameters
image_path = 'rate_changes.png'  # Replace with your image path
output_path = 'outvideo.mp4'  # Path to save the output video

zoom_duration = 3  # Duration of zoom-in effect in seconds
stay_duration = 2  # Duration to stay at each zoomed-in region in seconds
zoom_out_duration = 3  # Duration to zoom out to full image in seconds
final_stay_duration = 5  # Duration to stay at the full image at the end in seconds
transition_duration = 1  # Duration of transition between zooms in seconds
final_height = 720  # Final height of the video
fps = 24  # Frames per second

# Load the image
image = ImageClip(image_path).resize(height=final_height)  # Resize for better handling

# Define camera movement path and zoom levels
camera_movements = [
    {'center': (0.5, 0.5), 'zoom': 1.0},  # Full image (no zoom)
    {'center': (0.3, 0.3), 'zoom': 2.0},  # Zoom into this region
    {'center': (0.7, 0.7), 'zoom': 2.5},  # Zoom into another region
    {'center': (0.5, 0.5), 'zoom': 3.0}   # Zoom back to center region
]

# Define segment duration
segment_duration = zoom_duration + stay_duration + transition_duration

def make_frame(t):
    """Generates a frame for time `t` with the current camera position and zoom."""
    total_zoom_in_duration = len(camera_movements) * segment_duration - stay_duration
    total_duration = total_zoom_in_duration + zoom_out_duration + final_stay_duration
    
    if t > total_duration:
        t = total_duration  # Clip time to the final duration
    
    # Determine the current segment and time within the segment
    segment_index = min(int(t / segment_duration), len(camera_movements) - 1)
    time_in_segment = t % segment_duration
    
    # Initial settings
    center_x, center_y = camera_movements[segment_index]['center']
    zoom_scale = camera_movements[segment_index]['zoom']

    # Handle different phases within each segment
    if time_in_segment <= zoom_duration:
        # Zoom-in phase
        zoom_scale = camera_movements[segment_index]['zoom']
    elif time_in_segment <= zoom_duration + stay_duration:
        # Stay phase
        zoom_scale = camera_movements[segment_index]['zoom']
    else:
        # Transition phase
        next_segment_index = min(segment_index + 1, len(camera_movements) - 1)
        next_center_x, next_center_y = camera_movements[next_segment_index]['center']
        next_zoom_scale = camera_movements[next_segment_index]['zoom']
        
        progress = (time_in_segment - (zoom_duration + stay_duration)) / transition_duration
        zoom_scale = (1 - progress) * zoom_scale + progress * next_zoom_scale
        center_x = (1 - progress) * center_x + progress * next_center_x
        center_y = (1 - progress) * center_y + progress * next_center_y

    # Handle final zoom out and stay
    if t > total_zoom_in_duration:
        if t <= total_zoom_in_duration + zoom_out_duration:
            # Zoom out phase
            progress = (t - total_zoom_in_duration) / zoom_out_duration
            zoom_scale = (1 - progress) * camera_movements[-1]['zoom'] + progress * 1.0
            center_x, center_y = camera_movements[-1]['center']
        else:
            # Final stay at the full image
            zoom_scale = 1.0
            center_x, center_y = (0.5, 0.5)
    
    # Calculate cropping box
    w, h = image.size
    new_w, new_h = w / zoom_scale, h / zoom_scale
    crop_x1 = int(center_x * w - new_w / 2)
    crop_y1 = int(center_y * h - new_h / 2)
    crop_x2 = crop_x1 + int(new_w)
    crop_y2 = crop_y1 + int(new_h)
    
    # Ensure cropping box is within image bounds
    crop_x1 = max(0, crop_x1)
    crop_y1 = max(0, crop_y1)
    crop_x2 = min(w, crop_x2)
    crop_y2 = min(h, crop_y2)
    
    # Create a frame with cropping and resizing
    frame = crop(image, x1=crop_x1, y1=crop_y1, x2=crop_x2, y2=crop_y2).resize((w, h))
    
    return frame.get_frame(0)

# Calculate the total duration
video_duration = len(camera_movements) * segment_duration - stay_duration + zoom_out_duration + final_stay_duration

# Create video clip from frames
video_clip = VideoClip(make_frame, duration=video_duration)
video_clip = video_clip.set_duration(video_duration)

# Write the video file
video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=fps)
