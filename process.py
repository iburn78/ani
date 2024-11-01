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
k_ppt_file = 'Google_K_2024-11-01_shorts'
k_title = '13초컷 - 삼성바이오로직스 3분기 실적!'
k_title = 'Google - AI 경쟁에서 밀린다던데, 아직도 잘 나가나?'
k_desc = '''
#Google #Aphabet #AI
Google이 요즘 반독점 분할 소송이네, AI경쟁에서 뒤쳐지네 등등 말이 많죠. 그래도 글로벌 최대 부잣집인데, 3분기 실적과 함께 현재 이슈 정리해 보겠습니다.
'''
k_keywords = ['Google', '2024 3Q', 'Quaterly Performance']

e_ppt_file = k_ppt_file.replace('_K_', '_E_')
e_ppt_file = (e_ppt_file if e_ppt_file.endswith('.pptx') else e_ppt_file + '.pptx')
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
k_meta = Meta(ppt_file=k_ppt_file, google_application_credentials=GCA, lang='K',
    # slide_break=0.1, 
    # line_break=0.1,
    # speaking_rate_KR=1.3, 
    fade_after_slide=[0, 2, 3, 5, 6, 7], 
    # convert_slides_upto_slide_no=0, 
    # target_slide_for_video = [5, ],
    # video_file_path = ['ani.mp4', ], 
    # video_height_scale = [0.50, ], 
    # video_location = [(50, 260), ], # list of (x,y)
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
    fade_after_slide=[0, 2, 3, 5, 6, 7], 
    # speaking_rate_EN=1.3, 
    # target_slide_for_video = [5, ],
    # video_file_path = ['ani.mp4', ], 
    # video_height_scale = [0.50, ], 
    # video_location = [(50, 260), ], # list of (x,y)
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
with open(YOUTUBE_CONF, 'r') as json_file:
    config = json.load(json_file)
thumbnail_file = None
# thumbnail_file = e_ppt_file.replace('.pptx', '.PNG')
playlist_id = None
# playlist_id = config["it_quick_update_playlist_id"]
upload_video(e_meta, e_title, e_desc, e_keywords, thumbnail_file=thumbnail_file, client_secrets_file=CLIENT_SECRETS_FILE, playlist_id=playlist_id)