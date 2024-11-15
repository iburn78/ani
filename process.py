#%% ---------------------------------------------------------------------------------------
# ✓ Setup
# ------------------------------------------------
from ppt2video.tools import *
from ani_tools import *

GCA ='../config/google_cloud.json'
CONF_FILE = '../config/config.json'
CLIENT_SECRETS_FILE = "../config/google_client.json"
YOUTUBE_CONF = '../config/youtube_conf.json'

var_setting_block = '''
k_ppt_file = k_ppt_file.replace('.pptx', '')+'.pptx'
e_ppt_file = k_ppt_file.replace('_K_', '_E_')
thumbnail_file_k = None
thumbnail_file_e = None
playlist_id_qp = None
playlist_id_it = None
speaking_rate_KR = 1.2 # Korean
speaking_rate_EN = 1.1 # English 
speaking_rate_param = {}

if type_of_video == 0: 
    thumbnail_file_k = os.path.join(f"{k_ppt_file.replace('.pptx', '')}", "slide0.png")
    thumbnail_file_e = os.path.join(f"{e_ppt_file.replace('.pptx', '')}", "slide0.png")

if type_of_video == 2: 
    k_title = '13초컷 - ' + k_title
    with open(YOUTUBE_CONF, 'r') as json_file:
        config = json.load(json_file)
        playlist_id_qp = config["qp_quick_update_playlist_id"]
        playlist_id_it = config["it_quick_update_playlist_id"]
    speaking_rate_param = {
        'slide_break': 0.1, 
        'line_break': 0.1,
    }
'''

# ------------------------------------------------
# 0: wide videos
# 1: vertical shorts
# 2: 13 sec series
# ------------------------------------------------
type_of_video = 1 

k_ppt_file = '트리플약세_K_2024-11-15_shorts'
k_title = '한국은 현재 트리플 약세... 얼마나 지속될까?'
k_desc = '''
#트리플강세 #트리플약세 #주식 #채권 #환율 #Cycle #트럼프 #양극화
트럼프 당선 이후, 미국은 트리플 강세를 보이고, 한국은 트리플 약세를 보이고 있습니다. 극단적인 양극화가 순식간에 발생해 버렸습니다. 한번 살펴보겠습니다.
'''
k_keywords = ['Triple strength', 'Triple weakness', 'Trump', 'Quaterly Performance']
fade_after_slide=[0, 1, 2, 3, 4, 5, 6, 7],

# ------------------------------------------------
video_param = {
    "target_slide_for_video": [1, 3, 5],
    "video_file_path": ['index_us.mp4', 'index_other.mp4', 'index_KR.mp4'],
    "video_height_scale": [0.45, 0.45, 0.45],
    "video_location": [(40, 260), (40, 260), (40, 260)],  # list of (x, y)
    "video_interrupt": True,
}
video_param = {}

# ------------------------------------------------
# common variable settings
# ------------------------------------------------

k_ppt_file = k_ppt_file.replace('.pptx', '')+'.pptx'
e_ppt_file = k_ppt_file.replace('_K_', '_E_')
thumbnail_file_k = None
thumbnail_file_e = None
playlist_id_qp = None
playlist_id_it = None
speaking_rate_KR = 1.2 # Korean
speaking_rate_EN = 1.1 # English 
speaking_rate_param = {}

if type_of_video == 0: 
    thumbnail_file_k = os.path.join(f"{k_ppt_file.replace('.pptx', '')}", "slide0.png")
    thumbnail_file_e = os.path.join(f"{e_ppt_file.replace('.pptx', '')}", "slide0.png")

if type_of_video == 2: 
    k_title = '13초컷 - ' + k_title
    with open(YOUTUBE_CONF, 'r') as json_file:
        config = json.load(json_file)
        playlist_id_qp = config["qp_quick_update_playlist_id"]
        playlist_id_it = config["it_quick_update_playlist_id"]
    speaking_rate_param = {
        'slide_break': 0.1, 
        'line_break': 0.1,
    }

#%% ----------------------------------------------
# ✓ Generate Korean Video with Voice
# ------------------------------------------------
k_meta = Meta(ppt_file=k_ppt_file, google_application_credentials=GCA, lang='K',
    fade_after_slide=fade_after_slide,
    speaking_rate_KR=speaking_rate_KR, 
    **speaking_rate_param,
    **video_param,
    )
# ppt_to_video(k_meta)
save_ppt_as_images(k_meta)
num = ppt_to_text(k_meta)

#%% ----------------------------------------------
# if needed modify the script here.
# ------------------------------------------------

timepoints = ppt_tts(k_meta, num)
composite_video_from_ppt_and_voice(k_meta, timepoints)

#%% ----------------------------------------------
# ✓ Upload Korean 
# ------------------------------------------------
upload_video(k_meta, k_title, k_desc, k_keywords, thumbnail_file=thumbnail_file_k, client_secrets_file=CLIENT_SECRETS_FILE, playlist_id=playlist_id_qp)









#%% ---------------------------------------------------------------------------------------
# ✓ Upload English 
# ------------------------------------------------
e_meta = Meta(
    ppt_file=e_ppt_file, google_application_credentials=GCA, lang='E', 
    fade_after_slide=fade_after_slide,
    speaking_rate_EN=speaking_rate_EN, 
    **speaking_rate_param,
    **video_param,
    )
num = gen_Eng_notes_from_Korean(e_meta, CONF_FILE)
save_ppt_as_images(e_meta)

#%% ----------------------------------------------
# if needed modify the script here.
# ------------------------------------------------

#%% ----------------------------------------------
timepoints = ppt_tts(e_meta, num)
composite_video_from_ppt_and_voice(e_meta, timepoints)

#%% ----------------------------------------------
e_title, e_desc = translate_title_desc(k_title, k_desc, CONF_FILE)
e_keywords = k_keywords
print(e_title)
print(e_desc)
# e_title = ''
# e_desc = '''
# '''

#%% ----------------------------------------------
upload_video(e_meta, e_title, e_desc, e_keywords, thumbnail_file=thumbnail_file_e, client_secrets_file=CLIENT_SECRETS_FILE, playlist_id=playlist_id_it)