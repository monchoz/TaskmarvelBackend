from .transcribe import TranscribeApi, FileUploadApi

def initialize_routes(api):
    api.add_resource(TranscribeApi, '/api/transcribe')
    api.add_resource(FileUploadApi, '/api/upload')