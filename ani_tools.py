#%% 
from openai import OpenAI
from ppt2video.tools import *
import json
import os
import shutil

CONF_FILE = '../config/config.json'
CLIENT_SECRETS_FILE = "../config/google_client.json"

def _translate_text(input_text, conf_file, ssml=True):
    with open(conf_file, 'r') as json_file:
        config = json.load(json_file)
        api_key = config['openai']

    client = OpenAI(api_key=api_key)
    if ssml: 
        content_command = "The following text is in SSML format. Please translate the content to English while preserving the SSML tags:\n\n"
    else: 
        content_command = "The following text is a title or short description of a YouTube video. Please translate it into English concisely so that it fits as a title or short description:\n\n"
    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": (
                    content_command + input_text
                )
            }
        ]
    )
    return chat_completion.choices[0].message.content

def gen_Eng_notes_from_Korean(meta: Meta):
    num = ppt_to_text(meta)

    for n in range(num):
        txt_file = f"{os.path.join(meta.voice_path, meta.ppt_file.replace(meta.ppt_extension, '_' + str(n) + '.txt'))}"
        backup_file = txt_file.replace(".txt", "_backup.txt")
        shutil.copy(txt_file, backup_file)

        with open(txt_file, 'r', encoding='utf-8') as file:
            ssml_content = file.read()

        translated_text = _translate_text(ssml_content, CONF_FILE)

        with open(txt_file, 'w') as file:
            file.write(translated_text)

        print(f"Translated text for file {n}: {translated_text}")

    return num

def translate_title_desc(title, desc): 
    translated_title = _translate_text(title)
    translated_desc = _translate_text(desc)
    return translated_title, translated_desc


#%% 
# Upload part

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CATEGORY_ID = "27" # education

def upload_video(meta: Meta, title, desc, keywords, category_id = CATEGORY_ID):
    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    # Call the YouTube API to upload the video
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": desc,
                "tags": keywords,
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": "public"  # 'public', 'private' or 'unlisted'
            }
        },
        media_body=os.path.join(meta.ppt_path, meta.ppt_file)
    )
    
    response = request.execute()
    print(f"Video uploaded! Video ID: {response['id']}")

