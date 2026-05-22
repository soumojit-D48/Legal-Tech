import os
import uuid
import subprocess
from faster_whisper import WhisperModel


MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")

model = WhisperModel(
    MODEL_SIZE,
    device="cpu",
    compute_type="int8"
)


class VoiceService:

    @staticmethod
    def convert_to_wav(input_path: str, output_path: str):

        ffmpeg_path = r"C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin\ffmpeg.exe"

        command = [
            ffmpeg_path,
            "-y",
            "-i",
            input_path,
            "-ar",
            "16000",
            "-ac",
            "1",
            output_path
        ]

        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    @staticmethod
    def transcribe(input_path: str):

        wav_path = f"{uuid.uuid4()}.wav"

        VoiceService.convert_to_wav(input_path, wav_path)

        segments, info = model.transcribe(
            wav_path,
            beam_size=5
        )

        transcript_parts = []
        segment_data = []

        for segment in segments:

            transcript_parts.append(segment.text)

            segment_data.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })

        transcript = " ".join(transcript_parts)

        os.remove(wav_path)

        return {
            "transcript": transcript,
            "language": info.language,
            "confidence": round(info.language_probability, 3),
            "segments": segment_data
        }