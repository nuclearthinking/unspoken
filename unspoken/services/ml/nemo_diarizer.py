import os
import json
import uuid
import shutil
from pathlib import Path

import torch.cuda
from omegaconf import OmegaConf
from nemo.collections.asr.models import NeuralDiarizer

from unspoken.settings import settings
from unspoken.enitites.diarization import DiarizationResult
from unspoken.services.ml.base_diarizer import BaseDiarizer


class NemoDiarizer(BaseDiarizer):
    def diarize(self, wav_data: bytes) -> DiarizationResult:
        torch.cuda.empty_cache()
        diarization_dir = Path.cwd() / 'diarization' / str(uuid.uuid4())
        try:
            diarization_dir.mkdir(parents=True, exist_ok=True)
            wav_file_path = self._write_wav(wav_data, diarization_dir / 'mono_file.wav')
            config = self._generate_config(diarization_dir, wav_file_path)
            model = NeuralDiarizer(cfg=config).to(settings.device)
            model.diarize()
            rmtt_data = (diarization_dir / 'pred_rttms' / 'mono_file.rttm').read_text(encoding='utf-8')
            result = self._parse_rmtt_data(rmtt_data)
        finally:
            shutil.rmtree(diarization_dir, ignore_errors=True)
        return result

    @staticmethod
    def _write_wav(wav_data: bytes, wav_path: Path):
        with open(wav_path, 'wb') as f:
            f.write(wav_data)
            f.flush()
        return wav_path

    @staticmethod
    def _write_manifest_file(output_dir: Path, audio_file_path: Path):
        with open(output_dir / 'input_manifest.json', 'w') as fp:
            json.dump(
                {
                    'audio_filepath': str(audio_file_path),
                    'offset': 0,
                    'duration': None,
                    'label': 'infer',
                    'text': '-',
                    'rttm_filepath': None,
                    'uem_filepath': None,
                },
                fp,
            )
            fp.write('\n')

    def _generate_config(self, output_dir: Path, source_audio_path: Path):
        config = OmegaConf.load(settings.nemo_domain_type.get_config_path())
        self._write_manifest_file(output_dir, source_audio_path)
        config.diarizer.manifest_filepath = os.path.join(output_dir, 'input_manifest.json')
        config.diarizer.out_dir = output_dir
        config.diarizer.vad.parameters.onset = 0.8  # 0.8
        config.diarizer.vad.parameters.offset = 0.6  # 0.6
        config.diarizer.vad.parameters.pad_offset = 0.05  # -0.05
        return config
