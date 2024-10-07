#%% 
from ppt2video.tools import *

ppt_file='삼성전자_2024_2Q_E_2024-09-30.pptx'
image_prefix = '슬라이드'
voice_enabled = False

meta = Meta(ppt_file=ppt_file, image_prefix=image_prefix, voice_enabled=False)

ppt_to_video(meta)
#%% 

from ppt2video.tools import *

ppt_file='삼성전자_2024_2Q_K_2024-09-22.pptx'
image_prefix = '슬라이드'
lang = 'E'
gca ='../config/google_cloud.json'
meta = Meta(ppt_file=ppt_file, image_prefix=image_prefix, lang=lang, google_application_credentials=gca)

ppt_to_video(meta)