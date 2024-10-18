#%% 
from openai import OpenAI
from ppt2video.tools import *
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
import json
import os
import shutil

def _translate_text(input_text, conf_file, type='ssml'):
    with open(conf_file, 'r') as json_file:
        config = json.load(json_file)
        api_key = config['openai']

    client = OpenAI(api_key=api_key)
    if type=='ssml': 
        content_command = "The following text is in SSML format. Please translate the content to English while preserving the SSML tags:\n\n"
    elif type=='title': 
        content_command = "The following text is a title of a YouTube video. Please translate it into English concisely so that it fits as a title and don't put quotation marks in the result:\n\n"
    elif type=='desc':
        content_command = "The following text is a short description of a YouTube video. Please translate it into English concisely so that it fits as a short description. For hastags, translate them as well, leave the # marks, and put them in front of the result as in the original text:\n\n"
    else:
        content_command = "ERROR"

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

def gen_Eng_notes_from_Korean(meta: Meta, conf_file):
    num = ppt_to_text(meta)

    for n in range(num):
        txt_file = f"{os.path.join(meta.voice_path, meta.ppt_file.replace(meta.ppt_extension, '_' + str(n) + '.txt'))}"
        backup_file = txt_file.replace(".txt", "_backup.txt")
        shutil.copy(txt_file, backup_file)

        with open(txt_file, 'r', encoding='utf-8') as file:
            ssml_content = file.read()

        translated_text = _translate_text(ssml_content, conf_file, 'ssml')

        with open(txt_file, 'w', encoding='utf-8') as file:
            file.write(translated_text)

        print(f"Translated text for file {n}: {translated_text}")

    return num

def translate_title_desc(title, desc, conf_file): 
    translated_title = _translate_text(title, conf_file, 'title')
    translated_desc = _translate_text(desc, conf_file, 'desc')
    return translated_title, translated_desc


def upload_video(meta: Meta, title, desc, keywords, thumbnail_file=None, category_id = '27', client_secrets_file = None): # '27': education
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, SCOPES)
    credentials = flow.run_local_server(port=0)
    
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    # Call the YouTube API to upload the video
    video_file_path = os.path.join(meta.ppt_path, meta.ppt_file.replace('.pptx','.mp4'))
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
                "privacyStatus": "public"  # 'public', 'private', or 'unlisted'
            }
        },
        media_body=MediaFileUpload(video_file_path)
    )
    
    response = request.execute()
    print(f"Video uploaded! Video ID: {response['id']}")

    # Upload the thumbnail after the video is uploaded
    # Thumbnail upload seems only working for non-shorts
    if thumbnail_file != None: 
        thumbnail_path = os.path.join(meta.ppt_path, thumbnail_file)
        request = youtube.thumbnails().set(
            videoId=response['id'],
            media_body=MediaFileUpload(thumbnail_path)
        )
    
        thumbnail_response = request.execute()
        print(f"Thumbnail uploaded! Status: {thumbnail_response}")
