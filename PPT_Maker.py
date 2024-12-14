#%% 
import os
import pandas as pd
from pptx import Presentation
from PIL import Image
import win32com.client

WORKING_DIR = 'data/ppt/'

# reading a content DB, and make a ppt file for a given v_id
# defining procedure and format within the class for a given blank template
class PPT_MAKER:
    BLANK_FILE_NAME = 'blank.pptx'
    CONTENT_DB_FILENAME = 'content_db.xlsx'
    PLACEHOLDER_IDX_DICT = {
        'title': {'date': 11, 'title': 0, 'subtitle': None, 'image': None, 'desc': None},
        'image': {'date': None, 'title': 0, 'subtitle': 10, 'image': 11, 'desc': 12},
        'bullet': {'date': None, 'title': 0, 'subtitle': 10, 'image': None, 'desc': 12},
        'close': {'date': None, 'title': 0, 'subtitle': 10, 'image': None, 'desc': None},
    }

    def __init__(self, v_id, target_filename=None, working_dir=WORKING_DIR):
        self.working_dir = working_dir
        self.prs = Presentation(self.get_file_path(PPT_MAKER.BLANK_FILE_NAME))
        self.content_db = self.read_content_db(self.get_file_path(PPT_MAKER.CONTENT_DB_FILENAME))
        if self.get_target_db(v_id, target_filename):
            print(f'Target_db creation successful for {self.target_pptx_name} with length {len(self.target_db)}.')

    def get_file_path(self, filename):
        return os.path.join(self.working_dir, filename)

    def read_content_db(self, excel_path):
        # DB structure
        sheet_name = 'datasheet'
        preset_columns = ["v_id", "name", "lang", "date", "suffix", "slide", "type", "title", "subtitle", "image_path", "image", "desc", "note"]

        if os.path.exists(excel_path):
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime("%Y-%m-%d")
        else:
            df = pd.DataFrame(columns=preset_columns)
            with pd.ExcelWriter(excel_path) as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        return df

    # you can either give v_id (unique) or a filename complying a strict format.
    def get_target_db(self, v_id, target_filename=None):
        if target_filename:
            target_db = self.get_target_db_by_filename(target_filename)
        else:
            target_db = self.content_db.loc[self.content_db['v_id'] == v_id]

        self.target_db = self.validate_target_db(v_id, target_filename, target_db)
        self.target_pptx_name = target_filename or self.generate_target_filename(target_db)
        self.validate_target_filename()
        return True

    def get_target_db_by_filename(self, target_filename):
        tf = target_filename.replace('.pptx', '').split('_')
        return self.content_db.loc[
            (self.content_db['name'] == tf[0]) &
            (self.content_db['lang'] == tf[1]) &
            (self.content_db['date'] == tf[2]) &
            (self.content_db['suffix'] == tf[3] + '_' + tf[4])
        ]

    def validate_target_db(self, v_id, target_filename, target_db):
        if len(target_db) == 0: 
            raise ValueError("No matching entry found")
        # Check if target_db is empty
        if not (target_db['v_id'] == v_id).all():
            raise ValueError(f"v_id ({v_id}) is not unique for the given filename: {target_filename}")
        # Check if 'name', 'lang', 'date', or 'suffix' columns have non-identical values
        if target_db['name'].nunique() > 1 or target_db['lang'].nunique() > 1 or target_db['date'].nunique() > 1 or target_db['suffix'].nunique() > 1:
            raise ValueError(f"Non-identical values found in 'name', 'lang', 'date', or 'suffix' columns for v_id: {v_id}")
        # Check if all values in 'slide' are integers
        if not target_db['slide'].apply(lambda x: isinstance(x, int)).all():
            raise ValueError(f"All values in 'slide' column must be integers for v_id: {v_id}")
        # Check if all values in 'slide' are different
        if target_db['slide'].nunique() != len(target_db):
            raise ValueError(f"Duplicate values found in 'slide' column for v_id: {v_id}")
        return target_db

    def generate_target_filename(self, target_db):
        return f"{target_db['name'].iloc[0]}_{target_db['lang'].iloc[0]}_{target_db['date'].iloc[0]}_{target_db['suffix'].iloc[0]}.pptx"

    def validate_target_filename(self):
        if self.target_pptx_name == PPT_MAKER.BLANK_FILE_NAME:
            raise Exception('Check target file name: should not be the blank file name')

    def make_ppt(self):
        for index, row in self.target_db.iterrows():
            slide = self.prs.slides.add_slide(self.get_slide_type(row['type']))
            self.populate_slide_with_data(slide, row)
            self.add_image_to_slide(slide, row)

        PPT_MAKER.close_ppt_if_saved(self.target_pptx_name)
        self.prs.save(self.get_file_path(self.target_pptx_name))
        print("PPT save completed ---- ")

    def populate_slide_with_data(self, slide, row):
        tdict = PPT_MAKER.PLACEHOLDER_IDX_DICT[row['type']]
        for i in ['date', 'title', 'subtitle', 'desc']:
            if tdict[i] is not None: # should not None explictly!
                tph = next((obj for obj in slide.placeholders if obj.placeholder_format.idx == tdict[i]), None)
                if tph:
                    tph.text = row[i]

    def add_image_to_slide(self, slide, row):
        tdict = PPT_MAKER.PLACEHOLDER_IDX_DICT[row['type']]
        if tdict['image'] is not None: # should not None explictly!
            img_path = os.path.join(row['image_path'], row['image'])
            self.make_img_square(img_path)
            tph = next((obj for obj in slide.placeholders if obj.placeholder_format.idx == tdict['image']), None)
            if tph:
                tph.insert_picture(img_path)

    def make_img_square(self, image_path, fill_color=(255, 255, 255, 0)):
        with Image.open(image_path) as img:
            width, height = img.size
            new_size = max(width, height)
            new_img = Image.new("RGBA", (new_size, new_size), fill_color)
            new_img.paste(img, ((new_size - width) // 2, (new_size - height) // 2))
            new_img.save(image_path)

    def list_slide_layouts(self):
        for idx, layout in enumerate(self.prs.slide_layouts):
            print(f"Layout {idx}: {layout.name}")

    def get_slide_type(self, type):
        for idx, layout in enumerate(self.prs.slide_layouts):
            if type in layout.name: 
                return layout

    def print_placeholder_idx(self): 
        for slide_number, slide in enumerate(self.prs.slides, start=0):
            print(f"Slide number: {slide_number}")
            print('--------------')
            for placeholder in slide.placeholders:
                print(f"Placeholder Index: {placeholder.placeholder_format.idx}")
                print(f"Placeholder Type: {placeholder.placeholder_format.type}")
                if hasattr(placeholder, 'text'):
                    print(f"Placeholder Text: '{placeholder.text}'")

    @staticmethod
    def close_ppt_if_saved(ppt_filename):
        # Connect to PowerPoint application
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        for presentation in powerpoint.Presentations:
            if os.path.basename(presentation.FullName) == ppt_filename:
                if presentation.Saved:
                    presentation.Close()
                else:
                    print(f"{ppt_filename} is not saved. Not closing.")
                return
        print(f"{ppt_filename} is not open.")

    @staticmethod
    def replace_shape_text(shape, new_text):
        if not shape.has_text_frame:
            raise Exception('Not a text shape')
        for paragraph in shape.text_frame.paragraphs:
            runs = paragraph.runs
            if runs:
                # Overwrite existing runs to preserve as much formatting as possible
                runs[0].text = new_text
                # Clear remaining runs if there are any extra
                for i in range(1, len(runs)):
                    runs[i].text = ""
            else:
                # Fallback if no runs exist: add a new run with the new text
                new_run = paragraph.add_run()
                new_run.text = new_text
            if shape.text == new_text: 
                return True
            else: 
                raise Exception('Text replacement error')

    @staticmethod
    def replace_shape_image(shape, new_image_path): 
        if hasattr(shape, "image"):
            # Get the position and size of the current image
            left = shape.left
            top = shape.top
            width = shape.width
            height = shape.height
                
            # Remove the old image shape
            shape._spTree.remove(shape._element)
            # Replace with a new image
            shape.add_picture(new_image_path, left, top, width=width, height=height)
        else: 
            raise Exception('Not an image shape')

if __name__ == '__main__': 
    v_id = 1 
    pm = PPT_MAKER(v_id)
    pm.make_ppt()

