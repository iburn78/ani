#%% 
from ppt2video.tools import *
from openai import OpenAI
import json
import shutil

with open('../config/config.json', 'r') as json_file:
    config = json.load(json_file)
    api_key = config['openai']

client = OpenAI(api_key=api_key)

def translate_text(ssml_text):
    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": (
                    "The following text is in SSML format. Please translate the content to English "
                    "while preserving the SSML tags:\n\n"
                    f"{ssml_text}"
                )
            }
        ]
    )
    return chat_completion.choices[0].message.content

meta = Meta(
    ppt_file='삼성전자_2024_2Q_E_2024-10-07_shorts01.pptx',  # Name of your PPT filefrom ppt2video.tools import *
    image_prefix='슬라이드',  # The prefix for image files (varies depending on the PowerPoint language version)
    google_application_credentials='../config/google_cloud.json',  # Location and filename of your Google Cloud service account key
    lang = "E", 
)
num = ppt_to_text(meta)

for n in range(num):
    txt_file = f"{os.path.join(meta.voice_path, meta.ppt_file.replace(meta.ppt_extension, '_' + str(n) + '.txt'))}"
    backup_file = txt_file.replace(".txt", "_backup.txt")
    shutil.copy(txt_file, backup_file)

    with open(txt_file, 'r', encoding='utf-8') as file:
        ssml_content = file.read()

    translated_text = translate_text(ssml_content)

    with open(txt_file, 'w') as file:
        file.write(translated_text)

    print(f"Translated text for file {n}: {translated_text}")

#%% 
timepoints = ppt_tts(meta, num)
video_from_ppt_and_voice(meta, timepoints)