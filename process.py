#%% ----------------------------------------------
# ✓ Setup
# ------------------------------------------------
from ppt2video.tools import *
from ani_tools import *

GCA ='../config/google_cloud.json'
CONF_FILE = '../config/config.json'
CLIENT_SECRETS_FILE = "../config/google_client.json"

# ------------------------------------------------
k_ppt_file = '현대차_K_2024-10-24_shorts.pptx'
k_title = '인도에서 대박친 현대차, 실적 Review!'
k_desc = '''
#현대자동차 #인도IPO #PER
인도에서 최대 상장으로 대박친 현대자동차, 그간 실적 추이와 Value 측면에서 Review 해 보겠습니다.
'''
k_keywords = ['Hyundai Motors', 'India IPO', 'PER']

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
    fade_after_slide=[0, 1, 2, 3, 4, 5, 6],
    # convert_slides_upto_slide_no=0, 
    # target_slide_for_video = [2, ],
    # video_file_path = ['ani.mp4', ], 
    # video_height_scale = [0.45, ], 
    # video_location = [(50, 260), ], # list of (x,y)
    # video_interrupt = True, 
    )
ppt_to_video(k_meta)

#%% ----------------------------------------------
# ✓ Translate to English and generate video
# ------------------------------------------------
e_meta = Meta(
    ppt_file=e_ppt_file, image_prefix='슬라이드', google_application_credentials=GCA, lang='E', 
    convert_slides_upto_slide_no=0, 
    fade_after_slide=[0, 1, 2, 3, 4, 5, 6],
    speaking_rate_EN=1.10, 
    # target_slide_for_video = [2, ],
    # video_file_path = ['ani.mp4', ], 
    # video_height_scale = [0.45, ], 
    # video_location = [(50, 260), ], # list of (x,y)
    # video_interrupt = True, 
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