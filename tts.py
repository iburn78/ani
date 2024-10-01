#%%
from google.cloud import texttospeech_v1beta1 as tts
import os
import json

with open('data/ppt/meta.json', 'r', encoding='utf-8') as json_file:
    meta = json.load(json_file)

ppt_file = os.path.join(meta['ppt_path'], meta['ppt_file'])
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '../config/google_cloud.json'
client = tts.TextToSpeechClient()
voice = tts.VoiceSelectionParams(
    language_code="en-US", 
    # name="en-US-Wavenet-B",  # WaveNet voice (1 mil words/month vs 4 mil in basic)
    # language_code="ko-KR",  
    # name="ko-KR-Wavenet-D",  
    ssml_gender=tts.SsmlVoiceGender.MALE
)
audio_config = tts.AudioConfig(
    audio_encoding=tts.AudioEncoding.MP3
)
timepoints = {}
for i in range(meta['txt_file_number']):
    txt_file = ppt_file.replace('.pptx', '_'+str(i+1)+'.txt')
    voice_file =ppt_file.replace('/ppt/','/voice/').replace('.pptx', '_'+str(i+1)+'.mp3')

    with open(txt_file, 'r', encoding='utf-8') as file:
        text_content = file.read()
    synthesis_input = tts.SynthesisInput(ssml=text_content)
    request = tts.SynthesizeSpeechRequest(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config, 
        enable_time_pointing=[tts.SynthesizeSpeechRequest.TimepointType.SSML_MARK]
    )
    response = client.synthesize_speech(request=request)

    with open(voice_file, "wb") as out:
        out.write(response.audio_content)
        print(voice_file + ' done')

    timepoint_list = []
    if response.timepoints:
        for time_point in response.timepoints:
            print(f'Mark name: {time_point.mark_name}, Time: {time_point.time_seconds} seconds')
            timepoint_list.append([int(time_point.mark_name[5:]), time_point.time_seconds])
    else:
        print('No timepoints found.')
    timepoints[voice_file] = timepoint_list

voice_meta = 'data/voice/voice_meta.json'
with open(voice_meta, 'w', encoding='utf-8') as timepoints_file:
    json.dump(timepoints, timepoints_file, ensure_ascii=False, indent=4)
