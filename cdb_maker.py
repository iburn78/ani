#%% 
from ppt_maker import PPT_MAKER, WORKING_DIR
import pandas as pd
import os

df_krx = pd.read_feather(r'C:\Users\user\projects\trader\data_collection\data\df_krx.feather')
# read content_db, and if not exists, creates one with preset columns
content_db = PPT_MAKER.read_content_db(PPT_MAKER.get_file_path(PPT_MAKER.CONTENT_DB_FILENAME))
display(content_db)
target_db = pd.DataFrame(columns=content_db.columns)
slide_type = ['title', 'image', 'bullet', 'close']

v_id_ = 1 if content_db.empty else content_db['v_id'].iloc[-1] + 1 
date_ = pd.Timestamp.now().strftime('%Y-%m-%d')
suffix_ = 'shorts_13sec'
image_path_ = os.path.join(WORKING_DIR, 'images/')
slide_ = 0
type_ = slide_type[0]

code = '000270'
lang_ = 'K'
name_ = df_krx.loc[df_krx.index == code, 'Name'].iloc[0]

# %%

# Graph Generation
import sys

# Print the current PYTHONPATH
for path in sys.path:
    print(path)
# from trader.analysis import drawer
from trader.analysis import a01_bar_plot




