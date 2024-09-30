#%% 
from pptx import Presentation

ppt_file = 'data/ppt/삼성전자_2024_2Q_E_2024-09-30.pptx'
txt_file_base = ppt_file.replace('.pptx', '')
ppt = Presentation(ppt_file)

file_number = 1
max_size = 4500  # Maximum size for each file in bytes
current_size = 0  # Track the size of the current file
notes_content = '<speak>\n'  # Initial content

def write_to_file(content, current_file_number, current_size):
    """Write content to a numbered txt file and return updated file size."""
    txt_file = f"{txt_file_base}_{current_file_number}.txt"
    
    if current_size == 0:
        with open(txt_file, 'w', encoding='utf-8') as notes_file:
            notes_file.write('<speak>\n')
            notes_file.write(content)
    else: 
        with open(txt_file, 'a', encoding='utf-8') as notes_file:
            notes_file.write(content)
    
    # Return the new size after writing
    return current_size + len(content.encode('utf-8'))

# Process slides
for slide_number, slide in enumerate(ppt.slides, start=1):
    if slide.notes_slide and slide.notes_slide.notes_text_frame:
        slide_content = '<break time="2s"/>\n'
        notes = slide.notes_slide.notes_text_frame.text
        slide_content += notes.replace('\n', '<break time="0.7s"/>\n') + "\n"
    else:
        slide_content = ""

    # If adding the slide content would exceed the max size, write to a new file
    if current_size + len(slide_content.encode('utf-8')) > max_size:
        # Close the current file with '</speak>\n'
        current_size = write_to_file( '<break time="2s"/>\n </speak>\n', file_number, current_size)
        
        # Increment file number, reset the current size, and start a new file
        file_number += 1
        current_size = 0

    # Write the slide content to the current file
    current_size = write_to_file(slide_content, file_number, current_size)

# Write the closing </speak> tag to the final file
current_size = write_to_file( '<break time="2s"/>\n </speak>\n', file_number, current_size)
txt_file_num = f"{txt_file_base}_num.txt"
with open(txt_file_num, 'w', encoding='utf-8') as notes_file:
    notes_file.write(f'{file_number}')

