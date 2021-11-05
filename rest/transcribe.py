
# Imports the Google Cloud client library
import io
import os
from google.cloud import speech
from google.oauth2 import service_account
from os.path import splitext
from pydub import AudioSegment
from flask import Response, request
from flask_restful import Resource
from dotenv import load_dotenv
load_dotenv()


SERVICE_ACCOUNT_FILE = os.environ.get("GAC_FILE")
cred = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
# Instantiates a client
client = speech.SpeechClient(credentials=cred)

# The name of the audio file to transcribe
speech_file = "male.wav"


def wav2flac(wav_path):
    flac_path = "%s.flac" % splitext(wav_path)[0]
    song = AudioSegment.from_file(wav_path)
    song.export(flac_path, format = "flac")
    return flac_path


class TranscribeApi(Resource):
    def post(self):
        body = request.get_json()
        speech_file = body["fileName"]
        speech_lang = body["lang"]

        with io.open(wav2flac(speech_file), "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
            sample_rate_hertz=48000,
            language_code=speech_lang,
            audio_channel_count=2,
            enable_separate_recognition_per_channel=True,
            use_enhanced=True,
            model="command_and_search"
        )

        # Detects speech in the audio file
        # response = client.long_running_recognize(config=config, audio=audio)
        response = client.recognize(config=config, audio=audio)

        transcript_results = ""

        for i, result in enumerate(response.results):
            alternative = result.alternatives[0]
            print("-" * 20)
            print("First alternative of result {}".format(i))
            print(u"Transcript: {}".format(alternative.transcript))
            print(u"Channel Tag: {}".format(result.channel_tag))
            transcript_results = alternative.transcript

        return transcript_results, 200