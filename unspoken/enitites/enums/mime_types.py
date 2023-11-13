from enum import Enum


class MimeType(Enum):
    m4a = 'audio/x-m4a'
    aac = 'audio/aac'
    mp3 = 'audio/mpeg'
    wav = 'audio/wav'

    unknown = None

    @classmethod
    def _missing_(cls, value):
        return MimeType.unknown

    def is_audio(self) -> bool:
        return self in [
            self.m4a,
            self.aac,
            self.mp3,
            self.wav,
        ]
