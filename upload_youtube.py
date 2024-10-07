#%%
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

# Replace with your client secrets file
CLIENT_SECRETS_FILE = "../config/google_client.json"

# Scopes required for the API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def upload_video(file_name, title, desc, category_id, keywords):
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
        media_body=file_name
    )
    
    response = request.execute()
    print(f"Video uploaded! Video ID: {response['id']}")


file_name = 'data\ppt\삼성전자_2024_2Q_E_2024-10-07_shorts01.mp4'
title = "Samsung Electronics: Undervalued or Overvalued?"
desc = '''
#SamsungElectronics #PER #Overvaluation #Undervaluation #Plunge
Looking at the PER in a time series over the past 2 years or 8 years and comparing it with the current PER, Samsung Electronics' stock price?
'''
category_id = "27" # education 
keywords=["PER Value", "Samsung"]

upload_video(file_name, title, desc, category_id, keywords)
