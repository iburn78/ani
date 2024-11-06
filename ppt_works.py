#%% 
from pptx import Presentation

# Load the existing presentation
prs = Presentation("data/ppt/삼성바이오로직스_K_2024-11-01_shorts_13sec.pptx")

# Loop through each slide
for slide_number, slide in enumerate(prs.slides, start=0):
    print(f"\nSlide {slide_number}")
    print(len(slide.shapes))
    for shape in slide.shapes: 
        print(shape.name)
    
    # Loop through placeholders on the slide
    for placeholder in slide.placeholders:
        print(f"  Placeholder Index: {placeholder.placeholder_format.idx}")
        print(f"  Placeholder Type: {placeholder.placeholder_format.type}")
        print(f"  Placeholder Text: '{placeholder.text}'")

data = {
    "title": "Quarterly Report",
    "content": "This quarter's performance exceeded expectations.",
    "table_data": [["Category", "Value"], ["Revenue", "$1M"], ["Profit", "$200K"]]
}

# Update placeholders
slide = prs.slides[1]
# slide.placeholders[10].text = data["title"]
# slide.shapes[1].text = data['content']
shape = slide.shapes[4]
left = shape.left
top = shape.top
width = shape.width
height = shape.height

# Remove the existing image shape
slide.shapes._spTree.remove(shape._element)

# Add the new image in the same position and size
new_image_path = 'data/ppt/005380_fh_operat_01_E.png'
slide.shapes.add_picture(new_image_path, left, top, width, height)

# slide.shapes[2].text = data['content']
# slide.placeholders[1].text = data["content"]
prs.save('data/ppt/temp.pptx')
# %%
