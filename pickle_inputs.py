import numpy as np
from python_speech_features import mfcc
import scipy.io.wavfile as wav

TRAIN_FRACTION = 0.8

def load_batched_data(specPath, targetPath):
    import os
    '''returns 3-element tuple: batched data (list), max # of time steps (int), and
       total number of samples (int)'''
    list1 = [np.load(os.path.join(specPath, fn)) for fn in os.listdir(specPath)]
    list2 = [np.load(os.path.join(targetPath, fn)) for fn in os.listdir(targetPath)]
    return list1, list2

if __name__ == "__main__":
    TRAIN_INPUT_PATH = './nn_data/features' #directory of MFCC nFeatures x nFrames 2-D array .npy files
    TRAIN_TARGET_PATH = './nn_data/outputs' #directory of nCharacters 1-D array .npy files
    TEST_INPUT_PATH = './nn_data/features_test' #directory of MFCC nFeatures x nFrames 2-D array .npy files
    TEST_TARGET_PATH = './nn_data/outputs_test' #directory of nCharacters 1-D array .npy files

    AUDIO_PATH = '/media/sam/seraph/data/data-aaiw' #directory of raw wav files
    TEXT_FILE = '/media/sam/seraph/data/data-aaiw/aaiw_data_set.txt' #list of sound files and text

    ALPHABET = ["a", "b", "c", "d", "e", "f", "g", "h", "i", 
                "j", "k", "l", "m", "n", "o", "p", "q", "r", 
                "s", "t", "u", "v", "w", "x", "y", "z", " ", "'"]

    with open(TEXT_FILE, 'r') as f:
        data_lines = f.readlines()
        data_num = len(data_lines)
        training_num = int(data_num * TRAIN_FRACTION)
    with open(TEXT_FILE, 'r') as f:
        for i, line in enumerate(f):
            parts = line.split(',')

            # Get just the filename part of the audio file
            audio_file = parts[0]
            last_slash = audio_file.rfind('/') + 1
            audio_file = audio_file[last_slash:-4]

            text = parts[1]

            rate, signal = wav.read(AUDIO_PATH + "/" + audio_file + ".wav")
            mfcc_feat = mfcc(signal, rate, numcep=26)
            mfcc_feat = mfcc_feat.transpose()
            characters = np.array([])
            for character in text:
                characters = np.append(characters, ALPHABET.index(character))

            if i < training_num:
                np.save(TRAIN_INPUT_PATH + "/" + audio_file, mfcc_feat)
                np.save(TRAIN_TARGET_PATH + "/" + audio_file, characters)
            else:
                np.save(TEST_INPUT_PATH + "/" + audio_file, mfcc_feat)
                np.save(TEST_TARGET_PATH + "/" + audio_file, characters)

    inputs, outputs = load_batched_data(TRAIN_INPUT_PATH, TRAIN_TARGET_PATH)

    # 8 input samples:
    print len(inputs)

    # 26 MFCC features (12 MFCC coefficients + energy, and derivatives)
    print inputs[0]
    print len(inputs[0])

    # 423 frames (happens to be the max number of frames in these samples, but number of frames vary, lowest is 188 for sample 7)
    print inputs[0][0]
    print len(inputs[0][0])

    # 8 output samples
    print len(outputs)

    # for sample 0, 86 characters (ints, 0 to 26)
    print outputs[0]
    print len(outputs[0])
