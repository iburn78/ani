#%% 
from moviepy.editor import VideoFileClip, concatenate_videoclips
from datetime import datetime
import os

v_path = 'data/video/'
videos = sorted(os.listdir(v_path))[:3]
videos = [f for f in videos if os.path.isfile(os.path.join(v_path, f))][:3]

clips = []
clips.append(VideoFileClip(videos[0]))
clips.append(VideoFileClip(videos[1]).subclip(1, VideoFileClip(videos[1]).duration)) 
clips.append(VideoFileClip(videos[2]))

final_video = concatenate_videoclips(clips)
final_video_vol_ajusted = final_video.volumex(2)

final_output_path = os.path.join(v_path, f"final_video_+{datetime.now().strftime('%Y-%m-%d-%H-%M')}.mp4")
final_video_vol_ajusted.write_videofile(final_output_path, codec="libx264")



