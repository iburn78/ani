#%% 
from moviepy.editor import VideoFileClip, concatenate_videoclips
from datetime import datetime

# List of video file names
videos = [
    '2024-09-30 18-23-52.mp4', 
    '2024-09-30 18-28-34.mp4',
    '2024-09-30 18-33-31.mp4',
]

# Update paths for video files
for i, v in enumerate(videos):
    videos[i] = 'data/video/' + v

# Load the video files with specified subclips
video_A = VideoFileClip(videos[0]).subclip(0, VideoFileClip(videos[0]).duration)  # A: full video
video_B = VideoFileClip(videos[1]).subclip(1, VideoFileClip(videos[1]).duration)  # B: from 1 sec to end
video_C = VideoFileClip(videos[2]).subclip(0, VideoFileClip(videos[2]).duration)  # C: full video

# Concatenate the clips
final_video = concatenate_videoclips([video_A, video_B, video_C])

# Increase the volume of the final concatenated video by a factor of 2 (double the volume)
final_video_vol_ajusted = final_video.volumex(2)

# Export the final video
final_video_vol_ajusted.write_videofile("data/video/final_video.mp4".replace('.mp4', '_'+datetime.now().strftime('%Y-%m-%d-%H-%M')+'.mp4'), codec="libx264")

