#####
# Generate video and add audio to it
#####

#%% 
from moviepy.editor import TextClip

def create_title_screen():
    title_clip = TextClip("COMPANY A Q4 Performance 2024", fontsize=50, color='black', bg_color='white', size=(1920, 1080), print_cmd=True)
    title_clip = title_clip.set_duration(2).set_position('center')
    title_clip.write_videofile('wip/video_segments/title.mp4', fps=24)

create_title_screen()

#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter

# Data Preparation
x = np.arange(3)
data = pd.DataFrame(
    [[3, 5, 7], 
     [0.4, 0.5, 0.8], 
     [4, 6, 2], 
     [0.1, 0.2, 0.9], 
     [1, 4, 9], 
     [0.4, 0.7, 0.2], 
     [4, 8, 3], 
     [0.8, 0.9, 0.1]]
).T

# Initialize the plots
def initialize_plots():
    fig, axes = plt.subplots(2, 2, figsize=(16, 9), constrained_layout=True)  # Match the resolution aspect ratio
    axes = axes.flatten()
    bar_artists = []
    line_artists = []
    twin_axes = []
    text_artists = []
    
    for i, ax in enumerate(axes):
        bars = ax.bar(x, np.zeros_like(x), color='skyblue', label='Bar Data')
        bar_artists.append(bars)
        
        twin_ax = ax.twinx()
        twin_axes.append(twin_ax)
        
        line, = twin_ax.plot(x, np.zeros_like(x), color='red', marker='o', linestyle='-', label='Line Data')
        line.set_visible(False)
        line_artists.append(line)
        
        # Set limits and labels
        ax.set_ylim(0, np.max(data.iloc[:, 2 * i]) * 1.1)
        twin_ax.set_ylim(0, np.max(data.iloc[:, 2 * i + 1]) * 1.1)
        ax.set_ylabel('Bar Data', color='black')
        twin_ax.set_ylabel('Line Data', color='red')

        # Add text annotation for each subplot
        text = ax.text(0.5, 0.1, "", transform=ax.transAxes, ha='center', va='center', 
                    fontsize=11, fontweight='bold', color='blue',
                    bbox=dict(facecolor='gray', alpha=0.5, edgecolor='none'))  # Opaque gray background
        text_artists.append(text)
    
    return fig, axes, bar_artists, line_artists, twin_axes, text_artists

# Animation update function
def update(frame):

    subplot_index = frame // 20
    local_frame = frame % 20

    if subplot_index >= len(bar_artists):
        return []

    d1 = data.iloc[:, 2 * subplot_index]
    d2 = data.iloc[:, 2 * subplot_index + 1]

    bars = bar_artists[subplot_index]
    line = line_artists[subplot_index]
    ax = axes[subplot_index]
    twin_ax = twin_axes[subplot_index]
    text = text_artists[subplot_index]
    
    growth_increment = np.max(d1) / 3
    frames_per_bar = np.ceil(d1 / growth_increment).astype(int)
    cumulative_sum = np.array(frames_per_bar.cumsum())
    bar_plot_frames = cumulative_sum[-1]

    if local_frame <= bar_plot_frames:
        ax.legend(loc='upper left')
        current_bar = np.argmax(cumulative_sum >= local_frame)
        new_height = min(d1[current_bar], growth_increment * (local_frame - (cumulative_sum[current_bar] - frames_per_bar[current_bar])))
        bars[current_bar].set_height(new_height)
        # Hide text while bars are growing
        text.set_text("")
    else:
        line.set_visible(True)
        completed_points = (local_frame - bar_plot_frames) // 3 + 1
        if completed_points <= len(d2):
            twin_ax.legend(loc='upper right')
            line.set_xdata(x[:completed_points])
            line.set_ydata(d2[:completed_points])
        else:
            line.set_xdata(x)
            line.set_ydata(d2)
        # Display text once bars are fully drawn
        if completed_points == len(d2):
            text.set_text("Op margin is 30%")

    return tuple(bar for bars in bar_artists for bar in bars) + tuple(line_artists)

# Animation Parameters
total_frames = 80  # Total frames for both title and subplot animations
fps = 30
interval = 100

# Create and Save the Animation
fig, axes, bar_artists, line_artists, twin_axes, text_artists = initialize_plots()
ani = FuncAnimation(fig, update, frames=total_frames, blit=True, repeat=False, interval=interval)
writer = FFMpegWriter(fps=fps, metadata=dict(artist='Me'), bitrate=1800)
ani.save('wip/video_segments/data.mp4', writer=writer)


#%%

from moviepy.editor import VideoFileClip, concatenate_videoclips
import PIL
PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

def merge_videos():
    # Load and resize the title clip to match the final resolution
    title_clip = VideoFileClip('wip/video_segments/title.mp4').resize((1920, 1080))
    
    # Load and resize the data clip to match the final resolution
    data_clip = VideoFileClip('wip/video_segments/data.mp4').resize((1920, 1080))

    # Concatenate the clips
    final_clip = concatenate_videoclips([title_clip, data_clip])

    # Save the final video
    final_clip.write_videofile('wip/video_segments/merged.mp4', fps=24)

# Call the function to merge videos
merge_videos()


#%%

from moviepy.editor import VideoFileClip, AudioFileClip
import os

def add_audio_to_video(video_path, audio_path, start_time, output_path):
    video_clip = VideoFileClip(video_path)
    video_duration = video_clip.duration
    audio_clip = AudioFileClip(audio_path)
    end_time = start_time + video_duration + 5
    
    # Extract the desired segment of the audio file
    audio_segment = audio_clip.subclip(start_time, end_time)
    
    # Set the audio segment to the video clip
    video_with_audio = video_clip.set_audio(audio_segment)
    
    # Export the final video with the selected audio segment
    video_with_audio.write_videofile(output_path, codec='libx264', audio_codec='aac')

# Example usage
video_path = 'wip/video_segments/merged.mp4'
audio_dir = 'audio'
audio_file = 'Recollections - Asher Fulero.mp3'
start_time = 10  # Start time in seconds
output_path = 'wip/video_segments/merged_audio.mp4'

# Call the function to add audio to video
audio_path = os.path.join(audio_dir, audio_file)
add_audio_to_video(video_path, audio_path, start_time, output_path)