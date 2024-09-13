#####
# Generate srt and add it
#####

#%%
from moviepy.editor import VideoFileClip

def create_srt_from_frames(video_path, subtitle_data, output_srt_path):
    # Load the video to get its duration
    video_clip = VideoFileClip(video_path)
    fps = video_clip.fps

    def frame_to_time(frame):
        # Convert frame number to time in SRT format (HH:MM:SS,MMM)
        seconds = frame / fps
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"

    with open(output_srt_path, 'w', encoding='utf-8') as srt_file:
        for index, (start_frame, end_frame, text) in enumerate(subtitle_data):
            start_time = frame_to_time(start_frame)
            end_time = frame_to_time(end_frame)
            
            srt_file.write(f"{index + 1}\n")
            srt_file.write(f"{start_time} --> {end_time}\n")
            srt_file.write(f"{text}\n\n")

subtitle_data = [
    (0, 48, "Introduction to the video 안녕하세요"),
    (70, 100, "Content Subtitles"),
    (120, 200, "Good buy"),
# should not be longer than the video duration
]

create_srt_from_frames('wip/video_segments/merged_audio.mp4', subtitle_data, 'wip/video_segments/final.srt')

#%%
import subprocess

def embed_subtitles(video_file, subtitle_file, output_file):
    try:
        # Command to embed subtitles using FFmpeg
        command = [
            'ffmpeg',
            '-y',  # Overwrite output file if it already exists
            '-i', video_file,
            '-i', subtitle_file,
            '-c', 'copy',
            '-c:s', 'mov_text',
            output_file
        ]
        
        # Run the command
        subprocess.run(command, check=True)
        
        print(f"Subtitles have been successfully embedded into {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
    except FileNotFoundError:
        print("FFmpeg is not installed or not found in your system's PATH.")

embed_subtitles('wip/video_segments/merged_audio.mp4', 'wip/video_segments/final.srt', 'wip/video_segments/merged_audio_subs.mp4')