#%% 
from ppt_maker import PPT_MAKER, WORKING_DIR
from trader.tools.tools import get_name_from_code
from ani.ani_tools import close_excel_if_saved
from trader.analysis import drawer
from openai import OpenAI
import pandas as pd
import os, json
import textwrap

pd_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF_FILE = os.path.join(pd_, 'config/config.json')

class CDB_MAKER: #content database maker
    def __init__(self, code=None, lang='K'):
        self.content_db_path = PPT_MAKER.get_file_path(PPT_MAKER.CONTENT_DB_FILENAME)
        # read content_db, and if not exists, creates one with preset columns
        self.content_db = PPT_MAKER.read_content_db(self.content_db_path)
        self.slide_type = PPT_MAKER.SLIDE_TYPE # ['title', 'image', 'bullet', 'close']
        with open(CONF_FILE, 'r') as json_file:
            config = json.load(json_file)
            self.api_key = config['openai']
        if code:    
            self.setup(code, lang)

    def setup(self, code, lang='K'):
        # setup
        # ["v_id", "name", "lang", "date", "suffix", "slide", "type", "title", "subtitle", "image_path", "image", "desc", "note"] 
        self.code = code
        self.v_id = 1 if self.content_db.empty else self.content_db['v_id'].iloc[-1] + 1 
        self.name = get_name_from_code(code)
        self.lang = lang
        self.lang_ = 'Korean' if lang == 'K' else 'English'
        self.date = pd.Timestamp.now().strftime('%Y-%m-%d')
        self.suffix = 'shorts_13sec'
        self.image_path = os.path.join(WORKING_DIR, 'images/')

    def make_target_db(self):
        # columns to be filled: 'slide', 'type', 'title', 'subtitle', 'image', 'desc', 'note'
        # Work sequence: 
        # [company desc slide 1]
        # 1. get company description using AI with about ~20 words
        # 2. get ranking of the company in the industry using AI with about ~10 words, ranking in market cap 
        # [image slide 2, 3]
        # 1. get data for revenue and operating profit
        # 2. generate graphs (images) and save path (after adjusting the save path for ppt maker)
        # 3. generate title, subtitle, desc and notes for the graphs
        #    - title: yyyy nQ revenue/operating profit etc.
        #    - subtitle: interpretation of the graph with the most important information using AI
        #    - desc: descriptive information about the graph
        #    - note: script for that slide mostly repeating the subtitle and desc more succinctly
        #    - might add why these changes occured in a few words using AI
        # [bullet slide 4]
        # 1. get three most important issues the company is facing using AI with given format (e.g., [issue title], desc... )
        # 2. generate title, subtitle, and notes 
        #    - title might be 'Key issues' or 'Key challenges' predefined
        #    - generate subtitle to depict the issues in a few words using AI
        #    - notes: script for that slide summarizing the three key issues in maybe ~30 words
        # [close slide 5]
        # 1. get decision whether this company is promising or not using AI with about ~7 words as title
        # 2. generate subtitle and notes
        #    - subtitle: why this decision is made in a few words using AI ~ 10 words
        #    - notes: script for that slide summarizing the decision in maybe ~20 words
        # [title slide 0]
        # 1. gather all notes for all pages, and get the title for entire presentation in 10 words 
        
        self.strength_slide = self.gen_strength_slide(slide_no=1) 
        self.image_slides = self.gen_image_slides(slide_start_no=2) # two lines
        self.issues_slide = self.gen_issues_slide(slide_no=4)
        self.close_slide = self.gen_close_slide(slide_no=5)
        self.title_slide = self.gen_title_slide(slide_no=0)

        self.target_db = pd.concat([self.title_slide, self.strength_slide, self.image_slides, self.issues_slide, self.close_slide]) 
        self.target_db = self.target_db.reindex(columns=PPT_MAKER.CONTENT_DB_COLUMNS)
        self.target_db[['v_id', 'name', 'lang', 'date', 'suffix', 'image_path']] = [self.v_id, self.name, self.lang, self.date, self.suffix, self.image_path]

    def update_content_db(self):
        self.content_db = pd.concat([self.content_db, self.target_db])
        close_excel_if_saved(self.content_db_path)
        with pd.ExcelWriter(self.content_db_path) as writer:
            self.content_db.to_excel(writer, sheet_name=PPT_MAKER.CONTENT_DB_SHEETNAME, index=False)

    def _get_AI_response(self, command, knote=False):
        client = OpenAI(api_key=self.api_key)

        if self.lang == 'K':
            if knote: # korean note case
                command = command.strip() + '''\n한국어로 답변하고, 반드시 "습니다", "입니다"등으로 끝나는 경어를 활용한 서술체를 사용할 것'''
            else:
                command = command.strip() + '''\n한국어로 답변하고, "다"등으로 끝나는 서술체를 사용하지 말고 반드시 "음", "됨", "임"등으로 끝나는 문단체로 간결하게 답변할것'''

        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": (
                        command
                    )
                }
            ]
        )
        return chat_completion.choices[0].message.content

    def gen_strength_slide(self, slide_no):
        # explanation of the company's businesses and strengths 
        command = f"Get a short description of {self.name} company in {20} words in {self.lang_}"
        desc = self._get_AI_response(command)
        res_dict = {
            'slide': slide_no,
            'type': 'bullet',
            'title': 'Company Description',
            'subtitle': '',
            'desc': desc,
            'note': desc,
        }
        return pd.DataFrame([res_dict])

    def gen_issues_slide(self, slide_no):
        command = textwrap.dedent(f'''\
            Provide {3} most recent pending issues that could significantly affect the future performance of {self.name}, formatted exactly as follows:

            [title of issue 1]
            explanation of issue 1

            [title of issue 2]
            explanation of issue 2

            [title of issue 3]
            explanation of issue 3

            (or more if necessary)

            CONTENT REQUIREMENTS:
            - Titles should be around {7} words.
            - Explanations should be around {30} words each and include specific details with current facts or numbers. Avoid statistics more than 1 year old.
            - Focus only on the company's major top 2 business segments at most.
            - Do not include financial performances such as revenue or profit.
            - Do not include environmental or social issues.
            - If an issue is related to competition, competitors should be narrowly defined within their main business segment.
            - Avoid redundant explanations, quotation marks, or additional formatting to ensure the output can be directly copied and pasted as plain text.
            - Include "[" and "]" brackets in the issue titles.
            ''')

        desc = self._get_AI_response(command)

        note_command = textwrap.dedent(f'''\
            Summarize the following three key issues in {50} words in {self.lang_}:

            ''') + desc

        note = self._get_AI_response(note_command, knote=True)
        print(note)

        res_dict = {
            'slide': slide_no,
            'type': 'bullet',
            'title': '핵심 이슈' if self.lang == 'K' else 'Key Issues',
            'subtitle': '',
            'desc': desc,
            'note': note,
        }
        return pd.DataFrame([res_dict])

    def gen_image_slides(self, slide_start_no):
        res_dict = {
            'slide': slide_start_no,
            'type': 'image',
            'title': 'Revenue Trend',
            'subtitle': '',
            'desc': '',
            'note': '',
        }
        return pd.DataFrame([res_dict])

    def gen_close_slide(self, slide_no):
        res_dict = {
            'slide': slide_no,
            'type': 'close',
            'title': 'Thank you',
            'subtitle': '',
            'desc': '',
            'note': '',
        }
        return pd.DataFrame([res_dict])

    def gen_title_slide(self, slide_no):
        res_dict = {
            'slide': slide_no,
            'type': 'title',
            'title': 'Title',
            'subtitle': '',
            'desc': '',
            'note': '',
        }
        return pd.DataFrame([res_dict])

if __name__ == "__main__":
    cdb_maker = CDB_MAKER()
    cdb_maker.setup('005930', 'K')
    cdb_maker.make_target_db()
    cdb_maker.update_content_db()