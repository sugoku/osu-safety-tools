# osu-safety-tools
tools to genericize osu! maps (replacing background and audio)

If you want to remove background images or replace audio with a drum loop (for legal reasons or because you think a song is annoying) then look no further; this tool allows you to generate a plain background image for a beatmap containing the title, artist and difficulty. The tool also can automatically replace audio with a drum loop that is synchronized to the timing in an .osu file.

To replace the audio you must supply a `kick.wav`, `hihat.wav` and `clap.wav` file. You can use other file formats but you will have to replace the filenames listed in `osu_audio_gen.py`. To run the GUI program, simply start `run.bat` or open `main.py` with admin privileges. Dependencies are in requirements.txt, but if you have issues you may need to install `simpleaudio` as well. This code is written for Python 3 and will likely not work with Python 2 without a few changes.

To replace background images, the default font used is `cmunssdc.ttf` (Computer Modern) which is included under the [SIL Open Font License 1.1](https://opensource.org/licenses/OFL-1.1), but this can be changed in `osubg.py`.

`dbparse.py` is taken from https://github.com/chudooder/osutools and ported to Python 3; all rights are reserved to @chudooder. `osubg.py` is partially based on a snippet of code based on a StackOverflow response which can be found [here](https://stackoverflow.com/a/49581617), and thus that section of the code is under the [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) license. Any other code is available under the MIT License which is included.
