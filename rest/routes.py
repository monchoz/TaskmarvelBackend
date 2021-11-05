from .transcribe import TranscribeApi

def initialize_routes(api):
    api.add_resource(TranscribeApi, '/api/transcribe')