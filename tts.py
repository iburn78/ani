#%%
from google.cloud import texttospeech
import os


ppt_file = 'data/ppt/삼성전자_2024_2Q_E_2024-09-30.pptx'
txt_file_base = ppt_file.replace('.pptx', '')
txt_file_num = f"{txt_file_base}_num.txt"
with open(txt_file_num, 'r', encoding='utf-8') as file:
    num = int(file.read()) 

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '../config/google_cloud.json'
client = texttospeech.TextToSpeechClient()
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US", 
    name="en-US-Wavenet-B",  # WaveNet voice (1 mil words/month vs 4 mil in basic)
    # language_code="ko-KR",  
    # name="ko-KR-Wavenet-D",  
    ssml_gender=texttospeech.SsmlVoiceGender.MALE
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

for i in range(num):
    txt_file = 'data/ppt/삼성전자_2024_2Q_E_2024-09-30.txt'.replace('.txt', '_'+str(i+1)+'.txt')
    voice_file =ppt_file.replace('/ppt/','/voice/').replace('.pptx', '_'+str(i+1)+'.mp3')

    with open(txt_file, 'r', encoding='utf-8') as file:
        text_content = file.read()

    text_input = texttospeech.SynthesisInput(ssml=text_content)
    response = client.synthesize_speech(input=text_input, voice=voice, audio_config=audio_config)

    with open(voice_file, "wb") as out:
        out.write(response.audio_content)
        print(voice_file + ' done')

