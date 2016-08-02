(Work in Progress, not ready)

Code to create an 'iteratively self-improving' speech data set with transcriptions.
As a side effect, this can also train a pretty decent speech recognition engine (almost) from scratch!
(It is advised that you use audio/text sources from the public domain)

Inputs:
- A MP3 files containing speech (e.g. audiobook files, film audio track)
- A text file containing the whole transcript of the MP3 file(s) (e.g. book text, film subtitles/script)

Outputs:
- Short .wav files for parts of speech (from words to whole sentences)
- Spectrograms of each .wav file
- File containing text transcription for each .wav file

Requirements:
- (requirements)

Installation:
- (installation)

Use:
- (use)

Background

In order to be able to deal with real life speech, a speech recognition engine must be able to deal with a very large vocabulary, different types of voices and accents, as well as noise and realistic imperfections in speech.

The aim of this project is to have large, free speech corpora which can be created, used and shared without having to worry about licences. The secondary goal is to create a pretty sweet speech recognition engine.

The availability of public domain 'quasi-labelled' data sets (public domain audiobooks along with their text counterparts, public domain films and their subtitle files) was my starting point. From there, we need two things in order to turn individual bits of speech from these into good data sets: something to make a guess at the transcription of the speech, and something to verify whether the guess is correct or not.

To start off with, we can use a free, basic speech recognition model to make some guesses. We can then search the whole true text for the guess, and if it appears, we can tentatively say that the guess is correct. We can then use this low quality data to train our own speech recognition model. If done right, with the right model and amount of training, we can end up with something which can more accurately recognise the speech from the original source than the first speech recognition engine we used could. This allows up to extract more data (and more accurate data) from the original source, and begin to use the same process on more and more varied sources, creating a larger and larger data set which trains a more and more general and accurate model.

We start with public domain audiobooks, as these have several features which are desirable when training a newly born speech recognition model:
- People who read audiobooks tend to read clearly and enunciate words well
- For each audiobook, we're learning one person's voice and accent (with some exceptions)
- Audiobooks have no background noise or other sounds which need to be ignored

These conditions rarely apply to the real world. We want our speech corpus to include data to which the above conditions do not apply, as we want models trained on this data to be more robust and general.

The next stage is thus to create data sets to which the above conditions do not apply. The obvious solution is to use (public domain) films! As long as we have a script or subtitles, we can carry on training in the same way as before.

The data set I have create from this method, from both audiobooks and films, contains _ hours of speech, and as it all comes from public domain sources, I can share it with anyone I want for free. Nothing stops you from using this code on non-public domain sources, but I assume there would be legal implications to sharing them, or maybe even using them for commercial purposes. For research, maybe such use could be classified as 'fair use', as it is for research and transformative and definitely used for a different purpose than the original source material, but this kind of thing is not my expertise, so I'm sticking to public domain works.

Process

The code converts the MP3 files provided into 16000Hz* single channel .wav files, then splits these files into smaller .wav files which are at most 9 seconds* long, by splitting the larger .wav files on silences in the audio. We keep a log in a text file of each .wav file's details, including the original source, at which point it starts (in the original source) and when it ends. The code also creates spectrograms of each of the resulting small sound files.

* The desired sample rate and minimum sound file length can be changed as options when invoking the code.

The accompanying text file has all text changed to lower case, all whitespace turned to a single space, and all of its symbols and punctuation removed, EXCEPT for punctuation surrounded by non-'punctuation-or-whitespace'. So for example, if the original text file contained the following line:

If only we'd known, then we could've avoided all ill-advised actions - aside from dying! "Darn," he said.

The resulting text would be present in the new text file:

if only we'd known then we could've avoided all ill-advised actions aside from dying darn he said

This allows contractions to stay, but it also allows compound words (which I don't think are desirable). I may update this to just allow apostrophes in the middle of words, to allow contractions but get rid of compound words and the like.

Next, unless a speech recognition model is specified, the code will use ___ to attempt to recognise the speech in each small .wav file. If the guessed text appears anywhere in the book text, it is assumed to be correct (this will not always be true, especially for shorter pieces of text). For each 'correct' guess, we add a new line to a text file containing the name of the original source material, the guessed text, and an index representing where the guessed text appears in the book. If a guess' index does not fall between the two surrounding it, we check if the text can be found between the indices of the two surrounding it**. If it does, we keep it, if it doesn't, we throw it away, as it is probably an incorrect guess.

** First, we check if the two guesses of either side are in the correct order, index-wise, and if the indices are a reasonable number apart. If they are not, we throw away all three guesses.

Now we have created a starting data set. If we want to train a phoneme based model, we run ___.py which attempts to convert all the words in our data set to phonemes using the phoneme dictionary from ____. With the __ option, it will ask us what the phonemes are for words it does not recognise, otherwise it'll simply remove samples containing words it cannot translate. After that, or if we want to train on characters instead of phonemes, we can go on to train our model on our data set and then see if the trained model is able to get more 'correct' guesses from the audiobook than ____. If it doesn't, we may need to train more, use a different model, or gather more of this 'basic' data from other audiobooks using ____. If it does get more correct guesses than before, we're set, and we can carry on iteratively training on more data from the same book, before moving on to other books, and eventually films and other data sources.

Happy Speech Corpusing!
