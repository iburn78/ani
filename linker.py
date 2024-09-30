#%% 
from moviepy.editor import VideoFileClip, concatenate_videoclips

videos = [
    '2024-09-22 14-07-06.mp4', 
    '2024-09-22 14-09-13.mp4',
    '2024-09-22 14-10-53.mp4',
    '2024-09-22 14-11-41.mp4',
    '2024-09-22 14-13-24.mp4'
]
for i, v in enumerate(videos):
    videos[i] = 'videos/'+v
# Load the video files
video_A = VideoFileClip(videos[0]).subclip(0, 50)  # A: from start to 50 sec
video_B = VideoFileClip(videos[1]).subclip(0, 73)  # B: from start to 13 sec
video_C = VideoFileClip(videos[2]).subclip(0, 27)  # C: from start to 27 sec
video_D = VideoFileClip(videos[3]).subclip(0, 90)  # D: from start to 1 min 30 sec
video_E = VideoFileClip(videos[4])                 # E: from start to end

# Concatenate the clips
final_video = concatenate_videoclips([video_A, video_B, video_C, video_D, video_E])

# Export the final video
final_video.write_videofile("videos/final_video.mp4", codec="libx264")

