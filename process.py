#%% ----------------------------------------------
# ✓ Setup
# ------------------------------------------------
from ppt2video.tools import *
from ani_tools import *

GCA ='../config/google_cloud.json'
CONF_FILE = '../config/config.json'
CLIENT_SECRETS_FILE = "../config/google_client.json"

# ------------------------------------------------
k_ppt_file = 'SK하이닉스_K_2024-10-17.pptx'
k_title = 'SK하이닉스, 삼성전자와 비교분석한다면 - 고평가 vs 저평가?' 
k_desc = '''
#SK하이닉스 #삼성전자 #비교분석 #고평가 #저평가 #PER
SK하이닉스와 삼성전자 단순비교는 어렵겠지만, 양사가 HBM이슈에 동시에 큰 영향을 받고 있으니 비교해 보았습니다. 고평가 일까요 저평가 일까요?
'''
k_keywords = ['SK Hynix', 'Samsung Electronics', 'Strategy']

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
    # fade_after_slide=[0, 1, 2, 3, 4, 5, 6],
    )
ppt_to_video(k_meta)

#%% ----------------------------------------------
# ✓ Translate to English and generate video
# ------------------------------------------------
e_meta = Meta(
    ppt_file=e_ppt_file, image_prefix='슬라이드', google_application_credentials=GCA, lang='E', 
    convert_slides_upto_slide_no=0, 
    fade_after_slide=[0, 1, 2, 4, 8, 10, 11, 13, 14, 15],
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
thumbnail_file = k_ppt_file.replace('.pptx', '.PNG')
# thumbnail_file = None
upload_video(k_meta, k_title, k_desc, k_keywords, thumbnail_file=thumbnail_file, client_secrets_file=CLIENT_SECRETS_FILE)

#%% ----------------------------------------------
# ✓ Upload English 
# ------------------------------------------------
thumbnail_file = e_ppt_file.replace('.pptx', '.PNG')
# thumbnail_file = None
upload_video(e_meta, e_title, e_desc, e_keywords, thumbnail_file=thumbnail_file, client_secrets_file=CLIENT_SECRETS_FILE)