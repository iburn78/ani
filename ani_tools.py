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
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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
    elif type=='post':
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

def _get_desc(input_text, conf_file):
    with open(conf_file, 'r') as json_file:
        config = json.load(json_file)
        api_key = config['openai']

    client = OpenAI(api_key=api_key)
    content_command = '''
YouTube video script. Respond exactly in this format:

line 1: Korean title
line 2: Korean hash tags top 10 with the hash
line 3: Korean description up to 60 words
line 4: English title
line 5: English hash tags top 10 with the hash
line 3: English description up to 60 words

Use new lines without format keywords or quotes. For hash tags, remove spaces, capitalize the first letter of each word.

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

def get_desc(input_text, conf_file): 
    res = _get_desc(input_text, conf_file)
    res = "\n".join(line for line in res.splitlines() if line.strip()).splitlines()

    if len(res) != 6:
        print(res)
        raise Exception('Error in ChatGPT response and/or get_desc function')

    K_title = res[0]
    K_tags = res[1]
    K_desc = res[2]
    E_title = res[3]
    E_tags = res[4]
    E_desc = res[5]

    print(K_title)
    print(K_tags)
    print(K_desc)
    print(E_title)
    print(E_tags)
    print(E_desc)

    return None


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

def translate_title_desc(title, desc, conf_file): 
    translated_title = _translate_text(title, conf_file, 'title')
    translated_desc = _translate_text(desc, conf_file, 'desc')
    return translated_title, translated_desc

def translate_script(script, conf_file):
    return _translate_text(script, conf_file, 'post')

def upload_video(meta: Meta, title, desc, keywords, thumbnail_file=None, category_id = '27', client_secrets_file = None, playlist_id = None): # '27': education
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


def get_ids(client_secrets_file):
    SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, SCOPES)
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
    
    # Extract playlist IDs and titles
    playlists = [(item['id'], item['snippet']['title']) for item in response.get('items', [])]
    return channel_id, playlists

# CLIENT_SECRETS_FILE = "../config/google_client.json"
# channel_id, playlists = get_ids(CLIENT_SECRETS_FILE)
# print(f"Channel ID: {channel_id}")

# for playlist_id, title in playlists:
#     print(f"Playlist ID: {playlist_id}, Title: {title}")


class IST:  # IssueTracker Handler
    IST_SITE = 'https://issuetracker.info/'
    CONF_FILE = '../config/config.json'

    def __init__(self):
        self.session = requests.Session()
        self.login()

    def _get_csrf_token(self, url):
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token_input = soup.find("input", {"name": "csrfmiddlewaretoken"})
        self.csrf_token = csrf_token_input["value"] if csrf_token_input else None

    def login(self):
        login_url = urljoin(IST.IST_SITE, 'login/')
        self._get_csrf_token(login_url)

        with open(IST.CONF_FILE, 'r') as json_file:
            config = json.load(json_file)
            self.ist_id = config['issuetracker_id']
            ist_pass = config['issuetracker_pass']

        form_data = {
            "username": self.ist_id,
            "password": ist_pass,
            "csrfmiddlewaretoken": self.csrf_token,
        }
        headers = {
            "Referer": login_url,  # Required by CSRF protection
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        }

        response = self.session.post(login_url, data=form_data, headers=headers)
        if response.status_code != 200:
            raise Exception('IST login failed')


    def create_post(self, card_id: int, form_data: dict, images: list = [], html=False):
        target_url = urljoin(IST.IST_SITE, f'card/{card_id}/new_post/')
        self._get_csrf_token(target_url)

        form_data['csrfmiddlewaretoken'] = self.csrf_token
        lm = len(images)
        if lm > 10: 
            raise Exception('Only up to 10 images can be posted')
        mimage_str = 'abcdefghij'
        form_data['mimage_keys'] = mimage_str[:lm].upper() + mimage_str[lm:]
        if html:
            form_data['html_or_text'] = 'html'

        files = {}
        for i, im in enumerate(images):
            if not os.path.exists(im):
                raise Exception(f"image {im} does not exist")
            files[f'image{i+1}_input'] = (os.path.basename(im), open(im, 'rb'))

        headers = {
            "Referer": target_url,  # Required by CSRF protection
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        }
        response = self.session.post(target_url, data=form_data, files=files, headers=headers)

        # Close the image files after the POST request
        for _,file in files.items():
            file[1].close()

        if response.status_code == 200:
            print(f"Post{' ['+form_data['title']+']' if 'title' in form_data else ''}{' ('+str(lm)+' images)' if lm>0 else ''} created.")
            return None
        else:
            print(f"Post{' ['+form_data['title']+']' if 'title' in form_data else ''}{' ('+str(lm)+' images)' if lm>0 else ''} creation FAILED.")
            return response.text

# assumes youtube_conf
# import pandas in the function
def get_title_link(conf_file, excel_file):
    import pandas as pd

    with open(conf_file, 'r') as json_file:
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