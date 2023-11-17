from unspoken.services.ml.transcriber import TranscriberFactory

transcriber = TranscriberFactory.get_transcriber()

with open('sample.mp3', 'rb') as f:
    transcriber.transcribe(f)