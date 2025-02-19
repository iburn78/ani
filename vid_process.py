#%%
from ani_tools import *

PPT_PATH = 'data/ppt/ppts/'
VOICE_PATH = 'data/voice/'

class VidProcess:

    MAX_SHORTS_TIME = 59
    MAX_13SEC_TIME = 59
    UNLIMITED = 10000
    # ------------------------------------------------
    # 0: wide videos
    # 1: vertical shorts
    # 2: 13 sec series
    # ------------------------------------------------
    def __init__(self, k_ppt_file, no_fade=[], video_param={}, speaking_rate_param = {}, conf_file = CONF_FILE, gca = GOOGLE_CLOUD, google_client = GOOGLE_CLIENT, youtube_conf = YOUTUBE_CONF):
        self.type_of_video = check_filename(k_ppt_file)
        self.k_ppt_file = k_ppt_file.replace('.pptx', '')+'.pptx'
        self.e_ppt_file = self.k_ppt_file.replace('_K_', '_E_')

        fade_after_slide = [x for x in list(range(50)) if x not in no_fade]
        speaking_rate_KR = speaking_rate_param.get('speaking_rate_KR', 1.2)
        speaking_rate_EN = speaking_rate_param.get('speaking_rate_EN', 1.2)
        if self.type_of_video == 2:
            speaking_rate_param['slide_break'] = 0.7
            speaking_rate_param['line_break'] = 0.4

        self.k_meta = Meta(
            ppt_file=self.k_ppt_file, google_application_credentials=gca, lang='K',
            fade_after_slide=fade_after_slide,
            speaking_rate_KR=speaking_rate_KR, 
            ppt_path = PPT_PATH,
            voice_path= VOICE_PATH,
            **speaking_rate_param,
            **video_param,
            )

        self.e_meta = Meta(
            ppt_file=self.e_ppt_file, google_application_credentials=gca, lang='E', 
            fade_after_slide=fade_after_slide,
            speaking_rate_EN=speaking_rate_EN, 
            ppt_path = PPT_PATH,
            voice_path= VOICE_PATH,
            **speaking_rate_param,
            **video_param,
            )

        self.max_length = VidProcess.MAX_SHORTS_TIME if self.type_of_video == 1 else VidProcess.MAX_13SEC_TIME if self.type_of_video == 2 else VidProcess.UNLIMITED 
        self.conf_file = conf_file
        self.google_client = google_client
        self.thumbnail_file_k = None
        self.thumbnail_file_e = None
        self.playlist_id_qp = None
        self.playlist_id_it = None
        self.k_title_header = ""
        self.e_title_header = ""

        if self.type_of_video == 0: 
            self.thumbnail_file_k = os.path.join(f"{self.k_ppt_file.replace('.pptx', '')}", "slide0.png")
            self.thumbnail_file_e = os.path.join(f"{self.e_ppt_file.replace('.pptx', '')}", "slide0.png")

        if self.type_of_video == 2: 
            self.k_title_header = '13초컷 - '
            self.e_title_header = '13sec - '
            with open(youtube_conf, 'r') as json_file:
                config = json.load(json_file)
                self.playlist_id_qp = config["qp_quick_update_playlist_id"]
                self.playlist_id_it = config["it_quick_update_playlist_id"]

    def check_duration(self, total_duration):
        if total_duration > self.max_length: 
            print('----------------------------------------------------------------------')
            print(f'Total Duration {round(total_duration,1)} is over the limit {self.max_length}.')
            print('----------------------------------------------------------------------')
            return False
        return True

    def gen_K_video(self):
        num = ppt_to_text(self.k_meta)
        timepoints, total_duration = ppt_tts(self.k_meta, num)
        if self.check_duration(total_duration) == False: 
            raise Exception('Duration Error ---- ')
            # return False
        save_ppt_as_images(self.k_meta)
        composite_video_from_ppt_and_voice(self.k_meta, timepoints)
        return True

    def gen_E_video(self, translate = True):
        if translate:
            num = gen_Eng_notes_from_Korean(self.e_meta, CONF_FILE)  # if notes are not translated in the E-PPT-file, this translates notes only therein.
        else:
            num = ppt_to_text(self.e_meta)
        timepoints, total_duration = ppt_tts(self.e_meta, num)
        if self.check_duration(total_duration) == False: 
            raise Exception('Duration Error ---- ')
            # return False
        save_ppt_as_images(self.e_meta)
        composite_video_from_ppt_and_voice(self.e_meta, timepoints)
        return True

    def gen_K_prep(self):
        notes = get_notes(os.path.join(self.k_meta.ppt_path, self.k_ppt_file))
        [title, tags, desc] = get_desc(notes, 'K', self.conf_file)
        self.k_title_tail = title
        self.k_title = self.k_title_header + title
        self.k_desc = tags+ '\n' +desc
        self.k_keywords = list(tags.replace('#','').strip().split(' '))
        print('--------------------')
        print(self.k_title)
        print(self.k_desc)
        print(self.k_keywords)

    def gen_E_prep(self):
        if self.k_title_tail != None and len(self.k_title) > 0:
            self.e_title_tail, self.e_desc = translate_title_desc(self.k_title_tail, self.k_desc, self.conf_file)
            self.e_title = self.e_title_header + self.e_title_tail
            self.e_keywords = re.findall(r"#(\w+)", self.e_desc)
        else: 
            notes = get_notes(os.path.join(self.e_meta.ppt_path, self.e_ppt_file))
            [title, tags, desc] = get_desc(notes, 'E', self.conf_file)
            self.e_title = self.e_title_header + title
            self.e_desc = tags+ '\n' +desc
            self.e_keywords = list(tags.replace('#','').strip().split(' '))
        print('--------------------')
        print(self.e_title)
        print(self.e_desc)
        print(self.e_keywords)

    def set_K_prep(self, title = None, desc = None, tags = None):
        if title: 
            self.k_title = title
        if desc: 
            self.k_desc = tags + '\n' + desc
        if tags: 
            self.k_keywords = list(tags.replace('#','').strip().split(' '))

    def set_E_prep(self, title = None, desc = None, tags = None):
        if title: 
            self.e_title = title
        if desc: 
            self.e_desc = tags + '\n' + desc
        if tags: 
            self.e_keywords = list(tags.replace('#','').strip().split(' '))

    def process_K_video(self, k_info=None):
        if exist_in_youtube_log(self.k_ppt_file):
            self.k_title, self.k_desc = get_record_from_youtube_log(self.k_ppt_file)
            self.k_keywords = re.findall(r"#(\w+)", self.k_desc)
            print('Korean version upload already done.')
            return None
        if self.gen_K_video() == False: 
            print('K-video creation failed')
            return None
        if k_info:
            title = k_info['title']
            desc = k_info['desc']
            tags = k_info['tags']
            self.set_K_prep(title, desc, tags)
            print(self.k_title)
            print(self.k_desc)
            print(self.k_keywords)
        else:
            self.gen_K_prep()
            return

    def process_E_video(self, e_info=None):
        # 13 sec videos are already translated...
        if self.type_of_video == 2:
            translate = False
        else: 
            translate = True

        if exist_in_youtube_log(self.e_ppt_file):
            print('English version upload already done.')
            return None
        if self.gen_E_video(translate=translate) == False: 
            print('E-video creation failed')
            return None
        if e_info:
            title = e_info['title']
            desc = e_info['desc']
            tags = e_info['tags']
            self.set_E_prep(title, desc, tags)
            print(self.e_title)
            print(self.e_desc)
            print(self.e_keywords)
        else:
            self.gen_E_prep()
            return
    
    def upload_K_video(self):
        self.k_id = upload_video(self.k_meta, self.k_title, self.k_desc, self.k_keywords, thumbnail_file=self.thumbnail_file_k, client_secrets_file=self.google_client, playlist_id=self.playlist_id_qp)
        append_to_youtube_log(self.k_ppt_file, self.k_title, self.k_desc, self.k_keywords, self.k_id, self.type_of_video)
        # gen_E_file(self.k_meta.ppt_path, self.k_meta.ppt_file)

    def upload_E_video(self):
        self.e_id = upload_video(self.e_meta, self.e_title, self.e_desc, self.e_keywords, thumbnail_file=self.thumbnail_file_e, client_secrets_file=self.google_client, playlist_id=self.playlist_id_it)
        append_to_youtube_log(self.e_ppt_file, self.e_title, self.e_desc, self.e_keywords, self.e_id, self.type_of_video)

    ### USAGE Guide ################
    # k_info = {} (or e_info)
    # k_info['title'] = ''
    # k_info['desc'] = ''
    # k_info['tags'] = ''  # hash tag string

    # no_fade = []
    # video_param = {}
    # speaking_rate_param = {}
    # video_param = {
    #     "target_slide_for_video": [1, 4, 6], # slide starts from 0
    #     "video_file_path": ['index_KR.mp4', 'index_us.mp4', 'index_other.mp4'],
    #     "video_height_scale": [0.50, 0.50, 0.50],
    #     "video_location": [(30, 250), (30, 250), (30, 250)],  # list of (x, y)
    #     "video_interrupt": False,
    # }

    # Always initialize with K-file name
    # k_ppt_file = ''
    # vp = VidProcess(k_ppt_file)
    # vp.process()

if __name__ == "__main__": 
    k_ppt_file = '노루홀딩스_K_2025-01-13_shorts_13sec'

    vp = VidProcess(k_ppt_file)
    vp.process_K_video()
    # vp.process_E_video()
    #%% 
    # ppt_tts(vp.k_meta,1)
    # vp.upload_K_video()
    # vp.upload_E_video()