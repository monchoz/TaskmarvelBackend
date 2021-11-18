
# Imports the Google Cloud client library
import io
import os
from google.cloud import speech, storage
from google.oauth2 import service_account
from os.path import splitext
from pydub import AudioSegment
from flask import Response, request
from flask_restful import Resource
from dotenv import load_dotenv
load_dotenv()


RECORDINGS = "recordings/"
SERVICE_ACCOUNT_FILE = os.environ.get("GAC_FILE")
cred = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
# Instantiates a client
client = speech.SpeechClient(credentials=cred)
storage_client = storage.Client(credentials=cred)


def wav2flac(wav_path):
    flac_path = "%s.flac" % splitext(wav_path)[0]
    song = AudioSegment.from_file(wav_path)
    song.export(flac_path, format = "flac")
    return flac_path


def transcribe_from_audio(file_name, lang):
        with io.open(wav2flac(RECORDINGS + file_name), "rb") as audio_file:
                content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
            sample_rate_hertz=48000,
            language_code=lang,
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

        return transcript_results


# function to upload file to google cloud storage
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))


class FileUploadApi(Resource):
    def post(self):
        try:
            """ uploaded_file = request.files['file']
            if uploaded_file.filename != '':
                file_path = RECORDINGS + uploaded_file.filename
                 uploaded_file.save(file_path)"""
            #upload_blob("tm-recordings", file_path, uploaded_file.filename)
            upload_blob("tm-recordings", "recordings/Taskmarvel_recording_1636403191022.flac", "Taskmarvel_recording_1636403191022")
                #return transcribe_from_audio(uploaded_file.filename, "en-US"), 200
            return "done", 200
        except Exception as err:
            print(err)
            return "File upload went wrong", 500


class TranscribeApi(Resource):
    def post(self):
        body = request.get_json()
        speech_file = body["fileName"]
        speech_lang = body["lang"]

        return transcribe_from_audio(speech_file, speech_lang), 200