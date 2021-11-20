
# Imports the Google Cloud client library
import os
import proto
from google.cloud import speech, storage
from google.oauth2 import service_account
from os.path import splitext
from pydub import AudioSegment
from flask import request
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
        """Transcribe the given audio file."""
        print("🤖 Transcribing from audio...")
        audio = speech.RecognitionAudio(uri="gs://" + os.environ.get("GS_BUCKET") + "/" + file_name)

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
        
        for i, result in enumerate(response.results):
            alternative = result.alternatives[0]
            print("-" * 20)
            print("⭐ First alternative of result {}".format(i))
            print(u"⭐ Transcript: {}".format(alternative.transcript))
            print(u"⭐ Channel Tag: {}".format(result.channel_tag))

        return proto.Message.to_dict(response)
        

# function to upload file to google cloud storage
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('🤖 File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))


class FileUploadApi(Resource):
    def post(self):
        try:
            uploaded_file = request.files['file']
            if uploaded_file.filename != '':
                # save file to disk
                file_path = RECORDINGS + uploaded_file.filename
                uploaded_file.save(file_path)
                # convert to flac
                flac_path = wav2flac(file_path)
                file_name = os.path.basename(flac_path)
            # upload local file to google cloud storage
            print("🤖 Uploading file to google cloud storage...")
            upload_blob("tm-recordings", flac_path, file_name)
            # transcribe file
            return transcribe_from_audio(file_name, "en-US"), 200
        except Exception as err:
            print(err)
            return "🛑 File upload went wrong", 500


class TranscribeApi(Resource):
    def post(self):
        body = request.get_json()
        speech_file = body["fileName"]
        speech_lang = body["lang"]

        return transcribe_from_audio(speech_file, speech_lang), 200