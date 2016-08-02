# Book text has capitals, punctuation, etc
# make script to change book text to get rid of all punctuation which
# isn't surrounded on both sides by characters (to leave stuff like "she's" and "all-night")
# get rid of all newline characters and all capitals

# Warning: loads entire book file into memory

import sys
import string


with open("data/" + sys.argv[1] + "-book.txt", 'r') as book_text:
    filedata = book_text.read()

exclude = set(string.punctuation)

word_list = filedata.split()
new_word_list = []
for word in word_list:
    while len(word) and word[0] in exclude:
        word = word[1:]
    while len(word) and word[-1] in exclude:
        word = word[:-1]
    if len(word):
        new_word_list.append(word.lower())

filedata = ' '.join(new_word_list)

# Write the file out again
with open("data/" + sys.argv[1] + "-book-formatted.txt", 'w') as new_book_text:
    new_book_text.write(filedata)
