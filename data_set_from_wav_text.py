import os
import sys
import mmap
import speech_recognition as sr
import datetime


data_contents = os.listdir("./data")
sound_files = ["data/" + filename for filename in data_contents
               if (filename.endswith(".wav") and
                   filename.startswith(sys.argv[1]) and
                   len(filename) > 11 and
                   filename[-10:-4].isdigit())]
sound_files.sort()

data_set = open("data/{}_data_set.txt".format(sys.argv[1]), 'w')
num_sound_files = len(sound_files)
successes = 0

for i, sound_file in enumerate(sound_files):
    with open(sound_file[:-11] + "-book-formatted.txt") as book_text:
        # use the audio file as the audio source
        r = sr.Recognizer()
        with sr.AudioFile(sound_file) as source:
            audio = r.record(source)  # read the entire audio file
        guess = ""
        # recognize speech using Sphinx
        try:
            guess = r.recognize_sphinx(audio)
        except sr.UnknownValueError:
            print("Sphinx could not understand audio")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))

        s = mmap.mmap(book_text.fileno(), 0, access=mmap.ACCESS_READ)
        guess_index = s.find(guess)

        if guess_index != -1:
            data_set.write("{},{},{}\n".format(sound_file, guess, guess_index))
            successes += 1

        print "Analysed {} of {} files ({}% recognised so far)".format(i, num_sound_files, 100 * (successes/float(i+1)))

with open("data/" + sys.argv[1] + "-previous-recog-rate.txt", 'w') as recog_rate_file:
    recog_rate_file.write(datetime.datetime.now().isoformat() + "\n")
    recog_rate_file.write("Recognition rate: {}% ({} / {})".format(100 * (successes / float(num_sound_files)),
                                                                   successes, num_sound_files))

data_set.close()
