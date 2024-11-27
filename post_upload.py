#%% 
from ani_tools import *


#%% 

import os
import re
from datetime import datetime
import subprocess
from pptx import Presentation

def find_pptx_files(base_dir):
    category_K_files = []
    category_E_files = []
    
    # Walk through the directory and its subdirectories
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.pptx'):
                if '_K_' in file:
                    category_K_files.append(os.path.join(root, file))
                elif '_E_' in file:
                    category_E_files.append(os.path.join(root, file))
    
    return category_K_files, category_E_files

def filter_short_files(files):
    # Filter for files containing '_shorts' in the name (case insensitive)
    shorts_files = [file for file in files if '_shorts' in file.lower()]
    return shorts_files

def sort_files_by_date(file_list):
    files_with_date = []
    files_no_date = []
    
    for file in file_list:
        match = re.search(r'\d{4}-\d{2}-\d{2}', file)
        if match:
            date_str = match.group(0)
            # Convert the found date string into a datetime object
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            files_with_date.append((file, date_obj))
        else: 
            files_no_date.append(file)
    
    if len(files_no_date) > 0: 
        raise Exception('Certain files do not have proper date in filename')

    # Sort the files by date (oldest to newest)
    files_with_date.sort(key=lambda x: x[1])
    return [file[0] for file in files_with_date]

def lprint(flist):
    for f in flist:
        print(f)

def open_ppt_file(ppt_path):
    try:
        subprocess.run(['start', 'powerpnt', ppt_path], check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while opening the file: {e}")

base_dir = r'C:\Users\user\projects\analysis'
cat_K_files, cat_E_files = find_pptx_files(base_dir)
cat_K_shorts = sort_files_by_date(filter_short_files(cat_K_files))
cat_E_shorts = sort_files_by_date(filter_short_files(cat_E_files))

#%% 

ppt_path = cat_K_shorts[20]
open_ppt_file(ppt_path)
# for f in cat_E_files[:3]: 
#     n = get_slide_count(f)
#     print(n, f)

#%% 

from ppt2video.tools import _clean_text

def get_slide_count(ppt_path):
    ppt = Presentation(ppt_path)
    return len(ppt.slides)

def get_notes(ppt_path):
    ppt = Presentation(ppt_path)

    slide_content = ''
    for slide_number, slide in enumerate(ppt.slides):
        if slide.notes_slide and slide.notes_slide.notes_text_frame:
            notes = slide.notes_slide.notes_text_frame.text
            notes = _clean_text(notes)
            slide_content += f'<br> (P{slide_number+1}) '+notes + '\n'
    
    return slide_content


a = get_notes(cat_E_files[0])
print(a)

QP_SHORTS_CARD = 45  # Quarterly Performances -Shorts (한글본, Korean)
ist = IST()

form_data = {
    "title": "Programmatically Created Post",
    "content": a,
    "tags": "haha this is tags", 
}
images = ['data/ppt/images/005380_fh_operat_01_E.png', 'data/ppt/images/207940_price_average_E.png']

ist.create_post(QP_SHORTS_CARD, form_data, images, html=True)