import logging

import torch

from unspoken import exceptions
from unspoken.services import db
from unspoken.core.loader import prepare_models
from unspoken.enitites.diarization import DiarizationResult
from unspoken.enitites.transcription import TranscriptionResult
from unspoken.enitites.speach_to_text import SpeachToTextResult
from unspoken.services.ml.transcriber import Transcriber
from unspoken.services.audio.converter import convert_to_wav, preprocess_audio
from unspoken.enitites.enums.task_status import TaskStatus
from unspoken.services.ml.speechbarin_diarizer import SpeechBrainDiarizer
from unspoken.services.annotation.annotate_transcription import annotate, annotate_dtw

logger = logging.getLogger('uvicorn')


def clear_cuda_cache(func):
    def wrapper(*args, **kwargs):
        torch.cuda.empty_cache()

        result = func(*args, **kwargs)

        torch.cuda.synchronize()
        torch.cuda.empty_cache()

        return result

    return wrapper


def _convert_audio(source_file_data: bytes):
    wav_data = convert_to_wav(source_file_data)
    return wav_data


@clear_cuda_cache
def _transcribe_audio(wav_data: bytes) -> SpeachToTextResult:
    result = Transcriber().transcribe(wav_data)
    return result


def annotate_transcription(
    stt_result: SpeachToTextResult,
    diarization_result: DiarizationResult,
) -> TranscriptionResult:
    return annotate_dtw(stt_result, diarization_result)
    return annotate(stt_result, diarization_result)


def _save_to_database(
    task_id: int,
    annotated_transcription: TranscriptionResult,
    diarization_result: DiarizationResult,
    transcription_result: SpeachToTextResult,
) -> None:
    with db.Session() as session:
        task = db.get_task(task_id, session)
        if not task:
            raise exceptions.TaskNotFoundError(f'Task with id: {task_id} was not found.')

        db.save_transcription_result(
            task.transcript_id,
            annotated_transcription.model_dump(),
            session=session,
        )
        db.save_diarization_result(
            task.transcript_id,
            result=diarization_result.model_dump(),
            session=session,
        )
        db.save_speach_to_text_result(
            task.transcript_id,
            result=transcription_result.model_dump(),
            session=session,
        )
        logger.info('Saving speakers to database.')
        speakers = dict()
        for speaker in diarization_result.speakers:
            created_speaker = db.create_speaker(
                name=speaker,
                task_id=task.id,
                session=session,
            )
            speakers[speaker] = created_speaker.id
        logger.info('Saved %s speakers.', len(speakers.keys()))
        logger.info('Saving messages to database.')
        messages_to_save = []
        for message in annotated_transcription.messages:
            speaker_id = None
            if message.speaker in speakers:
                speaker_id = speakers[message.speaker]
            messages_to_save.append(
                db.Message(
                    speaker_id=speaker_id,
                    task_id=task.id,
                    text=message.text,
                    start_time=message.start,
                    end_time=message.end,
                )
            )
        db.save_messages(messages_to_save, session=session)
    logger.info('Saved %s messages.', len(messages_to_save))


def transcribe_audio_flow(temp_file_id: int, task_id: int):
    logger.info('Initializing models.')
    prepare_models()
    logger.info('Models initialized.')

    logger.info('Starting transcription flow for task %s.', task_id)
    temp_file = db.get_temp_file(temp_file_id)
    if not temp_file:
        logger.error('Not found temporary file with id: %s.', temp_file_id)
        raise exceptions.TempFileNotFoundError(f'Temp file with id {temp_file_id} not found.')
    task = db.get_task(task_id)
    if not task:
        logger.error('Task with id: %s was not found.', task_id)
        temp_file.delete()
        raise exceptions.TaskNotFoundError(f'Task with id: {task_id} was not found.')
    try:
        db.update_task(task, status=TaskStatus.processing)
        logger.info('Converting audio for tmp_file_id %s.', temp_file_id)
        wav_data = convert_to_wav(source_data=temp_file.read())

        logger.info('Reducing noises ')
        preprocessed_audio = preprocess_audio(wav_data=wav_data)

        logger.info('Transcribing audio for task_id %s.', task_id)
        transcription = _transcribe_audio(preprocessed_audio)

        logger.info('Diarizing audio for task_id %s.', task_id)
        diarizer = SpeechBrainDiarizer()
        diarized_transcription = diarizer.diarize_segments(preprocessed_audio, transcription)

        logger.info('Saving results for task_id %s.', task_id)
        _save_to_database(
            task_id=task_id,
            transcription_result=diarized_transcription,
        )
        db.update_task(task, status=TaskStatus.completed)
        logger.info('Transcription flow completed for task %s.', task_id)
    except Exception:
        logger.exception('Exception occurred during running transcription flow.')
        db.update_task(task, status=TaskStatus.failed)
        raise
    finally:
        temp_file.delete()
