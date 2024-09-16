from abc import abstractmethod

from unspoken.core.singleton import SingletonABCMeta
from unspoken.enitites.diarization import DiarizationResult, SpeakerSegment


class BaseDiarizer(metaclass=SingletonABCMeta):
    @abstractmethod
    def diarize(self, wav_data: bytes) -> DiarizationResult:
        raise NotImplementedError

    @staticmethod
    def _parse_rmtt_data(rmtt_data: str) -> DiarizationResult:
        speakers = set()
        result = DiarizationResult()
        for id_, line in enumerate(filter(bool, rmtt_data.splitlines()), start=1):
            words = list(filter(bool, line.split()))
            start, duration, speaker = words[3], words[4], words[7]
            speakers.add(speaker)
            result.segments.append(
                SpeakerSegment(
                    id=id_,
                    start=float(start),
                    end=float(start) + float(duration),
                    speaker=speaker,
                    duration=duration,
                )
            )
        result.speakers = list(speakers)
        result.speakers_count = len(speakers)
        return result
