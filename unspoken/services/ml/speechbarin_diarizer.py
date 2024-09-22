import logging
from io import BytesIO
from typing import List
from pathlib import Path

import numpy as np
import torch
import librosa
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
from speechbrain.inference import EncoderClassifier

from unspoken import exceptions
from unspoken.enitites.transcription import TranscriptionResult, TranscriptionSegment
from unspoken.enitites.speach_to_text import SpeachToTextResult
from unspoken.enitites.enums.ml_models import Model

logger = logging.getLogger(__name__)


class SpeechBrainSpeakerEmbedder:
    def __init__(self, device: str = 'cpu'):
        self.device = device
        local_model_path = Model.speechbrain.path()
        if not Path(local_model_path).exists():
            raise ValueError(
                f'Local model not found at {local_model_path}. Please run the model preparation step first.'
            )

        # Load pre-trained speaker recognition model
        self.classifier = EncoderClassifier.from_hparams(
            source=str(local_model_path),
            savedir=str(local_model_path),
            run_opts={'device': self.device},
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

        # Ensure we're returning a 1D numpy array
        embedding = embeddings.squeeze().cpu().detach().numpy()

        # If the embedding is still 2D, take the mean along the first dimension
        if embedding.ndim > 1:
            embedding = np.mean(embedding, axis=0)

        return embedding


def cluster_embeddings(embeddings: List[np.ndarray], max_speakers: int = 10) -> List[int]:
    """
    Cluster speaker embeddings to identify unique speakers.

    :param embeddings: List of speaker embeddings.
    :param max_speakers: Maximum number of speakers to consider.
    :return: List of cluster labels.
    """
    if not embeddings:
        return []

    embeddings = np.array(embeddings)

    # Try different numbers of clusters and choose the best one
    best_n_clusters = 2
    best_score = -1

    for n_clusters in range(2, min(max_speakers + 1, len(embeddings))):
        clustering = AgglomerativeClustering(n_clusters=n_clusters)
        labels = clustering.fit_predict(embeddings)
        score = silhouette_score(embeddings, labels)

        if score > best_score:
            best_score = score
            best_n_clusters = n_clusters

    # Use the best number of clusters
    final_clustering = AgglomerativeClustering(n_clusters=best_n_clusters)
    labels = final_clustering.fit_predict(embeddings)
    return labels


def assign_labels_to_short_segments(transcription_result: SpeachToTextResult) -> SpeachToTextResult:
    labeled_segments = [s for s in transcription_result.segments if s.speaker is not None]
    unlabeled_segments = [s for s in transcription_result.segments if s.speaker is None]

    for segment in unlabeled_segments:
        # Find the nearest labeled segments before and after
        prev_segment = next((s for s in reversed(labeled_segments) if s.end <= segment.start), None)
        next_segment = next((s for s in labeled_segments if s.start >= segment.end), None)

        if prev_segment and next_segment:
            if prev_segment.speaker == next_segment.speaker:
                segment.speaker = prev_segment.speaker
            else:
                # If surrounding speakers are different, choose the closer one
                if segment.start - prev_segment.end < next_segment.start - segment.end:
                    segment.speaker = prev_segment.speaker
                else:
                    segment.speaker = next_segment.speaker
        elif prev_segment:
            segment.speaker = prev_segment.speaker
        elif next_segment:
            segment.speaker = next_segment.speaker
        else:
            # If no labeled segments found, assign a default speaker
            segment.speaker = 'unknown_speaker'

    return transcription_result


class SpeechBrainDiarizer:
    def __init__(self, device: str = None):
        self.device = device if device else ('cuda' if torch.cuda.is_available() else 'cpu')
        self.embedder = SpeechBrainSpeakerEmbedder(device=self.device)

    def diarize_segments(self, wav_data: bytes, transcription_result: SpeachToTextResult) -> TranscriptionResult:
        audio, sr = librosa.load(BytesIO(wav_data), sr=None)

        embeddings = []
        valid_segments = []

        for segment in transcription_result.segments:
            start_sample = int(segment.start * sr)
            end_sample = int(segment.end * sr)
            segment_audio = audio[start_sample:end_sample]

            if len(segment_audio) < 400:  # Adjust this threshold as needed
                logger.warning(f'Segment {segment.id} is too short ({len(segment_audio)} samples). Skipping.')
                continue

            try:
                embedding = self.embedder.get_embedding(segment_audio, sr)
                embeddings.append(embedding)
                valid_segments.append(segment)
                logger.debug(f'Extracted embedding for segment {segment.id}: {segment.start}-{segment.end}s')
            except RuntimeError as e:
                logger.warning(f'Error processing segment {segment.id}: {str(e)}. Skipping.')
                continue

        if not embeddings:
            raise exceptions.NoDiarizedSegmentsError('No valid embeddings extracted. Cannot perform diarization.')

        labels = cluster_embeddings(embeddings)

        # Map cluster labels to speaker names
        unique_labels = set(labels)
        speaker_map = {label: f'Speaker_{label+1}' for label in unique_labels}

        # Create TranscriptionMessage objects
        messages = []
        for segment, label in zip(valid_segments, labels):
            speaker = speaker_map[label]
            message = TranscriptionSegment(text=segment.text, start=segment.start, end=segment.end, speaker=speaker)
            messages.append(message)

        # Create the final TranscriptionResult
        speakers = list(speaker_map.values())
        diarized_transcription = TranscriptionResult(messages=messages, speakers=speakers)

        # Assign labels to any skipped short segments
        diarized_transcription = self.assign_labels_to_short_segments(diarized_transcription, transcription_result)

        return diarized_transcription

    def assign_labels_to_short_segments(
        self, diarized_transcription: TranscriptionResult, original_transcription: SpeachToTextResult
    ) -> TranscriptionResult:
        diarized_messages = diarized_transcription.messages
        all_messages = []

        for segment in original_transcription.segments:
            matching_message = next(
                (m for m in diarized_messages if m.start == segment.start and m.end == segment.end), None
            )

            if matching_message:
                all_messages.append(matching_message)
            else:
                # This is a short segment that was skipped during diarization
                prev_message = next((m for m in reversed(all_messages) if m.end <= segment.start), None)
                next_message = next((m for m in diarized_messages if m.start >= segment.end), None)

                if prev_message and next_message:
                    speaker = (
                        prev_message.speaker
                        if segment.start - prev_message.end < next_message.start - segment.end
                        else next_message.speaker
                    )
                elif prev_message:
                    speaker = prev_message.speaker
                elif next_message:
                    speaker = next_message.speaker
                else:
                    speaker = 'unknown_speaker'

                new_message = TranscriptionSegment(
                    text=segment.text, start=segment.start, end=segment.end, speaker=speaker
                )
                all_messages.append(new_message)

        # Update speakers list if 'unknown_speaker' was added
        speakers = diarized_transcription.speakers
        if any(m.speaker == 'unknown_speaker' for m in all_messages) and 'unknown_speaker' not in speakers:
            speakers.append('unknown_speaker')

        return TranscriptionResult(messages=all_messages, speakers=speakers)
