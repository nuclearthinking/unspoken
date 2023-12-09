from enum import Enum


class MimeType(str, Enum):
    m4a = 'audio/x-m4a'
    aac = 'audio/aac'
    mp3 = 'audio/mpeg'
    wav = 'audio/wav'
    mp4 = 'video/mp4'

    unknown = None

    @classmethod
    def _missing_(cls, value):
        return MimeType.unknown

    def is_supported(self) -> bool:
        return self in [
            self.m4a,
            self.aac,
            self.mp3,
            self.wav,
            self.mp4,
        ]
