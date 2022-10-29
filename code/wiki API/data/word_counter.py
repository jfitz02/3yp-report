#count the number of words in all the file in director ./preprocessed
#and print the result

import os
import re

def count_words_in_file(file_name):
    file = open(file_name, 'r', encoding='utf-8')
    text = file.read()
    file.close()
    words = re.findall(r'\w+', text)
    return len(words)

def count_words_in_dir(dir_name):
    file_names = os.listdir(dir_name)
    total = 0
    for file_name in file_names:
        total += count_words_in_file(dir_name + '/' + file_name)
    return total

if __name__ == '__main__':
    print(count_words_in_dir('./preprocessed'))

