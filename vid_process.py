#%%
from ani_tools import *

class VidProcess:
    # 'data/ppt', 'data/voice' folder should be in the same directory as this script
    MAX_SHORTS_TIME = 59
    MAX_13SEC_TIME = 20
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
            speaking_rate_param['slide_break'] = 0.1
            speaking_rate_param['line_break'] = 0.1

        self.k_meta = Meta(
            ppt_file=self.k_ppt_file, google_application_credentials=gca, lang='K',
            fade_after_slide=fade_after_slide,
            speaking_rate_KR=speaking_rate_KR, 
            **speaking_rate_param,
            **video_param,
            )

        self.e_meta = Meta(
            ppt_file=self.e_ppt_file, google_application_credentials=gca, lang='E', 
            fade_after_slide=fade_after_slide,
            speaking_rate_EN=speaking_rate_EN, 
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
            return False
        save_ppt_as_images(self.k_meta)
        composite_video_from_ppt_and_voice(self.k_meta, timepoints)
        return True

    def gen_E_video(self):
        num = gen_Eng_notes_from_Korean(self.e_meta, CONF_FILE)
        timepoints, total_duration = ppt_tts(self.e_meta, num)
        if self.check_duration(total_duration) == False: 
            return False
        save_ppt_as_images(self.e_meta)
        composite_video_from_ppt_and_voice(self.e_meta, timepoints)
        return True

    def gen_K_prep(self):
        notes = get_notes(os.path.join(self.k_meta.ppt_path, self.k_ppt_file))
        [title, tags, desc] = get_desc(notes, 'K', self.conf_file)
        self.k_title = self.k_title_header + title
        self.k_desc = tags+ '\n' +desc
        self.k_keywords = list(tags.replace('#','').strip().split(' '))
        print('--------------------')
        print(self.k_title)
        print(self.k_desc)
        print(self.k_keywords)

    def gen_E_prep(self):
        self.e_title, self.e_desc = translate_title_desc(self.k_title, self.k_desc, self.conf_file)
        self.e_keywords = re.findall(r"#(\w+)", self.e_desc)
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
            user_input = input("Title, Desc, and Tags acceptable, and proceed to upload? (yes/no/exit): ").strip().lower()
            while user_input not in ['yes', 'y']:
                if user_input == 'exit': 
                    return None
                title = input('Title: ')
                desc = input('Desc: ')
                tags = input('Tags-hashtag words: ')
                self.set_K_prep(title, desc, tags)
                print('--------------------')
                print(self.k_title)
                print(self.k_desc)
                print(self.k_keywords)
                user_input = input("Proceed to upload? (yes/no)").strip().lower()
        self.k_id = upload_video(self.k_meta, self.k_title, self.k_desc, self.k_keywords, thumbnail_file=self.thumbnail_file_k, client_secrets_file=self.google_client, playlist_id=self.playlist_id_qp)
        append_to_youtube_log(self.k_ppt_file, self.k_title, self.k_desc, self.k_keywords, self.k_id, self.type_of_video)
        gen_E_file(self.k_meta.ppt_path, self.k_meta.ppt_file)

    def process_E_video(self, e_info=None):
        if exist_in_youtube_log(self.e_ppt_file):
            print('English version upload already done.')
            return None
        if self.gen_E_video() == False: 
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
            user_input = input("Title, Desc, and Tags acceptable, and proceed to upload? (yes/no/exit): ").strip().lower()
            while user_input not in ['yes', 'y']:
                if user_input == 'exit': 
                    return None
                title = input('Title: ')
                desc = input('Desc: ')
                tags = input('Tags-hashtag words: ')
                self.set_E_prep(title, desc, tags)
                print('--------------------')
                print(self.e_title)
                print(self.e_desc)
                print(self.e_keywords)
                user_input = input("Proceed to upload? (yes/no)").strip().lower()
            self.e_id = upload_video(self.e_meta, self.e_title, self.e_desc, self.e_keywords, thumbnail_file=self.thumbnail_file_e, client_secrets_file=self.google_client, playlist_id=self.playlist_id_it)
            append_to_youtube_log(self.e_ppt_file, self.e_title, self.e_desc, self.e_keywords, self.e_id, self.type_of_video)
    
    def process(self, k_info=None, e_info=None): 
        self.process_K_video(k_info)
        self.process_E_video(e_info)



if __name__ == "__main__": 
    k_ppt_file = ''
    no_fade = []
    video_param = {}
    # video_param = {
    #     "target_slide_for_video": [1, 4, 6], # slide starts from 0
    #     "video_file_path": ['index_KR.mp4', 'index_us.mp4', 'index_other.mp4'],
    #     "video_height_scale": [0.50, 0.50, 0.50],
    #     "video_location": [(30, 250), (30, 250), (30, 250)],  # list of (x, y)
    #     "video_interrupt": False,
    # }
    # k_info = {}
    # k_info['title'] = ''
    # k_info['desc'] = ''
    # k_info['tags'] = ''  # hash tag string
    k_info = None
    speaking_rate_param = {}
    vp = VidProcess(k_ppt_file, no_fade, video_param, speaking_rate_param)
    vp.process(k_info=k_info, e_info=None)