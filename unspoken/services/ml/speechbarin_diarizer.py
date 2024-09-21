import time
import logging
from io import BytesIO
from typing import List

import numpy as np
import torch
import librosa
from sklearn.cluster import AgglomerativeClustering
from speechbrain.inference import EncoderClassifier

from unspoken.settings import settings
from unspoken.enitites.speach_to_text import SpeachToTextSegment, SpeachToTextResult
from unspoken.enitites.enums.ml_models import Model

logger = logging.getLogger(__name__)


class SpeechBrainSpeakerEmbedder:
    def __init__(self, device: str = 'cpu'):
        self.device = device
        # Load pre-trained speaker recognition model
        self.classifier = EncoderClassifier.from_hparams(
            source='speechbrain/spkrec-ecapa-voxceleb',
            savedir=settings.models_dir_path,
            run_opts={'device': self.device},
            hparams_file=Model.speechbrain.path(),
        )

    def get_embedding(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Extract speaker embedding from audio.

        :param audio: Audio signal as a NumPy array.
        :param sample_rate: Sampling rate of the audio.
        :return: Speaker embedding as a NumPy array.
        """
        # Ensure audio is float32
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        # Normalize audio
        audio = librosa.util.normalize(audio)

        # Convert to torch tensor and add batch dimension
        audio_tensor = torch.from_numpy(audio).unsqueeze(0).to(self.device)

        # Extract embedding
        embeddings = self.classifier.encode_batch(audio_tensor)
        return embeddings.squeeze(0).cpu().detach().numpy()


def cluster_embeddings(embeddings: List[np.ndarray], distance_threshold: float = 1.0) -> List[int]:
    """
    Cluster speaker embeddings to identify unique speakers.

    :param embeddings: List of speaker embeddings.
    :param distance_threshold: Distance threshold for clustering.
    :return: List of cluster labels.
    """
    if not embeddings:
        return []

    embeddings = np.array(embeddings)
    clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=distance_threshold)
    labels = clustering.fit_predict(embeddings)
    return labels


class SpeechBrainDiarizer:
    def __init__(self, device: str = None):
        self.device = device if device else ('cuda' if torch.cuda.is_available() else 'cpu')
        self.embedder = SpeechBrainSpeakerEmbedder(device=self.device)

    def diarize_segments(self, wav_data: bytes, transcription_result: SpeachToTextResult) -> SpeachToTextResult:
        """
        Perform diarization on transcription segments.

        :param wav_data: Audio data in bytes.
        :param transcription_result: SpeachToTextResult object from transcription.
        :return: Updated SpeachToTextResult object with speaker labels.
        """
        start_time_overall = time.time()

        # Load audio from bytes
        audio, sr = librosa.load(BytesIO(wav_data), sr=16000)

        # Extract embeddings for each transcription segment
        embeddings = []
        valid_segments = []
        for segment in transcription_result.segments:
            start_sample = int(segment.start * sr)
            end_sample = int(segment.end * sr)
            segment_audio = audio[start_sample:end_sample]

            if len(segment_audio) == 0:
                logger.warning(f'Segment {segment.id} has zero length. Skipping.')
                continue

            embedding = self.embedder.get_embedding(segment_audio, sr)
            embeddings.append(embedding)
            valid_segments.append(segment)

            logger.debug(f'Extracted embedding for segment {segment.id}: {segment.start}-{segment.end}s')

        if not embeddings:
            logger.warning('No valid segments found for diarization.')
            return transcription_result

        # Cluster embeddings to identify speakers
        labels = cluster_embeddings(embeddings)
        logger.info(f'Clustering resulted in {len(set(labels))} speakers.')

        # Assign speaker labels to segments
        speakers = set()
        for segment, label in zip(valid_segments, labels):
            speaker = f'speaker_{label + 1}'
            speakers.add(speaker)
            segment.speaker = speaker

        transcription_result.speakers = list(speakers)
        end_time_overall = time.time()
        diarization_time = end_time_overall - start_time_overall
        logger.info(f'SpeechBrain diarization completed in {diarization_time:.3f} seconds.')

        return transcription_result
