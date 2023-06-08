import os
import subprocess
from typing import Iterator, TextIO


def str2bool(string):
    string = string.lower()
    str2val = {"true": True, "false": False}

    if string in str2val:
        return str2val[string]
    else:
        raise ValueError(
            f"Expected one of {set(str2val.keys())}, got {string}")


def format_timestamp(seconds: float, always_include_hours: bool = False, decimal_marker: str = '.'):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}{decimal_marker}{milliseconds:03d}"


def write_srt(transcript: Iterator[dict], file: TextIO):
    """
    Write a transcript to a file in SRT format.

    Example usage:
        from pathlib import Path
        from whisper.utils import write_srt

        result = transcribe(model, audio_path, temperature=temperature, **args)

        # save SRT
        audio_basename = Path(audio_path).stem
        with open(Path(output_dir) / (audio_basename + ".srt"), "w", encoding="utf-8") as srt:
            write_srt(result["segments"], file=srt)
    """
    for i, segment in enumerate(transcript, start=1):
        # write srt lines
        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True, decimal_marker=',')} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True, decimal_marker=',')}\n"
            f"{segment['text'].strip().replace('-->', '->')}\n",
            file=file,
            flush=True,
        )


def get_filename(path):
    return os.path.splitext(os.path.basename(path))[0]


def is_audio(path):
    return True if path.endswith(('.mp3', '.wav', '.flac', '.m4a', '.wma', '.aac')) else False


def ffmpeg_extract_audio(input_path, output_path):
    print(f"Extracting audio from {input_path}...")

     # Use ffprobe to get audio stream info
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'stream_tags=language', '-select_streams', 'a', '-of', 'csv=p=0', input_path]
    output = subprocess.check_output(cmd).decode('utf-8').strip()

    audio_stream_index = 1
    for idx, lang in enumerate(output.split('\n')):
        if "jpn" in lang:
            print("Found jpn audio!")
            audio_stream_index = idx + 1
            break

    if subprocess.run(('ffmpeg', '-y', '-i', input_path, '-map', "0:"+str(audio_stream_index), '-ac', '1', '-async', '1', output_path), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode > 0:
        raise Exception(f'Error occurred while extracting audio from {input_path}')
