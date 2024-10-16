#%% ----------------------------------------------
# ✓ Setup
# ------------------------------------------------
from ppt2video.tools import *
from ani_tools import *

GCA ='../config/google_cloud.json'
CONF_FILE = '../config/config.json'
CLIENT_SECRETS_FILE = "../config/google_client.json"

# ------------------------------------------------
k_ppt_file = '배당분석_K_2024-10-15.pptx'
k_title = '국내 배당수익률 최고인 회사는? 지난 3년간 분석'
k_desc = '''
#배당수익률 #배당 #투자전략
2021, 2022, 2023년 배당수익률이 최고인 회사는 어디인지 알아보고, 이를 추종하는 전략이 유효할지 알아보겠습니다. 간단한 분석입니다.
'''
k_keywords = ['Dividend', 'Yield', 'Strategy']

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
    )
ppt_to_video(k_meta)

#%% ----------------------------------------------
# ✓ Translate to English and generate video
# ------------------------------------------------
e_meta = Meta(
    ppt_file=e_ppt_file, image_prefix='슬라이드', google_application_credentials=GCA, lang='E', 
    convert_slides_upto_slide_no=0, 
    fade_after_slide=[0, 1, 2, 3, 4, 5, 6],
    speaking_rate_EN=1.1, 
    )
num = gen_Eng_notes_from_Korean(e_meta, CONF_FILE)
#%% 
# if needed modify the script here.
#%% 
timepoints = ppt_tts(e_meta, num)
video_from_ppt_and_voice(e_meta, timepoints)

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