from __future__ import annotations

import numpy as np
import essentia.standard as es
import pyloudnorm as pyln
from pedalboard import (
    Clipping,
    Compressor,
    Distortion,
    HighpassFilter,
    Limiter,
    LowShelfFilter,
    Pedalboard,
)
from pedalboard.io import AudioFile


class ShahzrouxEngine:
    """Audio mastering engine with adaptive dynamics and peak safety."""

    def __init__(self, target_tp: float = -1.0):
        self.target_tp = target_tp

    def analyze_jiwang_factor(self, audio_data: np.ndarray) -> tuple[str, int]:
        """Detect a rough song feel from BPM and return profile + release time."""
        audio_mono = np.mean(audio_data, axis=0) if audio_data.ndim > 1 else audio_data
        rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
        bpm, _, _, _, _ = rhythm_extractor(audio_mono)

        if bpm < 85:
            return "jiwang", 500
        return "rock", 100

    def _warmth_gain(self, warmth: int) -> tuple[float, float]:
        """Map UI warmth (0-100) into clipping and distortion settings."""
        warmth = int(np.clip(warmth, 0, 100))
        clipping_threshold = -3.0 + (warmth / 100.0) * 2.0  # -3 dB .. -1 dB
        distortion_drive = 0.5 + (warmth / 100.0) * 2.5  # 0.5 dB .. 3 dB
        return clipping_threshold, distortion_drive

    def process_audio(self, input_path: str, output_path: str, warmth: int = 75) -> str:
        with AudioFile(input_path) as f:
            audio = f.read(f.frames)
            sr = f.samplerate

        genre, release_ms = self.analyze_jiwang_factor(audio)
        clip_threshold, drive_db = self._warmth_gain(warmth)

        board = Pedalboard(
            [
                Clipping(threshold_db=clip_threshold),
                Distortion(drive_db=drive_db),
                HighpassFilter(cutoff_frequency_hz=30),
                LowShelfFilter(cutoff_frequency_hz=400, gain_db=1.5),
                Compressor(
                    threshold_db=-18,
                    ratio=3 if genre == "rock" else 2,
                    attack_ms=30,
                    release_ms=release_ms,
                ),
                Limiter(threshold_db=self.target_tp),
            ]
        )

        processed = board(audio, sr)

        meter = pyln.Meter(sr)
        curr_tp = meter.measure_true_peak(processed.T)
        if curr_tp > self.target_tp:
            gain_factor = 10 ** ((self.target_tp - curr_tp) / 20)
            processed *= gain_factor

        with AudioFile(output_path, "w", sr, processed.shape[0]) as o:
            o.write(processed)

        return output_path
