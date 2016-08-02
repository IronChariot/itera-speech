# Looks in the /toconvert folder, finds all files starting with arg1
# converts them into .wav files with the name 'arg2-book-N.wav'
# and then merges the .wav files together into a single file named 'arg2-book.wav'
# arg1: prefix of current audiobook files
# arg2: desired short name for book (e.g. title initials)

import os
import sys
import subprocess

FRAMERATE = 16000

assert len(sys.argv) == 3  # Script name, arg1 and arg2 as described in docstring
data_contents = os.listdir("./toconvert")
input_filenames = ["toconvert/" + n
                   for n in data_contents
                   if (n.startswith(sys.argv[1]))]
input_filenames.sort()

wav_index = 0
wav_name = sys.argv[2]
wav_files = []

# Convert all mp3 files to wav files:
for filename in input_filenames:
    print "mpg123 -r {} -mw data/{}-{}.wav {}".format(FRAMERATE, filename, wav_name, wav_index)
    if subprocess.call("mpg123 -r {} -mw data/{}-{}.wav {}".format(FRAMERATE, wav_name, wav_index, filename), shell=True):
        print "An error occurred!"
    os.remove(filename)
    wav_files.append("data/{}-{}.wav".format(wav_name, wav_index))
    wav_index += 1

# Merge wav files into one:
sox_argument_string = ' '.join(wav_files) + " data/{}-book.wav".format(wav_name)
print "sox " + sox_argument_string
subprocess.call("sox " + sox_argument_string, shell=True)

# Delete individual wavs
for wav_file in wav_files:
    os.remove(wav_file)
