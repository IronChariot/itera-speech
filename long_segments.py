import wave
import os
import sys
import uuid
import struct
from shutil import copyfile

FRAMERATE = 16000


def split_segment(segment_filename, min_length, max_length, lower_threshold, first=False):
    segment_file = wave.open(segment_filename, 'r')
    segment_length = segment_file.getnframes()
    segment_length_seconds = segment_length / float(FRAMERATE)

    if min_length < segment_length_seconds <= max_length:
        # If the segment is now the right length, just return it:
        # print "Finished recursing, found segment which is {}s long".format(segment_length_seconds)
        return [segment_filename]
    elif segment_length_seconds <= min_length:
        # If the segment is now too short, give up on it:
        # print "Finished recursing, deleting segment which is {}s long".format(segment_length_seconds)
        os.remove(segment_filename)
        return []

    # If the segment is currently too long, find quiet parts and split on the longest quiet:
    quiet_dict = find_quiets(segment_file, lower_threshold)
    if len(quiet_dict) == 0:
        # Segment too long but has no quiets somehow, so give up on it
        # print "Finished recursing, deleting segment which is",
        # print "{}s long but has no quiets".format(segment_length_seconds)
        os.remove(segment_filename)
        return []

    # Getting longest quiet which is closest to the middle (say in middle 6 seconds?)
    longest_quiet_index = -1
    longest_quiet = -1
    for quiet in quiet_dict:
        time_of_this_quiet = quiet_dict[quiet][0] + (quiet_dict[quiet][1] / 2)
        earliest = (segment_length / 2) - (FRAMERATE * 3)
        latest = (segment_length / 2) + (FRAMERATE * 3)
        if time_of_this_quiet < earliest:
            continue
        elif time_of_this_quiet > latest:
            break
        longest_quiet_index = quiet if quiet_dict[quiet][1] > longest_quiet else longest_quiet_index
        longest_quiet = quiet_dict[longest_quiet_index][1]

    if longest_quiet == -1:
        # No suitable quiet bit found, just give up
        # print "Finished recursing, deleting segment which is",
        # print "{}s long but has no quiets in middle 4 seconds".format(segment_length_seconds)
        return []
    time_of_quiet = quiet_dict[longest_quiet_index][0] + (quiet_dict[longest_quiet_index][1] / 2)
    length_of_half2 = segment_length - time_of_quiet

    segment_file.rewind()

    # Split segment on longest quiet bit:
    segments = []
    for newSegLength in [time_of_quiet, length_of_half2]:
        filename = "data/" + str(uuid.uuid4()) + ".wav"
        segments.append(filename)
        half = wave.open(filename, 'w')
        half.setnchannels(segment_file.getnchannels())
        half.setsampwidth(segment_file.getsampwidth())
        half.setframerate(segment_file.getframerate())
        half.writeframes(segment_file.readframes(newSegLength))
        half.close()
    if not first:
        os.remove(segment_filename)
    print "Recursing, segment lengths {}s and {}s".format(time_of_quiet / float(FRAMERATE),
                                                          length_of_half2 / float(FRAMERATE))
    return split_segment(segments[0], min_length, max_length, lower_threshold) + \
        split_segment(segments[1], min_length, max_length, lower_threshold)


def find_quiets(wave_object, lower_threshold):
    number_of_channels = wave_object.getnchannels()
    sample_width = wave_object.getsampwidth()
    quiet_dict = {}
    quiet_index = 0
    all_channels_beneath_threshold_duration = 0
    for iteration in xrange(0, wave_object.getnframes()):
        all_channels_as_binary = wave_object.readframes(1)
        all_channels_currently_beneath_threshold = True

        for channel_number in xrange(number_of_channels):
            channel_number += 1
            channel_start = (channel_number - 1) * sample_width
            channel_end = channel_number * sample_width
            channel_as_integer = struct.unpack('<h', all_channels_as_binary[channel_start:channel_end])
            channel_as_integer = channel_as_integer[0]

            if channel_as_integer < 0:
                channel_as_integer = 0 - channel_as_integer  # Make readout unipolar

            if channel_as_integer > lower_threshold:
                all_channels_currently_beneath_threshold = False

        if not all_channels_currently_beneath_threshold:
            if all_channels_beneath_threshold_duration != 0:
                # We just had a quiet period, record it
                quiet_dict[quiet_index] = (iteration - all_channels_beneath_threshold_duration,
                                           all_channels_beneath_threshold_duration)
                quiet_index += 1
                all_channels_beneath_threshold_duration = 0
        else:
            all_channels_beneath_threshold_duration += 1

    return quiet_dict

if __name__ == "__main__":

    minLength = 0.75
    maxLength = 9.0
    threshold = 1024

    dataContents = os.listdir("./data")
    parts = ["data/" + n[:-(len("-segment-log.txt"))] for n in dataContents
             if (n.endswith("-segment-log.txt") and
                 n.startswith(sys.argv[1]))]
    old_files = []

    for part in parts:
        newSegNum = 1
        segmentLog = open(part + "-segment-log.txt", 'r')
        newSegmentLog = open(part + "-segment-log-new.txt", 'w')

        for line in segmentLog:
            source, segmentNo, segStart, segEnd = line.split(",")
            segmentNo = int(segmentNo)
            segStart = int(segStart)
            segEnd = int(segEnd)
            segLen = (segEnd - segStart) / float(FRAMERATE)  # Segment length in seconds
            longSegFilename = source[:-9] + "-{:05}.wav".format(segmentNo)
            old_files.append(longSegFilename)
            if segLen > maxLength:
                # print "{} is {}s long, splitting...".format(longSegFilename, segLen)
                splitSegments = split_segment(longSegFilename, minLength, maxLength, threshold, True)
                # Write new lines in segment log with new numbers, rename wav files, increase newSegNum
                splitStart = segStart
                # Fake the times...
                splitLen = segLen // len(splitSegments)
                for n in xrange(len(splitSegments)):
                    newSegmentLog.write("{},{},{},{}\n".format(source,
                                                               newSegNum,
                                                               splitStart,
                                                               splitStart + splitLen))
                    try:
                        os.rename(splitSegments[n], source[:-9] + "-{:06}.wav".format(newSegNum))
                    except OSError:
                        print "Failed to rename {}".format(splitSegments[n][0])
                        raise
                    newSegNum += 1
                    splitStart += splitLen
            elif segLen <= minLength:
                pass  # Deleting files at the end now
            else:
                # Segment is fine, just need to update segment number
                # Write new line in segment log with new number, rename wav file, increase newSegNum
                newSegmentLog.write("{},{},{},{}\n".format(source,
                                                           newSegNum,
                                                           segStart,
                                                           segEnd))
                copyfile(longSegFilename, source[:-9] + "-{:06}.wav".format(newSegNum))
                newSegNum += 1
        segmentLog.close()
        newSegmentLog.close()

    # Only delete old files once we're sure that we've processed everything correctly
    for old_file in old_files:
        os.remove(old_file)
