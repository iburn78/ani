#%% 
from moviepy.editor import VideoFileClip, concatenate_videoclips
from datetime import datetime
import os

v_path = 'data/video/'
videos = sorted([f for f in os.listdir(v_path) if os.path.isfile(os.path.join(v_path, f))])

clips = []
clips.append(VideoFileClip(os.path.join(v_path, videos[0])).subclip(0, 74))
clips.append(VideoFileClip(os.path.join(v_path, videos[1])))
# clips.append(VideoFileClip(os.path.join(v_path, videos[1])).subclip(0, 23))
# clips.append(VideoFileClip(os.path.join(v_path, videos[2])).subclip(0, 41))
# clips.append(VideoFileClip(os.path.join(v_path, videos[3])).subclip(1.5, 35))
# clips.append(VideoFileClip(os.path.join(v_path, videos[0])).subclip(1, VideoFileClip(videos[1]).duration)) 

final_video = concatenate_videoclips(clips)

final_output_path = os.path.join(v_path, f"final_video_+{datetime.now().strftime('%Y-%m-%d-%H-%M')}.mp4")
final_video.write_videofile(final_output_path, codec="libx264")


#%% 
from moviepy.editor import VideoFileClip, AudioFileClip

# Load the video clip
video = VideoFileClip("data/ppt/it_logo_mv.mp4")
l=2
video = video.subclip(0, 2.3)

# Load the music/audio clip
music = AudioFileClip("data/ppt/Keys To Unravel - The Soundlings.mp3")

# Trim the music to the length of the video (2 seconds)
music = music.subclip(0, l)

# Apply a fade-out effect to the music (starts fading at 1.5 seconds, ends at 2.0 seconds)
# music = music.volumex(0.5).set_start(1.9)
music = music.audio_fadeout(1)  # second fade-out duration
music = music.volumex(0.5)

# Set the modified audio to the video
video = video.set_audio(music)

# Export the final video
video.write_videofile("data/ppt/output_video.mp4", codec="libx264", audio_codec="aac")