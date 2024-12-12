#%% 
from openai import OpenAI
from ppt2video.tools import *
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
import json
import os
import requests
import pandas as pd
import re

GOOGLE_CLIENT = "../config/google_client.json"
YOUTUBE_CONF = '../config/youtube_conf.json'
GOOGLE_CLOUD ='../config/google_cloud.json'
CONF_FILE = '../config/config.json'

VID_WORKING_DIR = 'data/ppt/'
YOUTUBE_LOG = 'data/youtube_log.xlsx'


def _translate_text(input_text, conf_file, type='ssml'):
    with open(conf_file, 'r') as json_file:
        config = json.load(json_file)
        api_key = config['openai']

    client = OpenAI(api_key=api_key)
    if type=='ssml': 
        content_command = "The following text is in SSML format. Please translate the content to English while preserving the SSML tags:\n\n"
    elif type=='title': 
        content_command = "The following text is a title of a YouTube video. Please translate it into English concisely so that it fits as a title with no more than 55 characters and don't put quotation marks in the result:\n\n"
    elif type=='desc':
        content_command = "The following text is a short description of a YouTube video. Please translate it into English concisely so that it fits as a short description. For hastags, translate them as well. For each hash tag, remove spaces, capitalize the first letter of each word, and leave the # marks. Put the hash tags in front of the result as in the original text. :\n\n"
    elif type=='script':
        content_command = "The following text is a script of a YouTube video. Please translate the Korean part into English. Also maintain the format of the text:\n\n"
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


def _get_desc(input_text, lang, conf_file):
    with open(conf_file, 'r') as json_file:
        config = json.load(json_file)
        api_key = config['openai']

    client = OpenAI(api_key=api_key)
    language = 'Korean' if lang == 'K' else 'English' if lang == 'E' else Exception("Invalid language")
    content_command = f'''
YouTube video script. Respond exactly in this format:

line 1: {language} title
line 2: {language} hash tags top 5 with the hash
line 3: {language} description up to 60 words

Titles need to be less than or at most 55 characters. Use new lines without format keywords or quotes. For hash tags, remove spaces, capitalize the first letter of each word.

'''
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

        with open(txt_file, 'r', encoding='utf-8') as file:
            ssml_content = file.read()

        translated_text = _translate_text(ssml_content, conf_file, 'ssml')

        with open(txt_file, 'w', encoding='utf-8') as file:
            file.write(translated_text)

        print(f"Translated text for file {n}: {translated_text}")

    return num


# Translate to English, and get English ttitle and desc
def translate_title_desc(title, desc, conf_file): 
    translated_title = _translate_text(title, conf_file, 'title')
    translated_desc = _translate_text(desc, conf_file, 'desc')
    return translated_title, translated_desc


# Translate to English, and get English script notes
def translate_script(script, conf_file):
    return _translate_text(script, conf_file, 'script')


# get Korean and English title, desc, tags
# lang = 'K' or 'E'
def get_desc(input_text, lang, conf_file): 
    res = _get_desc(input_text, lang, conf_file)
    res = "\n".join(line.strip() for line in res.splitlines() if line.strip()).splitlines()

    if len(res) != 3:
        print(res)
        raise Exception('Error in ChatGPT response and/or get_desc function')

    return res


# upload video to Youtube
def upload_video(meta: Meta, title, desc, keywords, thumbnail_file=None, category_id = '27', client_secrets_file = None, playlist_id = None): # '27': education
    if len(title) > 70:
        raise Exception('Title should be not too long. Currently more than 70.')
    
    # SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
    ]
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
    video_id = response['id']
    print(f"Video uploaded! Video ID: {video_id}")

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
    
    if playlist_id != None: 
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        )
        response = request.execute()
        print(f"Video added to playlist {playlist_id}")

    return video_id


def get_ids(google_client):
    SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        google_client, SCOPES)
    credentials = flow.run_local_server(port=0)
    
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    
    request = youtube.channels().list(
        part="id",
        mine=True
    )
    response = request.execute()
    
    # Extract the channel ID
    channel_id = response["items"][0]["id"]

    request = youtube.playlists().list(
        part="snippet",
        channelId=channel_id,
        maxResults=25  # Adjust as needed
    )
    response = request.execute()
    
    # Extract playlist IDs and titles (playlist_id, title)
    playlists = [(item['id'], item['snippet']['title']) for item in response.get('items', [])]

    return channel_id, playlists


def get_title_link_from_youtube(youtube_conf, excel_file):
    with open(youtube_conf, 'r') as json_file:
        config = json.load(json_file)
        API_KEY = config['API_key_Data_API_V3']
        CHANNEL_ID = config['quarterlyperf_channel_id']
        CHANNEL_ID = config['issuetracker_channel_id']

    # Define the endpoint URL
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={CHANNEL_ID}&maxResults=50&type=video&key={API_KEY}'

    # Make a request to the API
    response = requests.get(url)
    data = response.json()

    # Extract video titles and links
    video_titles = []
    video_links = []
    upload_dates = []
    for item in data['items']:
        video_title = item['snippet']['title']
        video_id = item['id']['videoId']
        video_link = f'https://www.youtube.com/watch?v={video_id}'
        upload_date = item['snippet']['publishedAt']  # Get the upload date
        video_titles.append(video_title)
        video_links.append(video_link)
        upload_dates.append(upload_date)

    TL = pd.DataFrame({'title': video_titles, 'link': video_links, 'upload_date': upload_dates})
    TL['upload_date'] = pd.to_datetime(TL['upload_date'])  # Ensure datetime type
    TL['upload_date'] = TL['upload_date'].dt.tz_convert('Asia/Seoul')  # Convert to Seoul timezone
    TL['upload_date'] = TL['upload_date'].dt.tz_localize(None)  # Remove timezone information
    TL = TL.sort_values(by='upload_date', ascending=True)  # Sort by upload date
    TL.to_excel(excel_file, index=False)


def check_filename(type_of_video, filename):
    if '_K_' not in filename and '_E_' not in filename:
        raise Exception('File name check - language type')
    
    if '_K' in filename and '_E' in filename:
        raise Exception('File name check - language type')

    if '_13sec' in filename: 
        if '_shorts' not in filename: 
            raise Exception('13sec is shorts: add _shorts in filename')
        if '_13secs' in filename: 
            raise Exception('Use 13sec instead of 13secs')
    
    if '_shor' in filename.lower():
        if '_shorts' not in filename: 
            raise Exception('term _shorts has to be used - not capitalized')
    
    if '_13s' in filename.lower():
        if '_13sec' not in filename: 
            raise Exception('term _13sec has to be used - not capitalized')

    if '_shorts' in filename:  
        if '_13sec' in filename and type_of_video != 2:
            raise Exception('Video type check')
        elif '_13sec' not in filename and type_of_video != 1:
            raise Exception('Video type check')
    elif type_of_video !=0: 
        raise Exception('Video type check')

    try:
        DATE_GAP = 2 #days
        # date has to be yyyy-mm-dd format, e.g., 2024-12-01
        date = re.search(r"\d{4}-\d{2}-\d{2}", filename).group()
        valid_date = pd.to_datetime(date, format='%Y-%m-%d', errors='raise')
        if abs((valid_date - pd.Timestamp.now().normalize()).days) > DATE_GAP:
            raise Exception("Check Date: too apart from today")
    except ValueError:
        raise Exception('Date check: not correct')


def append_to_youtube_log(ppt_file, title, desc, keywords, id, type_of_video, log_file=YOUTUBE_LOG):
    if '_K_' in ppt_file:
        category = 'QP-Korean'
    elif '_E_' in ppt_file:
        category = 'IST-English'
    else:
        raise Exception('File name check')

    date = re.search(r"\d{4}-\d{2}-\d{2}", ppt_file).group()
    now = pd.Timestamp.now().strftime('%Y-%m-%d, %H:%M:%S')

    video_record = {
        'category': category,
        'type': type_of_video,
        'filename': os.path.basename(ppt_file),
        'date': date,
        'title': title,
        'desc': desc,
        'keywords': ", ".join(keywords),  # Joining list of keywords into a string
        'id': id,
        'log_time': now
    }

    # Check if the log file exists
    if os.path.exists(log_file):
        df = pd.read_excel(log_file)
    else:
        # Create a new DataFrame with the correct columns if the file doesn't exist
        df = pd.DataFrame(columns=video_record.keys())
    
    # Convert video_record to a DataFrame and append it
    new_row = pd.DataFrame([video_record])
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Save the updated DataFrame back to Excel
    df.to_excel(log_file, index=False)
