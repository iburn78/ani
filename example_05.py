#%% 
from moviepy.editor import ImageClip, ColorClip, CompositeVideoClip
from PIL import Image
import time

# Function to resize with Lanczos filtering and unique filenames
def resize_image(image_path, target_height):
    img = Image.open(image_path)
    aspect_ratio = img.width / img.height
    new_width = int(target_height * aspect_ratio)
    resized_img = img.resize((new_width, target_height), Image.LANCZOS)
    
    # Create a unique filename to avoid overwriting
    timestamp = int(time.time())
    resized_path = f"resized_{timestamp}_" + image_path.split('/')[-1]
    
    resized_img.save(resized_path)
    return resized_path

# Set video parameters
video_duration = 10  # duration of the video in seconds
aspect_ratio = (16, 9)
fps = 30
video_resolution = (aspect_ratio[0] * 60, aspect_ratio[1] * 60)  # 16:9 aspect ratio

# Create a black screen video
black_clip = ColorClip(size=video_resolution, color=(0, 0, 0), duration=video_duration)

# Load and resize image 1
image1_path = r"wip/images/plot_01.png"
resized_image1_path = resize_image(image1_path, target_height=video_resolution[1] // 2)
image1 = ImageClip(resized_image1_path).set_duration(video_duration).set_start(1)

# Load and resize image 2
image2_path = r"wip/images/plot_02.png"
resized_image2_path = resize_image(image2_path, target_height=video_resolution[1] // 2)
image2 = ImageClip(resized_image2_path).set_duration(video_duration).set_start(5)

# Adjust position to fit in the left half of the screen
image1 = image1.set_position(lambda t: ((video_resolution[0] // 4) - image1.size[0] // 2, video_resolution[1] // 2 - image1.size[1] // 2))
image2 = image2.set_position(lambda t: ((video_resolution[0] // 4) - image2.size[0] // 2, video_resolution[1] // 2 - image2.size[1] // 2))

# Combine everything into a final clip
final_clip = CompositeVideoClip([black_clip, image1, image2])

# Write the final video to a file
final_clip.write_videofile("output_video.mp4", fps=fps)
