#%% ----------------------------------------------
# ✓ Setup
# ------------------------------------------------
from ppt2video.tools import *
from ani_tools import *

GCA ='../config/google_cloud.json'
CONF_FILE = '../config/config.json'
CLIENT_SECRETS_FILE = "../config/google_client.json"

# ------------------------------------------------
k_ppt_file = 'SK하이닉스_K_2024-10-25_shorts.pptx'
k_title = 'SK하이닉스 3분기 실적 발표 - Earning Surprise!!'
k_desc = '''
#SK하이닉스 #삼성전자 #어닝서프라이즈
SK하이닉스의 3분기 실적 발표가 있었습니다. 최대 호황이라고 해도 과언이 아닌데, 삼성전자와 극명히 비교됩니다. 같이 살펴보시죠!
'''
k_keywords = ['SK Hynix', '2024 3Q', 'Quaterly Performance']

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
    target_slide_for_video = [5, ],
    video_file_path = ['ani.mp4', ], 
    video_height_scale = [0.50, ], 
    video_location = [(50, 260), ], # list of (x,y)
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
    speaking_rate_EN=1.15, 
    target_slide_for_video = [5, ],
    video_file_path = ['ani.mp4', ], 
    video_height_scale = [0.50, ], 
    video_location = [(50, 260), ], # list of (x,y)
    # video_interrupt = True, 
    )
# num = gen_Eng_notes_from_Korean(e_meta, CONF_FILE)
#%% 
# if needed modify the script here.
#%% 
num=1
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