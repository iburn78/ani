#%% 
from ppt_maker import PPT_MAKER, WORKING_DIR
from trader.tools.tools import get_name_from_code, get_market_and_rank, rank_counter
from ani.ani_tools import close_excel_if_saved, script_optimizer
from trader.analysis.drawer import Drawer
from openai import OpenAI
import pandas as pd
import os, json
import textwrap
import re

pd_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF_FILE = os.path.join(pd_, 'config/config.json')

class CDB_MAKER: #content database maker
    ###### Structure of pages #######
    # Slide Template Types: ['title', 'image', 'bullet', 'close']
    # - definded in blank.pptx

    # Slide Content Types: ['title', 'strengths', 'image', 'issues', 'close'] 
    # - bullet template has two content types: 'strengths' and 'issues'
    
    # Reference Information Types: ['title', 'strengths', 'image', 'issues', 'close', 'general]
    # - slide content type + 'general'

    # In Each Template, Element Types: ['title', 'subtitle', 'desc', 'note'] 
    # - for bullet template, 'desc' element has two styles: 'b_title', 'b_desc' 

    # Keys to be stored in the db for each slide: ['slide'(no), 'type'(template), 'title', 'subtitle', 'image'(filename), 'desc', 'note']

    # Unique video (or a ppt file) identifier: v_id

    # reference_info data: list of strings ['info a', 'info b', ]. Do not include \n
    ALLOWED_REF_INFO_KEYS = ['title', 'strengths', 'image', 'issues', 'close', 'general']   

    # define max words number in each element to pass to AI
    LENGTH_K_DICT = {
        'title': {'title': 7, 'note': 12},
        'image': {'subtitle': 6, 'desc': 12, 'note': 20},
        'bullet': {'title': 6, 'subtitle': 6, 'b_title': 5, 'b_desc': 15, 'note': 25},
        'close': {'title': 6, 'subtitle': 8, 'note': 20},
    }
    LENGTH_E_DICT = {
        'title': {'title': 6, 'note': 10},
        'image': {'subtitle': 5, 'desc': 10, 'note': 15},
        'bullet': {'title': 5, 'subtitle': 5, 'b_title': 4, 'b_desc': 12, 'note': 20},
        'close': {'title': 5, 'subtitle': 7, 'note': 15},
    }
    ########### 
    # GPT_MODEL = "gpt-4o-mini"
    # GPT_MODEL = "gpt-4o"
    GPT_MODEL = "gpt-4o-2024-11-20"
    # Initially get AI response n times longer than intended length, then compress it using AI again to get live detail
    INITIAL_MULTPLE = 5 
    ########### 

    BIZ_COVERAGE = 2 # If multiple business segments, how many to focus
    ISSUES_COUNT = 3 # In order to change this other than 3, need to change issues slide command as well, as the response format is hard coded.
    DATA_FRESHNESS = 6 # months
    IMAGE_DIR_PATH = 'images/'
    SUFFIX = 'shorts_13sec'

    def __init__(self, code=None, lang=None, reference_info={}):
        self.content_db_path = PPT_MAKER.get_file_path(PPT_MAKER.CONTENT_DB_FILENAME)
        # read content_db, and if not exists, creates one with preset columns
        self.content_db = PPT_MAKER.read_content_db(self.content_db_path)
        self.slide_type = PPT_MAKER.SLIDE_TYPE # ['title', 'image', 'bullet', 'close']
        with open(CONF_FILE, 'r') as json_file:
            config = json.load(json_file)
            self.api_key = config['openai']
        if code and lang:    
            self.setup(code, lang, reference_info)

    def setup(self, code, lang='K', reference_info={}):
        # setup
        # ["v_id", "name", "lang", "date", "suffix", "slide", "type", "title", "subtitle", "image_path", "image", "desc", "note"] 
        self.code = code
        self.v_id = 1 if self.content_db.empty else int(self.content_db['v_id'].iloc[-1]) + 1 
        self.name = get_name_from_code(code)
        self.lang = lang
        self.lang_ = 'Korean' if lang == 'K' else 'English'
        self.eng_name = self.get_eng_name()
        self.lend = CDB_MAKER.LENGTH_K_DICT if lang == 'K' else CDB_MAKER.LENGTH_E_DICT
        self.ilend = {key: {nested_key: nested_value * CDB_MAKER.INITIAL_MULTPLE for nested_key, nested_value in value.items()} for key, value in self.lend.items()}
        self.date = pd.Timestamp.now().strftime('%Y-%m-%d')
        self.suffix = CDB_MAKER.SUFFIX
        self.image_path = os.path.join(WORKING_DIR, CDB_MAKER.IMAGE_DIR_PATH)
        self.notes = []
        self.reference_info = self._ref_info_inspect(reference_info)
        self.make_target_db()

    def make_target_db(self):
        # columns to be filled: 'slide'(no), 'type'(template), 'title', 'subtitle', 'image', 'desc', 'note'
        # Work sequence: 

        # [company desc slide 1]
        # 1. get company description 
        # 2. get trade market and ranking in market cap 
        
        # [image slide 2, 3]
        # 1. get data for revenue and operating profit
        # 2. generate graphs (images) and save path (after adjusting the save path for ppt maker)
        # 3. generate title, subtitle, desc and note for the graphs
        #    - title: yy nQ revenue/operating profit etc.
        #    - subtitle: interpretation of the graph with the most important information 
        #    - desc: descriptive information about the graph and the factful reason behind 

        # [bullet slide 4]
        # 1. get the most important issues the company with given format (e.g., [issue title], desc... )
        # 2. generate title, subtitle, and note 
        #    - title might be 'Key issues' or 'Key challenges' predefined
        #    - generate subtitle to depict the issues in a few 

        # [close slide 5]
        # 1. get which point about this company is most promising as title
        # 2. generate subtitle and note
        #    - subtitle: why this decision is made 

        # [title slide 0]
        # 1. gather all note for all pages, and get the title for entire presentation in 10 words 
        
        target_slides = []
        self.notes = [] # initialize
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
        self._update_content_db()
        print('success--- writing v_id', self.v_id)

    def _update_content_db(self):
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
            # elif style == 'bullet':  # bullet 
            #     command = command.strip() + '''\n- 한국어로 답변하되, [] 안에는 문장이 아닌 하나의 명사구문으로 답변하고, 그 외 부분은 문장으로 답변하되 "다"등으로 끝나는 서술체를 사용하지 말고 "음", "됨", "임"등으로 끝나는 음슴체로 간결하게 답변할 것'''
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
            # elif style == 'bullet':  # bullet
            #     command = command.strip() + '''\n- Answer in English as a noun phrase in [], and as concise sentences elsewhere'''
            else: 
                if style != None: # custom style
                    command = command.strip() + '\n' + str(style) 

        chat_completion = client.chat.completions.create(
            model=CDB_MAKER.GPT_MODEL,
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
        return self.pre_process(response)

    def _ref_info_inspect(self, reference_info):
        if not isinstance(reference_info, dict):
            raise ValueError("reference_info must be a dict.")

        invalid_keys = set(reference_info.keys()) - set(CDB_MAKER.ALLOWED_REF_INFO_KEYS)
        if invalid_keys:
            raise ValueError(f"Invalid keys: {', '.join(invalid_keys)}")

        for key, value in reference_info.items():
            if not isinstance(value, list):
                raise ValueError(f"Key '{key}' must have a list value.")
            for item in value:
                if not isinstance(item, str) or '\n' in item:
                    raise ValueError(f"Invalid item in '{key}': {item!r}")
        return reference_info

    def _append_ref_info(self, command, target_content_type=None):
        # 'general' is included anyway
        if target_content_type not in CDB_MAKER.ALLOWED_REF_INFO_KEYS: raise Exception('key error')
        ref = self.reference_info.get('general', [])
        if target_content_type != 'general':
            ref = self.reference_info.get(target_content_type, []) + ref
        
        if len(ref) > 0:
            r_ = ''
            for r in ref:
                r_ += '- '+r+'\n'
            reference_info = textwrap.dedent(f'''\  
            REFERENCE INFORMATION:
            {r_}
            ''')
            command = command + '\n' + reference_info
        return command 

    # t_type: template type, c_type: content type
    def _initial_command_process(self, initial_command, t_type, c_type, command_style_dict):
        initial_command = self._append_ref_info(initial_command, target_content_type=c_type)
        lend = self.lend[t_type]  # final response length dictionary

        # ensure getting right number of responses
        ind = 0
        while True:
            raw_response = self._get_AI_response(initial_command)
            raw_response = [r for r in raw_response.splitlines() if r.strip() != '']
            if len(raw_response) == len(command_style_dict): 
                break
            else:
                ind += 1
                print('--- Raw Response Length Error --- no tried:', ind)
                print(raw_response)
                if ind >= 10: 
                    print('--- MAX TRIAL LIMT EXCEED --- SOMETHING WRONG ---')
                    break

        # reduce to desired length
        response = []
        for i in range(len(command_style_dict)):
            command = textwrap.dedent(f'''\ 
                Summarize in {lend[command_style_dict[i+1][0]]} words at most. Use facts and details therein, and avoid abstract expressions and hype words.

                ''')+raw_response[i]+'\n'
            if command_style_dict[i+1][0] == 'note':
                response.append(self.post_process(self._get_AI_response(command, style=command_style_dict[i+1][1]), remove_period=False))
            else:
                response.append(self.post_process(self._get_AI_response(command, style=command_style_dict[i+1][1])))
        return response

    # combine bullet items and build them into a desc string element
    # [title]
    # exp
    # 
    # [title]
    # ext ... 
    # this format is interpreted by PPT MAKER
    def _build_bullet_desc(self, response, target_content_type, seq=1): # sequence 1: title then exp, sequence -1: exp then title
        if target_content_type == 'strengths': # default length is 3 items
            n_get = 3
        elif target_content_type == 'issues': 
            n_get = CDB_MAKER.ISSUES_COUNT
        else: 
            raise Exception('Check usage...')
        r = ''
        if seq == 1: # title and exp 
            for i in range(n_get):
                r += '['+response[2*i]+']\n'+response[2*i+1]+'\n\n'
        elif seq == -1: # exp and title
            for i in range(n_get):
                r += '['+response[2*i+1]+']\n'+response[2*i]+'\n\n'
        else: 
            raise Exception('Check...')

        return r.strip()

    # applied to each output of AI response
    def pre_process(self, text): 
        # Pattern to match variations of "line n:" (case-insensitive)
        pattern = re.compile(r'line\s+\d+\s*[-:]', re.IGNORECASE)
        # Substitute the matching patterns with an empty string
        text = pattern.sub('', str(text)).strip()
        # if enclosed entirely by '' or "", remove it
        text = text[1:-1] if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")) else text

        return text

    # applied before saving as dataframe
    def post_process(self, text, remove_period = True):
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
        if remove_period and text.endswith('.'):
            text = text[:-1]
    
        return text.strip()
    

    def get_eng_name(self):
        command = textwrap.dedent(f'''\
            Provide the English name of {self.name}. 
            Only provide the name without any additional information, quotation marks, periods, commas, or formatting.
            ''')
        return self._get_AI_response(command)


    ### CONTENT SLIDE GENERATION PART ###
    def gen_strength_slide(self, slide_no):
        # explanation of the company's businesses and strengths 
        t_type = 'bullet' # template type
        content_type = 'strengths' 
        ilend = self.ilend[t_type]  # initial response length dictionary

        market, rank = get_market_and_rank(self.code)

        # get first initial responses then refine them 
        initial_command = textwrap.dedent(f'''\ 
            Provide the following about {self.name}, formatted as follows:

            line 1: The company's business in {ilend['b_title']} words
            line 2: Key products, services, or business models in {ilend['b_desc']} words
            line 3: The company's top key strength in {ilend['b_title']} words
            line 4: Evidence of the top key strength in {ilend['b_desc']} words
            line 5: The company's second key strength in {ilend['b_title']} words
            line 6: Evidence of the second key strength in {ilend['b_desc']} words
            line 7: A script summarizing the busienss and strengths in {ilend['note']} words
            line 8: The title in {ilend['subtitle']} words

            CONTENT REQUIREMENTS:
            - Provide **exactly one line of text** for each numbered item.
            - Primarily refer to Korean sources, using English sources only as supplementary.
            - Exclude terms like 'line n', 'business', 'strength', 'evidence', 'script', or 'title' from the response.
            - Include specific details with current facts or numbers as much as possible such as industry rankings, key technologies etc.
            - Focus on the company's top {CDB_MAKER.BIZ_COVERAGE} business segments at most.
            - Do not include the company name anywhere.
            - Do not include financial performances such as revenue or profit.
            - Do not include environmental or social issues unless they are part of the core business.
            - If an issue is related to competition, competitors should be narrowly defined within their top {CDB_MAKER.BIZ_COVERAGE} major business segments.
            - Avoid redundant explanations, quotation marks, or additional formatting to ensure the output can be directly copied and pasted as plain text.
            ''')        
        command_style_dict = { # keys: line nubmer (starting from 1), first data: length dict keys, second data: AI response style
            1: ('b_title', 'noun_phrase'), 
            2: ('b_desc', 'short_sentence'),
            3: ('b_title', 'noun_phrase'), 
            4: ('b_desc', 'short_sentence'),
            5: ('b_title', 'noun_phrase'), 
            6: ('b_desc', 'short_sentence'),
            7: ('note', 'sentence'),
            8: ('subtitle', 'noun_phrase'),
        }
        response = self._initial_command_process(initial_command, t_type, content_type, command_style_dict)
        subtitle = response[7] + f' <{market} {rank_counter(rank, lang=self.lang)}>'  # < >: interpreted by PPT MAKER
        bullet_desc = self._build_bullet_desc(response, target_content_type=content_type)
        note = script_optimizer(response[6])
        self.notes.append(note)

        res_dict = {
            'slide': slide_no,
            'type': t_type, # template type
            'title': self.name if self.lang == 'K' else self.eng_name,
            'subtitle': subtitle,
            'desc': bullet_desc, 
            'note': note,
        }
        return pd.DataFrame([res_dict])

    def gen_issues_slide(self, slide_no):
        t_type = 'bullet' # template type
        content_type = 'issues' 
        ilend = self.ilend[t_type]  # initial response length dictionary
        initial_command = textwrap.dedent(f'''\
            Provide {CDB_MAKER.ISSUES_COUNT} recent pending issues within {CDB_MAKER.DATA_FRESHNESS} months that could significantly affect the future performance of {self.name}, formatted exactly as follows:

            line 1: A detailed explanation of the most important issue in {ilend['b_desc']} words
            line 2: The title of the issue above in {ilend['b_title']} words
            line 3: A detailed explanation of the second most important issue in {ilend['b_desc']} words
            line 4: The title of the second issue above in {ilend['b_title']} words
            line 5: A detailed explanation of the third most important issue in {ilend['b_desc']} words
            line 6: The title of the thrid issue above in {ilend['b_title']} words
            line 7: A script summarizing the all three issues in {ilend['note']} words
            line 8: The title of the all three issues in {ilend['subtitle']} words

            CONTENT REQUIREMENTS:
            - Provide **exactly one line of text** for each numbered item.
            - Primarily refer to Korean sources, using English sources only as supplementary.
            - Exclude terms like 'line n', 'business', 'strength', 'evidence', 'script', 'issue', or 'title' from the response.
            - Focus on the company's top {CDB_MAKER.BIZ_COVERAGE} business segments at most.
            - Do not include the company name anywhere.
            - Do not include financial performances such as revenue or profit.
            - Do not include environmental or social issues unless they are part of the core business.
            - If an issue is related to competition, competitors should be narrowly defined within their top {CDB_MAKER.BIZ_COVERAGE} major business segments.
            - Avoid redundant explanations, quotation marks, or additional formatting to ensure the output can be directly copied and pasted as plain text.
            ''')        
        command_style_dict = { # keys: line nubmer (starting from 1), first data: length dict keys, second data: AI response style
            1: ('b_desc', 'short_sentence'), 
            2: ('b_title', 'noun_phrase'), 
            3: ('b_desc', 'short_sentence'), 
            4: ('b_title', 'noun_phrase'), 
            5: ('b_desc', 'short_sentence'), 
            6: ('b_title', 'noun_phrase'), 
            7: ('note', 'sentence'),
            8: ('subtitle', 'noun_phrase'),
        }
        response = self._initial_command_process(initial_command, t_type, content_type, command_style_dict)
        subtitle = response[7]
        bullet_desc = self._build_bullet_desc(response, target_content_type=content_type, seq=-1)
        note = script_optimizer(response[6])
        self.notes.append(note)

        res_dict = {
            'slide': slide_no,
            'type': t_type, # template type
            'title': '핵심 이슈' if self.lang == 'K' else 'Key Issues',
            'subtitle': subtitle, 
            'desc': bullet_desc,
            'note': note,
        }
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
            output_file=output_file,
            plt_show=False,
            )

        if x[-1][2] != 'Q':
            raise Exception('Check Data Format...')

        if self.lang == 'K':
            title = f'{x[-1][:2]}/{x[-1][3]}분기 실적'
        else: 
            title = f'{x[-1][:2]}/{x[-1][3]}Q results'

        # content generation part
        t_type = 'image' # template type
        content_type = 'image'
        ilend = self.ilend[t_type]
        account_name = {'revenue': 'revenue', 
                        'operating_income': 'operting profit',}
        initial_command = textwrap.dedent(f'''\ 
            The following is {account_name[target_account]} data of {self.name}.
            Quarters: {x}
            Data: {y} in 9^{unit_base} KRW

            Provide analysis of the quarterly data, formatted exactly as follows:

            line 1: Assessment of the most recent quarter's performance with respect to the other quarters, e.g. turnaround, seasonalilty, U-shaped, plummeted, outlier, overperformed, etc in {ilend['subtitle']} words. If data is significantly different from the last year same quarter, note that too.
            line 2: Explain in {ilend['desc']} words the detailed reasons for the above assessment based on internet search.
            line 3: A script summarizing the above assessment and reasons behind {ilend['note']} words

            CONTENT REQUIREMENTS:
            - Provide **exactly one line of text** for each numbered item.
            - Primarily refer to Korean sources, using English sources only as supplementary.
            - Exclude terms like 'line n', 'business', 'strength', 'evidence', 'script', 'issue', or 'title' from the response.
            - Do not include the company name anywhere.
            - Avoid redundant explanations, quotation marks, or additional formatting to ensure the output can be directly copied and pasted as plain text.
            ''')        
        command_style_dict = { # keys: line nubmer (starting from 1), first data: length dict keys, second data: AI response style
            1: ('subtitle', 'noun_phrase'), 
            2: ('desc', 'short_sentence'), 
            3: ('note', 'sentence'),
        }
        response = self._initial_command_process(initial_command, t_type, content_type, command_style_dict)
        subtitle = response[0]
        desc = response[1]
        note = script_optimizer(response[2])
        self.notes.append(note)

        res_dict = {
            'slide': slide_no,
            'type': t_type, # template type
            'title': title, 
            'subtitle': subtitle,
            'desc': desc,
            'note': note,
            'image': image,
        }
        self.notes.append(note)
        return pd.DataFrame([res_dict])

    def gen_close_slide(self, slide_no):
        t_type = 'close' # template type
        content_type = 'close'
        ilend = self.ilend[t_type]
        notes_so_far = '\n\n'.join(self.notes)
        initial_command = textwrap.dedent(f'''\ 
            Below is a script for a video about {self.name}. Provide responses exactly as instructed based on the script content:

            line 1: A final assessment of the outlook of the company for the next quarter in {ilend['title']} words.
            line 2: A closing remark on which economic or social indicator to follow further to forecast the performance of the company in {ilend['subtitle']} words.
            line 3: A script summarizing the above assessment and reasons behind {ilend['note']} words

            CONTENT REQUIREMENTS:
            - Provide **exactly one line of text** for each numbered item.
            - Primarily refer to Korean sources, using English sources only as supplementary.
            - Exclude terms like 'line n', 'business', 'strength', 'evidence', 'script', 'issue', or 'title' from the response.
            - Do not include the company name anywhere.
            - Avoid redundant explanations, quotation marks, or additional formatting to ensure the output can be directly copied and pasted as plain text.

            Script:
            ''') + notes_so_far + '\n'
        command_style_dict = { # keys: line nubmer (starting from 1), first data: length dict keys, second data: AI response style
            1: ('title', 'noun_phrase'), 
            2: ('subtitle', 'short_sentence'), 
            3: ('note', 'sentence'),
        }
        response = self._initial_command_process(initial_command, t_type, content_type, command_style_dict)
        title = response[0]
        subtitle = response[1]
        note = script_optimizer(response[2]) 
        note += '\n' + ('감사합니다. ' if self.lang == 'K' else 'Thank you. ')
        self.notes.append(note)

        res_dict = {
            'slide': slide_no,
            'type': t_type, # template type
            'title': title, 
            'subtitle': subtitle,
            'desc': None,
            'note': note,
        }
        return pd.DataFrame([res_dict])

    def gen_title_slide(self, slide_no):
        t_type = 'title' # template type
        content_type = 'title'
        ilend = self.ilend[t_type]
        notes_so_far = '\n\n'.join(self.notes)
        initial_command = textwrap.dedent(f'''\ 
            This is a script for a video about {self.name}. Provide responses exactly as instructed based on the script content:

            line 1: A title for the front page of the video that would catch people's interest in {ilend['title']} words.
            line 2: An introductory script that aligns with the above title in {ilend['note']} words.

            CONTENT REQUIREMENTS:
            - Provide **exactly one line of text** for each numbered item.
            - The company name **must be included** naturally in both line 1 and line 2.
            - Primarily refer to Korean sources, using English sources only as supplementary.
            - Exclude terms like 'line n', 'business', 'strength', 'evidence', 'script', 'issue', or 'title' from the response.
            - Avoid redundant explanations, quotation marks, or additional formatting to ensure the output can be directly copied and pasted as plain text.

            Script:
            ''') + notes_so_far + '\n'
        command_style_dict = { # keys: line nubmer (starting from 1), first data: length dict keys, second data: AI response style
            1: ('title', 'noun_phrase'), 
            2: ('note', 'sentence'),
        }
        response = self._initial_command_process(initial_command, t_type, content_type, command_style_dict)
        title = response[0]
        note = script_optimizer(response[1])

        res_dict = {
            'slide': slide_no,
            'type': t_type, # template type
            'title': title,
            'subtitle': None, 
            'desc': None,
            'note': note,
        }
        return pd.DataFrame([res_dict])


def _debugger(df): 
    for col in df.columns: 
        print(f'{col}---------')
        print(df[col].iloc[0])

if __name__ == "__main__":
    ref_info = {'strengths': ['The company has a key strength in HBM'], 
                'general': ['HBM is a key issue in the momory industry'], 
                }
    code = '000660'
    _ = CDB_MAKER(code, 'K', ref_info) #_.v_id
    _ = CDB_MAKER(code, 'E', ref_info)