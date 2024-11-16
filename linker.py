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
