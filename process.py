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
k_ppt_file = '트리플약세_K_2024-11-15_shorts'
# k_title = '13초컷 - 삼성바이오로직스 3분기 실적!'
k_title = '한국은 현재 트리플 약세... 얼마나 지속될까?'
k_desc = '''
#트리플강세 #트리플약세 #주식 #채권 #환율 #Cycle #트럼프 #양극화
트럼프 당선 이후, 미국은 트리플 강세를 보이고, 한국은 트리플 약세를 보이고 있습니다. 극단적인 양극화가 순식간에 발생해 버렸습니다. 한번 살펴보겠습니다.
'''
k_keywords = ['Triple strength', 'Triple weakness', 'Trump', 'Quaterly Performance']

e_ppt_file = k_ppt_file.replace('_K_', '_E_')
e_ppt_file = (e_ppt_file if e_ppt_file.endswith('.pptx') else e_ppt_file + '.pptx')
e_title, e_desc = translate_title_desc(k_title, k_desc, CONF_FILE)
# titles should not be too long
print(e_title)
print(e_desc)
#%%
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
    fade_after_slide=[0, 1, 2, 3, 4, 5, 6, 7],
    # convert_slides_upto_slide_no=0, 
    # target_slide_for_video = [1, 3, 5],
    # video_file_path = ['index_us.mp4', 'index_other.mp4', 'index_KR.mp4' ], 
    # video_height_scale = [0.45, 0.45, 0.45], 
    # video_location = [(40, 260), (40, 260), (40, 260)], # list of (x,y)
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
    fade_after_slide=[0, 1, 2, 3, 4, 5, 6, 7],
    # speaking_rate_EN=1.3, 
    # target_slide_for_video = [1, 3, 5],
    # video_file_path = ['index_us.mp4', 'index_other.mp4', 'index_KR.mp4' ], 
    # video_height_scale = [0.45, 0.45, 0.45], 
    # video_location = [(40, 260), (40, 260), (40, 260)], # list of (x,y)
    # video_interrupt = True, 
    )
num = gen_Eng_notes_from_Korean(e_meta, CONF_FILE)
#%% 
# if needed modify the script here.
#%% 
timepoints = ppt_tts(e_meta, num)
# save_ppt_as_images(e_meta)
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