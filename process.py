#%% ----------------------------------------------
# ✓ Setup
# ------------------------------------------------
from ppt2video.tools import *
from ani_tools import *

GCA ='../config/google_cloud.json'
CONF_FILE = '../config/config.json'
CLIENT_SECRETS_FILE = "../config/google_client.json"
YOUTUBE_CONF = '../config/youtube_conf.json'

# ------------------------------------------------
k_ppt_file = '트럼프당선후지수변화_K_2024-11-08_shorts'
k_title = '13초컷 - 삼성바이오로직스 3분기 실적!'
k_title = '트럼프 당선 직후 미국과 한국의 주식시장 방향 변화 분석, 기타 주요국은?'
k_desc = '''
#트럼프 #주식시장 #영향
트럼프 당선 직후 미국은 시장이 사상 최고가를 경신중이라는데, 우리나라와 비교하면 어떠한지, 그리고 일본, 홍콩, 영국등 주요국은 어떠했는지 살펴보겠습니다.
'''
k_keywords = ['Trump', 'Stock Index', 'US vs Korea', 'Quaterly Performance']

e_ppt_file = k_ppt_file.replace('_K_', '_E_')
e_ppt_file = (e_ppt_file if e_ppt_file.endswith('.pptx') else e_ppt_file + '.pptx')
e_title, e_desc = translate_title_desc(k_title, k_desc, CONF_FILE)
# titles should not be too long
#%%
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
k_meta = Meta(ppt_file=k_ppt_file, google_application_credentials=GCA, lang='K',
    # slide_break=0.1, 
    # line_break=0.1,
    # speaking_rate_KR=1.3, 
    fade_after_slide=[0, 2, 4, 6], 
    # convert_slides_upto_slide_no=0, 
    target_slide_for_video = [1, 3, 5],
    video_file_path = ['index_us.mp4', 'index_other.mp4', 'index_KR.mp4' ], 
    video_height_scale = [0.45, 0.45, 0.45], 
    video_location = [(40, 260), (40, 260), (40, 260)], # list of (x,y)
    # video_interrupt = True, 
    )
ppt_to_video(k_meta)

#%% ----------------------------------------------
# ✓ Translate to English and generate video
# ------------------------------------------------
e_meta = Meta(
    ppt_file=e_ppt_file, google_application_credentials=GCA, lang='E', 
    # slide_break=0.1, 
    # line_break=0.1,
    # convert_slides_upto_slide_no=0, 
    fade_after_slide=[0, 2, 4, 6], 
    # speaking_rate_EN=1.3, 
    target_slide_for_video = [1, 3, 5],
    video_file_path = ['index_us.mp4', 'index_other.mp4', 'index_KR.mp4' ], 
    video_height_scale = [0.45, 0.45, 0.45], 
    video_location = [(40, 260), (40, 260), (40, 260)], # list of (x,y)
    # video_interrupt = True, 
    )
num = gen_Eng_notes_from_Korean(e_meta, CONF_FILE)
#%% 
# if needed modify the script here.
#%% 
timepoints = ppt_tts(e_meta, num)
save_ppt_as_images(e_meta)
# video_from_ppt_and_voice(e_meta, timepoints)
composite_video_from_ppt_and_voice(e_meta, timepoints)

#%% ----------------------------------------------
# ✓ Upload Korean 
# ------------------------------------------------
with open(YOUTUBE_CONF, 'r') as json_file:
    config = json.load(json_file)
thumbnail_file = None
# thumbnail_file = k_ppt_file.replace('.pptx', '.PNG')
playlist_id = None
# playlist_id = config["qp_quick_update_playlist_id"]
upload_video(k_meta, k_title, k_desc, k_keywords, thumbnail_file=thumbnail_file, client_secrets_file=CLIENT_SECRETS_FILE, playlist_id=playlist_id)

#%% ----------------------------------------------
# ✓ Upload English 
# ------------------------------------------------
#%% 
with open(YOUTUBE_CONF, 'r') as json_file:
    config = json.load(json_file)
thumbnail_file = None
# thumbnail_file = e_ppt_file.replace('.pptx', '.PNG')
playlist_id = None
# playlist_id = config["it_quick_update_playlist_id"]
upload_video(e_meta, e_title, e_desc, e_keywords, thumbnail_file=thumbnail_file, client_secrets_file=CLIENT_SECRETS_FILE, playlist_id=playlist_id)