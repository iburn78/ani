#%%
from moviepy.editor import TextClip, concatenate_videoclips
from moviepy.video.fx.all import fadein, fadeout

# Create Text Clips
# font = "Malgun-Gothic"  # only this works with moviepy
font = "Noto Sans KR"  # only this works with moviepy
        
def create_text_clip(text, duration):
    return TextClip(text, font=font, fontsize=24, color='white', bg_color='black', size=(640, 480)) \
        .set_duration(duration) \
        .set_pos('center')

# Define Texts
texts = [
    "첫 번째 단락입니다.",
    "두 번째 단락입니다.",
    "세 번째 단락입니다.",
    "네 번째 단락입니다."
]

# Create Clips
clips = [create_text_clip(text, 10) for text in texts]

# Combine Clips
video = concatenate_videoclips(clips, method="compose")

# Add fade effects
video = video.fx(fadein, 1).fx(fadeout, 1)

# Write to file
video.write_videofile("output.mp4", fps=24)
