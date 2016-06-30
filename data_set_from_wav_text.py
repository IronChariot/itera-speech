import os
import mmap
import speech_recognition as sr


data_contents = os.listdir("./data")
sound_files = ["data/" + filename for filename in data_contents
               if filename.endswith(".wav") and
                  len(filename) > 11 and
                  filename[-10:-4].isdigit()]

data_set = open("data/data_set.txt", 'w')

for sound_file in sound_files:
    with open(sound_file[:-11] + "-formatted.txt") as book_text:
        # use the audio file as the audio source
        r = sr.Recognizer()
        with sr.AudioFile(sound_file) as source:
            audio = r.record(source) # read the entire audio file
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

data_set.close()
