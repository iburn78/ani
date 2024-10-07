#%% ----------------------------------------------
# ✓ Setup
# ------------------------------------------------
from ppt2video.tools import *
from ani_tools import *

GCA ='../config/google_cloud.json'
CONF_FILE = '../config/config.json'
CLIENT_SECRETS_FILE = "../config/google_client.json"

# ------------------------------------------------
k_ppt_file = '.pptx'
k_title = ''
k_desc = '''
'''
k_keywords = ['', '']

e_title, e_desc = translate_title_desc(k_title, k_desc, CONF_FILE)
print(e_title)
print(e_desc)

# e_title = ''
# e_desc = '''
# '''
e_keywords = ['', '']

#%% ----------------------------------------------
# ✓ Generate Korean Video with Voice
# ------------------------------------------------
k_meta = Meta(ppt_file=k_ppt_file, image_prefix='슬라이드', google_application_credentials=GCA, lang='K')
ppt_to_video(k_meta)

#%% ----------------------------------------------
# ✓ Translate to English and generate video
# ------------------------------------------------
e_ppt_file = k_ppt_file.replace('_K_', '_E_')
e_meta = Meta(ppt_file=e_ppt_file, image_prefix='슬라이드', google_application_credentials=GCA, lang='E')

num = gen_Eng_notes_from_Korean(e_meta, CONF_FILE)
timepoints = ppt_tts(e_meta, num)
video_from_ppt_and_voice(e_meta, timepoints)

#%% ----------------------------------------------
# ✓ Upload Korean 
# ------------------------------------------------
upload_video(k_meta, k_title, k_desc, k_keywords, CLIENT_SECRETS_FILE)

#%% ----------------------------------------------
# ✓ Upload English 
# ------------------------------------------------
upload_video(e_meta, e_title, e_desc, e_keywords, CLIENT_SECRETS_FILE)