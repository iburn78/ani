#%% 
from tools import *

ppt_file='삼성전자_2024_2Q_E_2024-09-30.pptx'
image_prefix = '슬라이드'

meta = Meta(ppt_file=ppt_file, image_prefix=image_prefix)

ppt_to_video(meta)
