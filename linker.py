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


#%% 
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import os
import json

meta_file = 'data/ppt/meta.json'
voice_meta_file = 'data/voice/voice_meta.json'
output_file_path = 'data/video/'

with open(voice_meta_file, 'r', encoding='utf-8') as json_file:
    timepoints = json.load(json_file)

with open(meta_file, 'r', encoding='utf-8') as json_file:
    meta = json.load(json_file)

images_folder = os.path.join(meta['ppt_path'], meta['ppt_file'].replace('.pptx',''))
output_file = os.path.join(output_file_path, meta['ppt_file'].replace('.pptx', '.mp4'))
def create_video_from_ppt_and_audio(images_folder, timepoints, output_file, fps=24):
    video_with_audios = []

    for audio_file, slide_times in timepoints.items():
        audio_clip = AudioFileClip(audio_file)

        video_clips = []
        for i in range(len(slide_times) - 1):
            start_time = slide_times[i][1]  # Get the start time for the slide
            end_time = slide_times[i + 1][1]  # Get the end time for the next slide
            slide_number = slide_times[i][0]

            # Construct the image filename
            slide_image_filename = f'슬라이드{slide_number}.PNG'
            slide_image_path = os.path.join(images_folder, slide_image_filename)

            # Load the slide image
            slide_clip = ImageClip(slide_image_path).set_duration(end_time - start_time).set_start(start_time)
            video_clips.append(slide_clip)

        # Concatenate video clips for the current audio
        video_with_audio = concatenate_videoclips(video_clips)
        video_with_audio = video_with_audio.set_audio(audio_clip).volumex(2)
        video_with_audios.append(video_with_audio)

    # Concatenate all videos into one final video
    final_video = concatenate_videoclips(video_with_audios)

    # Set fps for the final video
    final_video.fps = fps
    
    # final_video.write_videofile(output_file, codec="libx264")
    final_video.write_videofile(
    output_file,
    codec="libx264",
)

# Run the video creation function
create_video_from_ppt_and_audio(images_folder, timepoints, output_file)