#%% 
from tools import *

max_size = 4500
slide_break = 2 
line_break = 0.7
fps = 24

meta = {}
meta['ppt_file'] = '삼성전자_2024_2Q_E_2024-09-30.pptx'
meta['lang'] = 'E' 
meta['wave'] = False
meta['ppt_path'] = 'data/ppt/'
meta['voice_path'] = 'data/voice/'
meta['image_prefix'] = '슬라이드'

meta = ppt_to_text(meta, max_size=max_size, slide_break=slide_break, line_break=line_break)
timepoints = ppt_tts(meta)
create_video_from_ppt_and_voice(meta, timepoints=timepoints, fps=fps)

