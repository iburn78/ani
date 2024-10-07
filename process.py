#%% ----------------------------------------------
# Setup
# ------------------------------------------------

k_ppt_file = 'ForeignOwnership_2024-10-07_K_shorts.pptx'
k_title = ''
k_desc = '''
'''
k_keywords = ['', '']
e_keywords = ['', '']

#%% ----------------------------------------------
# Generate Korean Video with Voice
# ------------------------------------------------
from ppt2video.tools import *
from ani_tools import *
image_prefix = '슬라이드'
gca ='../config/google_cloud.json'
k_meta = Meta(ppt_file=k_ppt_file, image_prefix=image_prefix, google_application_credentials=gca, lang='K')
ppt_to_video(k_meta)



#%% ----------------------------------------------
# Translate to English and generate video
# ------------------------------------------------
e_ppt_file = k_ppt_file.replace('_K_', '_E_')
e_meta = Meta(ppt_file=e_ppt_file, image_prefix=image_prefix, google_application_credentials=gca, lang='E')
num = gen_Eng_notes_from_Korean(e_meta)
timepoints = ppt_tts(e_meta, num)
video_from_ppt_and_voice(e_meta, timepoints)



#%% ----------------------------------------------
# Upload
# ------------------------------------------------
# Step1: upload Korean version to youtube
upload_video(k_meta, k_title, k_desc, k_keywords)


#%% ----------------------------------------------
# Step2: check e_title, e_desc
e_title, e_desc = translate_title_desc(k_title, k_desc)
print(e_title, e_desc)

# e_title = ''
# e_desc = '''
# '''


#%% ----------------------------------------------
# Step3: upload Eng version to youtube
upload_video(e_meta, e_title, e_desc, e_keywords)