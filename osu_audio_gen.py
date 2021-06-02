import sys, os
import numpy as np
from pathlib import Path
from pydub import AudioSegment


def generate_audio(osufn, progress=None):
    osufn = Path(osufn)

    global_offset = 18  # milliseconds

    audiofn = "audio.mp3"

    kickfn = "kick.wav"
    hihatfn = "hihat.wav"
    clapfn = "clap.wav"

    with open(osufn) as f:
        lines = f.readlines()
        start = -1
        end = -1
        for i in range(len(lines)):
            if lines[i].startswith("AudioFilename: "):
                audiofn = osufn.parent/(' '.join(lines[i].strip().split(' ')[1:]))
            if lines[i].startswith("[TimingPoints]"):
                start = i
            elif start > 0 and lines[i].startswith("["):
                end = i
                break
        if start == -1:
            print("error: invalid .osu file")
            sys.exit()
        elif end == -1:
            end = len(lines)
        timing_points = [x.strip().split(',') for x in lines[start:end]]
        for i in range(len(timing_points)-1, -1, -1):
            if len(timing_points[i]) < 8 or not int(timing_points[i][6]):  # remove invalid lines and inherited timing points
                del timing_points[i]

    kick = AudioSegment.from_file(kickfn)
    hihat = AudioSegment.from_file(hihatfn)
    clap = AudioSegment.from_file(clapfn)

    audio = AudioSegment.silent(duration=len(AudioSegment.from_file(audiofn)))

    kicks = []
    hihats = []
    claps = []
    # offset in ms, beat length, beats per measure, sound set, idk, volume, inherited, flags
    # generate beat timestamps
    l = len(timing_points)
    for i in range(len(timing_points)):
        if progress is not None:
            progress.emit(int(i/l*10))
        offset = float(timing_points[i][0])
        next_offset = float(timing_points[i+1][0]) if i < len(timing_points)-1 else len(audio)
        beat_length = float(timing_points[i][1])
        beats_per_measure = int(timing_points[i][2])
        
        if beats_per_measure == 4:
            kicks += list(np.arange(offset + global_offset, next_offset + global_offset, beat_length*2))
            hihats += list(np.arange(offset + beat_length/2 + global_offset, next_offset + global_offset, beat_length))
            claps += list(np.arange(offset + beat_length + global_offset, next_offset + global_offset, beat_length*2))
        elif beats_per_measure == 2:
            kicks += list(np.arange(offset + global_offset, next_offset + global_offset, beat_length))
            hihats += list(np.arange(offset + beat_length/2 + global_offset, next_offset + global_offset, beat_length))
        else:
            kicks += list(np.arange(offset + global_offset, next_offset + global_offset, beat_length*beats_per_measure))
            hihats += list(np.arange(offset + beat_length + global_offset, next_offset + global_offset, beat_length))
    
    i = 0
    l = len(kicks)+len(hihats)+len(claps)
    for pos in kicks:
        audio = audio.overlay(kick, position=int(pos))
        if progress is not None:
            progress.emit(10+int(i/l*90))
        i += 1
    for pos in hihats:
        audio = audio.overlay(hihat, position=int(pos))
        if progress is not None:
            progress.emit(10+int(i/l*90))
        i += 1
    for pos in claps:
        audio = audio.overlay(clap, position=int(pos))
        if progress is not None:
            progress.emit(10+int(i/l*90))
        i += 1

    os.rename(audiofn, f"{audiofn}.bak")
    audio.export(audiofn)
    
    if progress is not None:
        progress.emit(100)