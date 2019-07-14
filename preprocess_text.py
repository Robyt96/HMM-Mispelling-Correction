import re
import random

def preprocess(input_text):
    # do preprocessing operations on input text. The processed text is saved in
    # the file 'preprocessed_text.txt'
    
    # open input file in read mode
    with open(input_text, 'r') as it:
        lines = it.readlines()
        random.seed(18)
        random.shuffle(lines)
    
    # open new file in write mode
    preprocessed_text = open('preprocessed_text.txt', 'w')
    
    # define counter for final words
    tot_words = 0
    
    # preprocess input text
    for line in lines:
        # convert all to lower case
        line = line.lower()
        
        # remove some symbols
        line = line.replace('.', '')
        line = line.replace(',', '')
        line = line.replace(';', '')
        line = line.replace('!', '')
        line = line.replace('?', '')
        line = line.replace("'", "' ")
        # à è ì ò ù?
        
        # split the line string in a list of words
        words = line.split()
        
        # remove words that aren't made by only letters
        words = [word for word in words if re.match('^[a-z]+$', word)]
        tot_words += len(words)
        
        # save the new line into the file
        new_line = ' '.join(words) + '\n'
        preprocessed_text.write(new_line)

    # close the file created
    preprocessed_text.close()
    
    # print
    print('Total words in preprocessed text: ' + str(tot_words))
    