#%% 
######
## Korean Text
######

from moviepy.editor import TextClip

# Example Korean text
korean_text = "한글"
# txt_clip = TextClip(korean_text, fontsize=50, font='Malgun-Gothic', color='Red')
txt_clip = TextClip(korean_text, fontsize=50, font='Noto Sans KR', color='Red')

# Set duration and position
txt_clip = txt_clip.set_duration(10).set_position('center')
txt_clip = txt_clip.set_fps(24)

# Export the clip
txt_clip.write_videofile("output_with_korean_text.mp4", codec="libx264")
