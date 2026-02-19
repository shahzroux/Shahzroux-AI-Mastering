import pedalboard
from pedalboard import Pedalboard, Compressor, HighpassFilter, LowShelfFilter, Limiter, Distortion, Clipping, Reverb, NoiseGate
from pedalboard.io import AudioFile
import essentia.standard as es
import numpy as np
import pyloudnorm as pyln

class ShahzrouxEngine:
    def __init__(self):
        self.target_tp = -1.0 # Standard True Peak untuk Streaming [cite: 184]

    def analyze_jiwang_factor(self, audio_data):
        # Gunakan Essentia untuk kesan BPM [cite: 173, 228]
        audio_mono = np.mean(audio_data, axis=0) if audio_data.ndim > 1 else audio_data
        rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
        bpm, _, _, _, _ = rhythm_extractor(audio_mono)
        
        # Adaptive Logic: Bawah 85 BPM dikira 'Jiwang' [cite: 175, 239]
        if bpm < 85:
            return "jiwang", 500  # Slow release untuk rasa sustain [cite: 232]
        else:
            return "rock", 100    # Fast release untuk rasa punchy [cite: 231]

    def process_audio(self, input_path, output_path):
        with AudioFile(input_path) as f:
            audio = f.read(f.frames)
            sr = f.samplerate

        genre, release_ms = self.analyze_jiwang_factor(audio)
        board = Pedalboard()

        # 1. Analog Warmth (Tape & Tube Saturation) [cite: 188, 189]
        board.append(Clipping(threshold_db=-1.5)) 
        board.append(Distortion(drive_db=1.0))

        # 2. Nusantara EQ (Mid-Range Presence) [cite: 195, 196]
        board.append(HighpassFilter(cutoff_frequency_hz=30)) [cite: 181]
        board.append(LowShelfFilter(cutoff_frequency_hz=400, gain_db=1.5)) [cite: 197]

        # 3. Adaptive "Glue" Compression [cite: 199, 200]
        board.append(Compressor(
            threshold_db=-18, 
            ratio=3 if genre=="rock" else 2, 
            attack_ms=30, 
            release_ms=release_ms
        ))

        # 4. Final Limiting & Safety Check [cite: 217, 219]
        board.append(Limiter(threshold_db=-1.0))
        processed = board(audio, sr)
        
        # True Peak Correction menggunakan pyloudnorm [cite: 221, 222]
        meter = pyln.Meter(sr)
        curr_tp = meter.measure_true_peak(processed.transpose())
        if curr_tp > self.target_tp:
            gain_factor = 10 ** ((self.target_tp - curr_tp) / 20)
            processed *= gain_factor

        with AudioFile(output_path, 'w', sr, processed.shape) as o:
            o.write(processed)
        
        return output_path
