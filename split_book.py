"""
Code modified from:
https://github.com/ZoeB/wave-tools/blob/master/wavesplit.py
"""

# This script finds all .wav files ending with '-book.wav' in the data directory,
# and splits them into shorter (0.5 to 15 seconds) audio clips.
# Depending on the way the speaker reads, the 'duration' may need to be longer or shorter.

# TODO: For each book .wav file, if a certain (high) % of the first 200 audio clips are
# very short, start again with a longer 'duration' var. If they are too long, start again
# with a shorter 'duration' var.

import struct  # For converting the (two's complement?) binary data to integers
import wave  # For .wav input and output
import os
import sys

# Set sensible defaults
threshold = 1024  # This has to be a number between 1 and 32767
duration = 5513  # Measured in single samples (0.25 seconds at 22050Hz)

# data_contents = os.listdir("./data")
# inputFilenames = ["data/" + n
#                   for n in data_contents
#                   if (n.endswith("-book.wav"))]

# Cycle through files
for inputFilename in ["data/" + sys.argv[1] + "-book.wav"]:
    outputFilenamePrefix = inputFilename[:-9]
    outputFilenameNumber = 0

    segmentLog = open(outputFilenamePrefix + "-segment-log.txt", 'w')

    try:
        inputFile = wave.open(inputFilename, 'r')
    except IOError:
        print(inputFilename, "doesn't look like a valid .wav file.  Skipping.")
        continue

    framerate = inputFile.getframerate()
    numberOfChannels = inputFile.getnchannels()
    sampleWidth = inputFile.getsampwidth()

    currentlyWriting = False
    allChannelsBeneathThresholdDuration = 0
    currentFrame = 0
    startFrame = 0

    for iteration in xrange(0, inputFile.getnframes()):
        allChannelsAsBinary = inputFile.readframes(1)
        allChannelsCurrentlyBeneathThreshold = True
        currentFrame += 1

        for channelNumber in xrange(numberOfChannels):
            channelNumber += 1
            channelStart = (channelNumber - 1) * sampleWidth
            channelEnd = channelNumber * sampleWidth
            channelAsInteger = struct.unpack('<h', allChannelsAsBinary[channelStart:channelEnd])
            channelAsInteger = channelAsInteger[0]

            if channelAsInteger < 0:
                channelAsInteger = 0 - channelAsInteger  # Make readout unipolar

            if channelAsInteger >= threshold:
                allChannelsCurrentlyBeneathThreshold = False

        if currentlyWriting:
            # We are currently writing
            outputFile.writeframes(allChannelsAsBinary)

            if allChannelsCurrentlyBeneathThreshold:
                allChannelsBeneathThresholdDuration += 1

                if allChannelsBeneathThresholdDuration >= duration:
                    currentlyWriting = False
                    segmentLog.write("{},{},{},{}\n".format(inputFilename,
                                                            outputFilenameNumber,
                                                            startFrame,
                                                            currentFrame + 1))
                    outputFile.close()
            else:
                    allChannelsBeneathThresholdDuration = 0
        else:
            # We're not currently writing
            if not allChannelsCurrentlyBeneathThreshold:
                # We have sound
                currentlyWriting = True
                startFrame = currentFrame
                allChannelsBeneathThresholdDuration = 0
                outputFilenameNumber += 1
                outputFilename = str(outputFilenameNumber)
                outputFilename = outputFilename.zfill(5)  # Pad to 5 digits
                outputFilename = outputFilenamePrefix + '-' + outputFilename + '.wav'
                print 'Writing to ' + outputFilename
                outputFile = wave.open(outputFilename, 'w')
                outputFile.setnchannels(inputFile.getnchannels())
                outputFile.setsampwidth(inputFile.getsampwidth())
                outputFile.setframerate(inputFile.getframerate())

    if currentlyWriting:
        segmentLog.write("{},{},{},{}".format(inputFilename, outputFilenameNumber, startFrame, currentFrame + 1))
        segmentLog.close()
        outputFile.close()
        inputFile.close()

    os.remove(inputFilename)
