#%% ================================================================================
#   ================================================================================
from ani_tools import *
from ist_tools import get_notes, get_desc
import shutil

# ------------------------------------------------
# 0: wide videos
# 1: vertical shorts
# 2: 13 sec series
# ------------------------------------------------
k_ppt_file = '한국경제증발량_K_2024-12-10_shorts'
no_fade = []
video_param = {}
# video_param = {
#     "target_slide_for_video": [1, 4, 6], # slide starts from 0
#     "video_file_path": ['index_KR.mp4', 'index_us.mp4', 'index_other.mp4'],
#     "video_height_scale": [0.50, 0.50, 0.50],
#     "video_location": [(30, 250), (30, 250), (30, 250)],  # list of (x, y)
#     "video_interrupt": False,
# }

type_of_video = check_filename(k_ppt_file)
###################### VID WORKING DIR Deleted.
prep_K_file = os.path.join(VID_WORKING_DIR, k_ppt_file.replace('.pptx','')+'.pptx')
notes = get_notes(prep_K_file)
[title, tags, desc] = get_desc(notes, 'K', CONF_FILE)
k_title = title
k_desc = tags+ '\n' +desc
k_keywords = list(tags.replace('#','').strip().split(' '))
# ------------------------------------------------
# Check title, desc and keywords
# ------------------------------------------------
print(k_title)
print(k_desc)
print(k_keywords)

# k_title = ""
# k_desc = '''
# '''
# k_keywords = []

# ------------------------------------------------
# common variable settings
# ------------------------------------------------
fade_after_slide=list(range(30))
fade_after_slide = [x for x in fade_after_slide if x not in no_fade]
k_ppt_file = k_ppt_file.replace('.pptx', '')+'.pptx'
e_ppt_file = k_ppt_file.replace('_K_', '_E_')
thumbnail_file_k = None
thumbnail_file_e = None
playlist_id_qp = None
playlist_id_it = None
speaking_rate_KR = 1.2 # Korean
speaking_rate_EN = 1.2 # English 
speaking_rate_param = {
}

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

#%% ================================================================================
#   ================================================================================
# ✓ Generate Korean Video with Voice
# ------------------------------------------------
k_meta = Meta(ppt_file=k_ppt_file, google_application_credentials=GOOGLE_CLOUD, lang='K',
    fade_after_slide=fade_after_slide,
    speaking_rate_KR=speaking_rate_KR, 
    **speaking_rate_param,
    **video_param,
    )
save_ppt_as_images(k_meta)
num = ppt_to_text(k_meta)
timepoints, total_duration = ppt_tts(k_meta, num)
composite_video_from_ppt_and_voice(k_meta, timepoints)

#%% ================================================================================
#   ================================================================================
# ✓ Upload Korean 
# ------------------------------------------------
k_id = upload_video(k_meta, k_title, k_desc, k_keywords, thumbnail_file=thumbnail_file_k, client_secrets_file=GOOGLE_CLIENT, playlist_id=playlist_id_qp)

#%% ================================================================================
#   ================================================================================
# ✓ If successful, append to youtube log 
# ------------------------------------------------
append_to_youtube_log(k_ppt_file, k_title, k_desc, k_keywords, k_id, type_of_video)














#%% ================================================================================
#   ================================================================================
# ✓ File to work-on
# ------------------------------------------------
prep_E_file = prep_K_file.replace('_K_', '_E_')
if not os.path.exists(prep_E_file):
    shutil.copy(prep_K_file, prep_E_file)

#%% ================================================================================
#   ================================================================================
# ✓ Upload English 
# ------------------------------------------------
e_meta = Meta(
    ppt_file=e_ppt_file, google_application_credentials=GOOGLE_CLOUD, lang='E', 
    fade_after_slide=fade_after_slide,
    speaking_rate_EN=speaking_rate_EN, 
    **speaking_rate_param,
    **video_param,
    )
save_ppt_as_images(e_meta)
num = gen_Eng_notes_from_Korean(e_meta, CONF_FILE)

# ------------------------------------------------
# if needed modify the script here.
# ------------------------------------------------

#%% ================================================================================
#   ================================================================================
timepoints, total_duration = ppt_tts(e_meta, num)
composite_video_from_ppt_and_voice(e_meta, timepoints)

e_title, e_desc = translate_title_desc(k_title, k_desc, CONF_FILE)
e_keywords = re.findall(r"#(\w+)", e_desc)
print(e_title)
print(e_desc)
print(e_keywords)

#%% ================================================================================
#   ================================================================================
# if needed modify title, desc, and tags here
# ------------------------------------------------
e_title = ""
e_desc = ""
print(e_title)
print(e_desc)
print(e_keywords)

#%% ---------------------------------------------------------------------------------------
#%% ================================================================================
#   ================================================================================
# if needed modify title, desc, and tags here
# ------------------------------------------------
e_id = upload_video(e_meta, e_title, e_desc, e_keywords, thumbnail_file=thumbnail_file_e, client_secrets_file=GOOGLE_CLIENT, playlist_id=playlist_id_it)

#%%
#%% ================================================================================
#   ================================================================================
# if needed modify title, desc, and tags here
# ------------------------------------------------
append_to_youtube_log(e_ppt_file, e_title, e_desc, e_keywords, e_id, type_of_video)
