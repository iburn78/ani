#####
# Generate vioce from srt file and add it to video
#####

#%% 
import re

def extract_subtitles_from_srt(srt_file):
    """
    Extracts subtitles and their timestamps from an SRT file.
    Returns a list of tuples (start_time, end_time, text).
    """
    with open(srt_file, 'r', encoding='utf-8') as file:
        srt_content = file.read()
    
    # Regular expression to match subtitles with timestamps
    subtitles = re.findall(r'(\d{2}:\d{2}:\d{2}.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}.\d{3})\s*\n(.*?)\n\n', srt_content, re.DOTALL)
    
    return [(start, end, text.replace('\n', ' ')) for start, end, text in subtitles]



from gtts import gTTS
import os

def generate_speech_for_subtitles(subtitles, output_dir):
    """
    Generates speech audio files for each subtitle segment and saves them to the output directory.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for i, (start_time, end_time, text) in enumerate(subtitles):
        tts = gTTS(text=text, lang='en')  # Adjust 'lang' if needed
        audio_file = os.path.join(output_dir, f'segment_{i}.mp3')
        tts.save(audio_file)
        print(f"Generated speech for segment {i} saved to {audio_file}")



from pydub import AudioSegment

def concatenate_audio_segments(subtitles, audio_dir, output_file):
    """
    Concatenates audio segments based on subtitle timings into a single audio file.
    """
    final_audio = AudioSegment.empty()
    
    for i, (start_time, end_time, _) in enumerate(subtitles):
        audio_file = os.path.join(audio_dir, f'segment_{i}.mp3')
        segment_audio = AudioSegment.from_mp3(audio_file)
        final_audio += segment_audio
    
    final_audio.export(output_file, format='mp3')
    print(f"Combined audio saved to {output_file}")


# File paths
srt_file_path = 'wip/video_segments/final.srt'
audio_dir = 'wip/audio_segments'
output_audio_path = os.path.join(audio_dir, 'speech.mp3')

# Extract subtitles
subtitles = extract_subtitles_from_srt(srt_file_path)

# Generate speech for each subtitle segment
generate_speech_for_subtitles(subtitles, audio_dir)

# Combine audio segments into a final audio file
concatenate_audio_segments(subtitles, audio_dir, output_audio_path)


#%% 

from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

video_path = 'wip/video_segments/merged_audio_subs.mp4'
audio_path = 'wip/audio_segments/speech.mp3'
output_path = 'wip/final.mp4'

# Load video and new audio
video_clip = VideoFileClip(video_path)
new_audio_clip = AudioFileClip(audio_path)

# Extract existing audio
existing_audio_clip = video_clip.audio

# Combine existing and new audio
combined_audio = CompositeAudioClip([existing_audio_clip, new_audio_clip])

# Set combined audio to video
video_with_combined_audio = video_clip.set_audio(combined_audio)

# Save the video with the combined audio
video_with_combined_audio.write_videofile(output_path, codec='libx264', audio_codec='aac')
