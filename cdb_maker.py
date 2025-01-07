#%% 
from ppt_maker import PPT_MAKER, WORKING_DIR
from trader.tools.tools import get_name_from_code, get_market_and_rank, rank_counter
from ani.ani_tools import close_excel_if_saved
from trader.analysis.drawer import Drawer
from openai import OpenAI
import pandas as pd
import os, json
import textwrap
import re

pd_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF_FILE = os.path.join(pd_, 'config/config.json')

class CDB_MAKER: #content database maker

    # define max words number in each element to pass to AI
    LENGTH_K_DICT = {
        'title': {'title': 7, 'note': 15},
        'image': {'title': 3, 'subtitle': 5, 'desc': 15, 'note': 30},
        'bullet': {'title': 7, 'subtitle': 5, 'b_title': 20, 'b_desc': 40, 'note': 30},
        'close': {'title': 7, 'subtitle': 10, 'note': 15},
    }
    LENGTH_E_DICT = {
        'title': {'title': 5, 'note': 10},
        'image': {'title': 3, 'subtitle': 4, 'desc': 10, 'note': 25},
        'bullet': {'title': 5, 'subtitle': 4, 'b_title': 5, 'b_desc': 20, 'note': 25},
        'close': {'title': 5, 'subtitle': 7, 'note': 10},
    }
    BIZ_COVERAGE = 2 # if multiple business segments, how many to focus
    ISSUES_COUNT = 3 
    DATA_FRESHNESS = 6 # months

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
        self.v_id = 1 if self.content_db.empty else int(self.content_db['v_id'].iloc[-1]) + 1 
        self.name = get_name_from_code(code)
        self.lang = lang
        self.lang_ = 'Korean' if lang == 'K' else 'English'
        self.eng_name = self.get_eng_name()
        self.lend = CDB_MAKER.LENGTH_K_DICT if lang == 'K' else CDB_MAKER.LENGTH_E_DICT
        self.date = pd.Timestamp.now().strftime('%Y-%m-%d')
        self.suffix = 'shorts_13sec'
        self.image_path = os.path.join(WORKING_DIR, 'images/')
        self.notes = []

    def make_target_db(self):
        # columns to be filled: 'slide', 'type', 'title', 'subtitle', 'image', 'desc', 'note'
        # Work sequence: 
        # [company desc slide 1]
        # 1. get company description using AI with about ~20 words
        # 2. get ranking of the company in the industry using AI with about ~10 words, ranking in market cap 
        # [image slide 2, 3]
        # 1. get data for revenue and operating profit
        # 2. generate graphs (images) and save path (after adjusting the save path for ppt maker)
        # 3. generate title, subtitle, desc and note for the graphs
        #    - title: yyyy nQ revenue/operating profit etc.
        #    - subtitle: interpretation of the graph with the most important information using AI
        #    - desc: descriptive information about the graph
        #    - note: script for that slide mostly repeating the subtitle and desc more succinctly
        #    - might add why these changes occured in a few words using AI
        # [bullet slide 4]
        # 1. get three most important issues the company is facing using AI with given format (e.g., [issue title], desc... )
        # 2. generate title, subtitle, and note 
        #    - title might be 'Key issues' or 'Key challenges' predefined
        #    - generate subtitle to depict the issues in a few words using AI
        #    - note: script for that slide summarizing the three key issues in maybe ~30 words
        # [close slide 5]
        # 1. get decision whether this company is promising or not using AI with about ~7 words as title
        # 2. generate subtitle and note
        #    - subtitle: why this decision is made in a few words using AI ~ 10 words
        #    - note: script for that slide summarizing the decision in maybe ~20 words
        # [title slide 0]
        # 1. gather all note for all pages, and get the title for entire presentation in 10 words 
        
        target_slides = []
        # slide number (page number) should be assigned explicitly
        target_slides.append(self.gen_strength_slide(slide_no=1))
        target_slides.append(self.gen_image_slide(slide_no=2, target_account='revenue')) 
        target_slides.append(self.gen_image_slide(slide_no=3, target_account='operating_income')) 
        target_slides.append(self.gen_issues_slide(slide_no=4))
        target_slides.append(self.gen_close_slide(slide_no=5))
        target_slides.append(self.gen_title_slide(slide_no=0))

        self.target_db = pd.concat(target_slides).sort_values(by='slide', ascending=True)
        self.target_db = self.target_db.reindex(columns=PPT_MAKER.CONTENT_DB_COLUMNS)
        self.target_db[['v_id', 'name', 'lang', 'date', 'suffix', 'image_path']] = [self.v_id, self.name, self.lang, self.date, self.suffix, self.image_path]
        print('success--- writing v_id', self.v_id)
        return int(self.v_id)

    def update_content_db(self):
        self.content_db = pd.concat([self.content_db, self.target_db])
        close_excel_if_saved(self.content_db_path)
        with pd.ExcelWriter(self.content_db_path) as writer:
            self.content_db.to_excel(writer, sheet_name=PPT_MAKER.CONTENT_DB_SHEETNAME, index=False)

    def _get_AI_response(self, command, style = None):
        client = OpenAI(api_key=self.api_key)

        if self.lang == 'K':
            if style == 'noun_phrase':  # title, subtitle
                command = command.strip() + '''\n- 한국어로 답변하되, 반드시 문장이 아닌 하나의 명사구문으로 답변할것. 단, 명사를 단순히 열거하지 말것'''
            elif style == 'sentence':  # note
                command = command.strip() + '''\n- 한국어로 문장으로 답변하되, 반드시 "습니다", "입니다"등으로 끝나는 경어를 활용한 서술형 문장으로 답변할 것'''
            elif style == 'short_sentence':  # desc 
                command = command.strip() + '''\n- 한국어로 문장으로 답변하되, "다"등으로 끝나는 서술체를 사용하지 말고 반드시 "음", "됨", "임"등으로 끝나는 음슴체로 간결하게 답변할 것'''
            elif style == 'bullet':  # bullet 
                command = command.strip() + '''\n- 한국어로 답변하되, [] 안에는 문장이 아닌 하나의 명사구문으로 답변하고, 그 외 부분은 문장으로 답변하되 "다"등으로 끝나는 서술체를 사용하지 말고 "음", "됨", "임"등으로 끝나는 음슴체로 간결하게 답변할 것'''
            else: 
                if style != None: # custom style
                    command = command.strip() + '\n' + str(style) 
        else: # English
            if style == 'noun_phrase': # title, subtitle
                command = command.strip() + '''\n- Answer in English as a noun phrase, not full sentences, and do not list only standalone nouns'''
            elif style == 'sentence':  # note
                command = command.strip() + '''\n- Answer in English as complete sentences'''
            elif style == 'short_sentence':  # general desc
                command = command.strip() + '''\n- Answer in English as concise sentences'''
            elif style == 'bullet':  # bullet
                command = command.strip() + '''\n- Answer in English as a noun phrase in [], and as concise sentences elsewhere'''
            else: 
                if style != None: # custom style
                    command = command.strip() + '\n' + str(style) 

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
        response = chat_completion.choices[0].message.content

        # basic pre-process of response
        response = str(response).strip()
        response = response[1:-1] if (response.startswith('"') and response.endswith('"')) or (response.startswith("'") and response.endswith("'")) else response
        
        return response
    
    def get_eng_name(self):
        command = textwrap.dedent(f'''\
            Provide the English name of {self.name}. 
            Only provide the name without any additional information, quotation marks, periods, commas, or formatting.
            ''')
        return self.post_process(self._get_AI_response(command))

    def gen_strength_slide(self, slide_no):
        ptype = 'bullet'
        lend = self.lend[ptype]  # length dictionary
        # explanation of the company's businesses and strengths 
        market, rank = get_market_and_rank(self.code)

        command = textwrap.dedent(f'''\ 
            Provide the following about {self.name}, formatted exactly as follows:

            [Summary of company business in {lend['b_title']} words at most]
            Explanation of the company's business in {lend['b_desc']} words at most, focusing only on the company's top {CDB_MAKER.BIZ_COVERAGE} business segments at most.

            [Summary of company top key strength in {lend['b_title']} words at most]
            Explanation of the company's top key strength in {lend['b_desc']} words at most.

            [Summary of company second key strength in {lend['b_title']} words at most]
            Explanation of the company's second key strength in {lend['b_desc']} words at most.

            CONTENT REQUIREMENTS:
            - Explanations should include specific details with current facts or numbers.
            - Focus only on the company's top {CDB_MAKER.BIZ_COVERAGE} major business segments at most.
            - Do not include the company name anywhere.
            - Do not include financial performances such as revenue or profit.
            - Do not include environmental or social issues unless they are part of the core business.
            - If an issue is related to competition, competitors should be narrowly defined within their main business segment.
            - Avoid redundant explanations, quotation marks, or additional formatting to ensure the output can be directly copied and pasted as plain text.
            - Include "[" and "]" brackets as shown in the format, and start explanations on a new line.
            ''')        
        desc = self._get_AI_response(command, style='bullet')
        
        subtitle_command = textwrap.dedent(f'''\
            Provide the best title that catches key strengths based on the following description of {self.name} in at most {lend['subtitle']} words, and do not inlcude the company name in the title.

            ''') + desc + '\n'
        subtitle = self._get_AI_response(subtitle_command, style='noun_phrase')
        subtitle = subtitle + f' <{market} {rank_counter(rank, lang=self.lang)}>'

        note_command = textwrap.dedent(f'''\
            Summarize the following description of {self.name} in {lend['note']} words:

            ''') + desc + '\n'
        note = self._get_AI_response(note_command, style='sentence')

        res_dict = {
            'slide': slide_no,
            'type': ptype,
            'title': self.name if self.lang == 'K' else self.eng_name,
            'subtitle': self.post_process(subtitle),
            'desc': self.post_process(desc),
            'note': self.post_process(note),
        }
        self.notes.append(note)
        return pd.DataFrame([res_dict])

    def gen_issues_slide(self, slide_no):
        ptype = 'bullet'
        lend = self.lend[ptype]
        command = textwrap.dedent(f'''\
            Provide {CDB_MAKER.ISSUES_COUNT} recent pending within {CDB_MAKER.DATA_FRESHNESS} months issues that could significantly affect the future performance of {self.name}, formatted exactly as follows:

            [Title of issue 1]
            Explanation of issue 1

            [Title of issue 2]
            Explanation of issue 2

            [Title of issue 3]
            Explanation of issue 3

            (or more if necessary)

            CONTENT REQUIREMENTS:
            - Titles should be around {lend['b_title']} words.
            - Explanations should be around {lend['b_desc']} words each and include specific details with current facts or numbers. Avoid statistics more than {CDB_MAKER.DATA_FRESHNESS} months old.
            - Do not include the company name anywhere.
            - Focus only on the company's major top {CDB_MAKER.BIZ_COVERAGE} business segments at most.
            - Do not include financial performances such as revenue or profit.
            - Do not include environmental or social issues.
            - If an issue is related to competition, competitors should be narrowly defined within their main business segment.
            - Avoid redundant explanations, quotation marks, or additional formatting to ensure the output can be directly copied and pasted as plain text.
            - Include "[" and "]" brackets as shown in the format, and start explanations on a new line.
            ''')
        desc = self._get_AI_response(command, style='bullet')

        subtitle_command = textwrap.dedent(f'''\
            Provide the best title that summarizes the following key issues of {self.name} in at most {lend['subtitle']} words, and do not inlcude the company name in the title.

            ''') + desc + '\n'
        subtitle = self._get_AI_response(subtitle_command, style='noun_phrase')

        note_command = textwrap.dedent(f'''\
            Summarize the following key issues of {self.name} in {lend['note']} words:

            ''') + desc + '\n'
        note = self._get_AI_response(note_command, style='sentence')

        res_dict = {
            'slide': slide_no,
            'type': ptype,
            'title': '핵심 이슈' if self.lang == 'K' else 'Key Issues',
            'subtitle': self.post_process(subtitle),
            'desc': self.post_process(desc),
            'note': self.post_process(note),
        }
        self.notes.append(note)
        return pd.DataFrame([res_dict])

    def gen_image_slide(self, slide_no, target_account):
        # image creation part
        num_qts = 5
        unit_base = 9  
        increment_FT= (4, 0) # from ith before to jth before (0: latest quarter)
        now = pd.Timestamp.now().strftime('%m%d%H%M')
        image = f'{self.code}_{target_account}_{now}.png'
        output_file = os.path.join(WORKING_DIR, 'images', image)
        drawer = Drawer(
            spine_color='black', 
            label_text_color='black',
            figsize = (7, 6), 
            text_size = 18,
            tick_text_size = 15,
            )
        x, y = drawer.quarterly_bar_plot(
            self.code, 
            target_account, 
            num_qts, 
            unit_base, 
            increment_FT=increment_FT, 
            output_file=output_file
            )

        if x[-1][2] != 'Q':
            raise Exception('Check Data Format...')

        if self.lang == 'K':
            title = f'{x[-1][:2]}/{x[-1][3]}분기 실적'
        else: 
            title = f'{x[-1][:2]}/{x[-1][3]}Q performance'

        # content generation
        ptype = 'image'
        lend = self.lend[ptype]
        command = textwrap.dedent(f'''\ 
            The following is {target_account.replace("_", " ")} data of {self.name}.
            Quarters: {x}
            Data: {y} in 9^{unit_base} KRW

            line 0: Provide an analysis of the latest quarter's data in {lend['subtitle']} words, focusing on comparisons with the same quarter last year and/or the previous quarter.
            line 1: Explain in {lend['desc']} words the detailed reason for the {target_account.replace("_", " ")} trend of {self.name}, based on internet search.

            Instructions:
            - Do not include the company name in any part of the response.
            - Avoid redundant explanations, quotation marks, or additional formatting to ensure the output can be directly copied and pasted as plain text.
            ''')
        r_ = self._get_AI_response(command, style='short_sentence')
        responses = []
        for r in r_.splitlines():
            if r.strip() != '':
                responses.append(r)
        if len(responses) != 2:
            raise Exception('Check image section AI responses...')

        note_command = textwrap.dedent(f'''\
            Summarize the following regarding {self.name} in {lend['note']} words:

            ''') + responses[0] + '\n' + responses[1] + '\n' 
        note = self._get_AI_response(note_command, style='sentence')

        res_dict = {
            'slide': slide_no,
            'type': ptype,
            'title': self.post_process(title), 
            'subtitle': self.post_process(responses[0]),
            'desc': self.post_process(responses[1]),
            'note': self.post_process(note),
            'image': image,
        }
        self.notes.append(note)
        return pd.DataFrame([res_dict])

    def gen_close_slide(self, slide_no):
        ptype = 'close'
        lend = self.lend[ptype]
        notes_so_far = '\n\n'.join(self.notes)
        command = textwrap.dedent(f'''\ 
            This is a script for a video about {self.name}. Provide responses exactly as instructed based on the script content:

            line 1: Provide a final assessment of the outlook of the company for the next quarter in {lend['title']} words.
            line 2: Provide a closing remark on which economic or social indicator to follow further to forecast the performance of the company in {lend['subtitle']} words.

            Instructions:
            - Do not include the company name in any part of the response.
            - Avoid redundant explanations, quotation marks, or additional formatting to ensure the output can be directly copied and pasted as plain text.

            Script:
            ''') + notes_so_far + '\n'
        r_ = self._get_AI_response(command, style='short_sentence')
        responses = []
        for r in r_.splitlines():
            if r.strip() != '':
                responses.append(r)
        if len(responses) != 2:
            raise Exception('Check close section AI responses...')

        note_command = textwrap.dedent(f'''\
            Summarize the following in {lend['note']} words:

            ''') + responses[0] + '\n' + responses[1] + '\n' 
        note = self._get_AI_response(note_command, style='sentence')

        res_dict = {
            'slide': slide_no,
            'type': 'close',
            'title': self.post_process(responses[0]),
            'subtitle': self.post_process(responses[1]),
            'desc': None,
            'note': self.post_process(note),
        }
        self.notes.append(note)
        return pd.DataFrame([res_dict])

    def gen_title_slide(self, slide_no):
        ptype = 'title'
        lend = self.lend[ptype]
        notes_so_far = '\n\n'.join(self.notes)
        command = textwrap.dedent(f'''\ 
            This is a script for a video about {self.name}. Provide responses exactly as instructed based on the script content:

            line 1: Provide a title for the front page of the video that would catch people's interest in {lend['title']} words.
            line 2: Provide an introductory script that aligns with the above title in {lend['note']} words.

            Instructions:
            - The company name must be included naturally in each line.
            - Avoid redundant explanations, quotation marks, or additional formatting to ensure the output can be directly copied and pasted as plain text.
            - Do 

            Script:
            ''') + notes_so_far + '\n'
        r_ = self._get_AI_response(command, style='short_sentence')

        responses = []
        for r in r_.splitlines():
            if r.strip() != '':
                responses.append(r)
        if len(responses) != 2:
            raise Exception('Check close section AI responses...')
        print(responses[0])
        print(responses[1])

        note_command = textwrap.dedent(f'''\
            Modify the style of the following sentence as instructed:

            ''') + responses[1] + '\n' 
        note = self._get_AI_response(note_command, style='sentence')

        res_dict = {
            'slide': slide_no,
            'type': 'title',
            'title': self.post_process(responses[0]),
            'subtitle': None, 
            'desc': None,
            'note': self.post_process(note),
        }
        return pd.DataFrame([res_dict])
    
    def post_process(self, text):
        text = text.strip()
        # Remove unmatched single and double quotation marks (ignoring apostrophes in words)
        text = re.sub(r"(^|[^a-zA-Z0-9])'(?!\w)", r'\1', text)  # Handle unmatched single quotes
        text = re.sub(r'(^|[^"])\"(?![^\"]*$)', r'\1', text)    # Handle unmatched double quotes
    
        # Remove enclosing single or double quotation marks
        if text.startswith("'") and text.endswith("'"):
            text = text[1:-1].strip()
        elif text.startswith('"') and text.endswith('"'):
            text = text[1:-1].strip()
    
        # Remove trailing period
        if text.endswith('.'):
            text = text[:-1]
    
        return text.strip()
        

        #### 
        # remove title:, etc and other unnecessary puncutations like " . etc.
        # Don't repeat company name in notes
        # put more useful info in closing page: may simplify closing page
        # detail lacking exp... gather facts.... 

def _debugger(df): 
    for col in df.columns: 
        print('['col+']:')
        print(df[col].iloc[0])

if __name__ == "__main__":
    cdb_maker = CDB_MAKER()
    cdb_maker.setup('000660', 'K')
    cdb_e_maker = CDB_MAKER()
    cdb_e_maker.setup('000660', 'E')

    _debugger(cdb_maker.gen_strength_slide(slide_no=1))
    # _debugger(cdb_maker.gen_image_slide(slide_no=2, target_account='revenue'))
    # _debugger(cdb_maker.gen_image_slide(slide_no=3, target_account='operating_income'))
    # _debugger(cdb_maker.gen_issues_slide(slide_no=4))
    # _debugger(cdb_maker.gen_close_slide(slide_no=5))
    # _debugger(cdb_maker.gen_title_slide(slide_no=0))

    _debugger(cdb_e_maker.gen_strength_slide(slide_no=1))
    # _debugger(cdb_e_maker.gen_image_slide(slide_no=2, target_account='revenue'))
    # _debugger(cdb_e_maker.gen_image_slide(slide_no=3, target_account='operating_income'))
    # _debugger(cdb_e_maker.gen_issues_slide(slide_no=4))
    # _debugger(cdb_e_maker.gen_close_slide(slide_no=5))
    # _debugger(cdb_e_maker.gen_title_slide(slide_no=0))

    # cdb_maker.make_target_db()
    # cdb_maker.update_content_db()