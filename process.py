#%% ----------------------------------------------
# ✓ Setup
# ------------------------------------------------
from ppt2video.tools import *
from ani_tools import *

GCA ='../config/google_cloud.json'
CONF_FILE = '../config/config.json'
CLIENT_SECRETS_FILE = "../config/google_client.json"

# ------------------------------------------------
k_ppt_file = '배터리3사_K_2024-10-23_shorts.pptx'
k_title = '오늘 급등한 배터리 관련주들, 그간 주가 추이 비교해보면?'
k_desc = '''
#LG에너지솔루션 #삼성SDI #SK이노베이션 #Price
배터리3사 주가를 한번 비교해 보겠습니다. 단순 비교이지만, Macro를 봐야 하는지 Micro를 봐야 하는지 고민이 깊어집니다.
'''
k_keywords = ['Battery', 'Price', 'Macro', 'Micro']

e_ppt_file = k_ppt_file.replace('_K_', '_E_')
e_title, e_desc = translate_title_desc(k_title, k_desc, CONF_FILE)
print(e_title)
print(e_desc)

# e_title = ''
# e_desc = '''
# '''
# e_keywords = ['', '']

e_keywords = k_keywords

#%% ----------------------------------------------
# ✓ Generate Korean Video with Voice
# ------------------------------------------------
k_meta = Meta(ppt_file=k_ppt_file, image_prefix='슬라이드', google_application_credentials=GCA, lang='K',
    # fade_after_slide=[0, 1, 3, 4, 5, 6],
    # convert_slides_upto_slide_no=0, 
    target_slide_for_video = [2, ],
    video_file_path = ['ani.mp4', ], 
    video_height_scale = [0.45, ], 
    video_location = [(50, 260), ], # list of (x,y)
    video_interrupt = True, 
    )
ppt_to_video(k_meta)

#%% ----------------------------------------------
# ✓ Translate to English and generate video
# ------------------------------------------------
e_meta = Meta(
    ppt_file=e_ppt_file, image_prefix='슬라이드', google_application_credentials=GCA, lang='E', 
    convert_slides_upto_slide_no=0, 
    # fade_after_slide=[0, 1, 3, 4, 5, 6],
    speaking_rate_EN=1.10, 
    target_slide_for_video = [2, ],
    video_file_path = ['ani.mp4', ], 
    video_height_scale = [0.45, ], 
    video_location = [(50, 260), ], # list of (x,y)
    video_interrupt = True, 
    )
num = gen_Eng_notes_from_Korean(e_meta, CONF_FILE)
#%% 
# if needed modify the script here.
#%% 
timepoints = ppt_tts(e_meta, num)
# video_from_ppt_and_voice(e_meta, timepoints)
composite_video_from_ppt_and_voice(e_meta, timepoints)

#%% ----------------------------------------------
# ✓ Upload Korean 
# ------------------------------------------------
# thumbnail_file = k_ppt_file.replace('.pptx', '.PNG')
thumbnail_file = None
upload_video(k_meta, k_title, k_desc, k_keywords, thumbnail_file=thumbnail_file, client_secrets_file=CLIENT_SECRETS_FILE)

#%% ----------------------------------------------
# ✓ Upload English 
# ------------------------------------------------
# thumbnail_file = e_ppt_file.replace('.pptx', '.PNG')
thumbnail_file = None
upload_video(e_meta, e_title, e_desc, e_keywords, thumbnail_file=thumbnail_file, client_secrets_file=CLIENT_SECRETS_FILE)