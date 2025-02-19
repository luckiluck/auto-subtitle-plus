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


def format_timestamp(seconds: float, always_include_hours: bool = False):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def write_srt(transcript: Iterator[dict], file: TextIO):
    for i, segment in enumerate(transcript, start=1):
        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True)} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True)}\n"
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
    if subprocess.run(('ffmpeg', '-y', '-i', input_path, '-ac', '1', '-async', '1', output_path), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode > 0:
        raise Exception(f'Error occurred while extracting audio from {input_path}')
