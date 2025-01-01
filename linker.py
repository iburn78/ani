#%% 
from moviepy.editor import VideoFileClip, concatenate_videoclips
from datetime import datetime
import os

cd_ = os.path.dirname(os.path.abspath(__file__)) # .   
v_path = os.path.join(cd_, 'data/video/')
p_path = os.path.join(cd_, 'data/ppt/')
m_ptah = os.path.join(cd_, 'data/audio/')
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
# from moviepy.editor import VideoFileClip, AudioFileClip
# video = VideoFileClip(os.path.join(p_path, "it_logo_mv.mp4"))
# music = AudioFileClip(os.path.join(m_path, "Keys To Unravel - The Soundlings.mp3"))
# music = music.audio_fadeout(1)  # second fade-out duration
# music = music.volumex(0.5)  # reducing only seems working < 1
# video = video.set_audio(music)
# video.write_videofile(os.path.join(p_path, "output_video.mp4"), codec="libx264", audio_codec="aac")