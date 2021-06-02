# osu-safety-tools
tools to genericize osu! maps (replacing background and audio)

If you want to remove (inappropriate) background images or replace audio with a drum loop (for legal/moral reasons or because you think a song is annoying) then look no further; this tool allows you to generate a plain background image for a beatmap containing the title, artist and difficulty. The tool also can automatically replace audio with a drum loop that is synchronized to the timing in an .osu file.

To replace the audio you must supply a `kick.wav`, `hihat.wav` and `clap.wav` file. You can use other file formats but you will have to replace the filenames listed in `osu_audio_gen.py`. To run the GUI program, simply start `run.bat` or open `main.py` with admin privileges. Dependencies are in requirements.txt, but if you have issues you may need to install `simpleaudio` as well. This code is written for Python 3 and will likely not work with Python 2 without a few changes.

`dbparse.py` is taken from https://github.com/chudooder/osutools and all rights are reserved to @chudooder. Any other script is available under the MIT License which is included.
