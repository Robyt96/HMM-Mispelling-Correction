from pomegranate import *

from preprocess_text import preprocess
from perturb_text import perturb


#input_text = "La-vita-sul-pianeta-Marte.txt"
input_text = "books.txt"

# call function that preprocess the input text
preprocess(input_text)

# call function that introduce noise in the text
perturb('preprocessed_text.txt')

# define states list -> states = ['a', 'b', ..., 'z']
states = [chr(code) for code in range(ord('a'), ord('z') + 1)]

# initialize prior probability distribution dictionary and end probability 
# distribution dictionary. That is:
# -> start_probs = {'a': 0, 'b': 0, ..., 'z': 0}
# -> end_probs = {'a': 0, 'b': 0, ..., 'z': 0}
# start_probs[x] is the probability that a word start with char x
# end_probs[x] is the probability that a word end with char x
start_probs = {}
end_probs = {}
for state in states:
    start_probs[state] = 0
    end_probs[state] = 0

# initialize transition probability distribution dictionary and observation
# probability distribution dictionary. That is:
# -> trans = {'a': {'a': 0, 'b': 0, ..., 'z': 0},
#             'b': {'a': 0, 'b': 0, ..., 'z': 0},
#             ...,
#             'z': {'a': 0, 'b': 0, ..., 'z': 0}}
#
# -> obs = {'a': {'a': 0, 'b': 0, ..., 'z': 0},
#           'b': {'a': 0, 'b': 0, ..., 'z': 0},
#           ...,
#           'z': {'a': 0, 'b': 0, ..., 'z': 0}}
#
# trans[x][y] is the transition probability from x to y
# obs[x][y] is the probability of observe y when the right character was x
trans = {}
obs = {}
for x in states:
    trans[x] = {}
    obs[x] = {}
    for y in states:
        trans[x][y] = 0
        obs[x][y] = 0

# open the preprocessed text and generate trainset and testset
trainset_percentage = 0.8
with open('preprocessed_text.txt', 'r') as pt:
    lines = pt.readlines()
    # trainset is the first 80% of the text
    trainset_original = lines[:int(trainset_percentage * len(lines))]
    # testset is the last 20% of the text
    testset_original = lines[int(trainset_percentage * len(lines)):]

# open the perturbed text and generate trainset and testset
with open('perturbed_text.txt', 'r') as prt:
    lines = prt.readlines()
    # trainset is the first 80% of the text
    trainset_perturbed = lines[:int(trainset_percentage * len(lines))]
    # testset is the last 20% of the text
    testset_perturbed = lines[int(trainset_percentage * len(lines)):]

# reading the original trainset learn start, end and transition probabilities
for line in trainset_original:
    words = line.split()
    for word in words:
        first_letter = word[0]
        last_letter = word[-1]
        start_probs[first_letter] += 1
        end_probs[last_letter] += 1
        
        for i in range(1, len(word)):
            trans[word[i-1]][word[i]] += 1

# comparing original and perturbed trainsets learn observation probabilities
for i in range(len(trainset_original)): # loop on lines
    words_original = trainset_original[i].split()
    words_perturbed = trainset_perturbed[i].split()
    for j in range(len(words_original)): # loop on words
        word_original = words_original[j]
        word_perturbed = words_perturbed[j]
        for k in range(len(word_original)): # loop on chars
            obs[word_original[k]][word_perturbed[k]] += 1

# function defined to normalize between 0 and 1 all the values in a dictionary
def normalize_values(dict):
    tot = sum(dict.values())
    for key in dict:
        if (tot != 0):
            dict[key] /= tot

# normalize frequencies
normalize_values(start_probs)
normalize_values(end_probs)
for state in trans:
    normalize_values(trans[state])
for state in obs:
    normalize_values(obs[state])

# create the HMM model with pomegranate
# documentation at https://pomegranate.readthedocs.io/en/latest/HiddenMarkovModel.html
model = HiddenMarkovModel('misspelling_correction')

# create states with their observations probabilities
mstates = []
for state in obs:
    mstates += [State(DiscreteDistribution(obs[state]), name=state)]
model.add_states(mstates)

# add start probabilities to the model
for state in start_probs:
    model.add_transition(
        model.start,
        mstates[ord(state) - 97],
        start_probs[state]
    )

# add end probabilities to the model
for state in end_probs:
    model.add_transition(
        mstates[ord(state) - 97],
        model.end,
        end_probs[state]
    )

# add transition probabilities to the model
for start_state in trans:
    for end_state in trans[start_state]:
        model.add_transition(
            mstates[ord(start_state) - 97],
            mstates[ord(end_state) - 97],
            trans[start_state][end_state]
        )

# bake the model
model.bake()

# save the model in a file
with open('model.txt', 'w') as f:
    f.write(model.to_json())

# test the model created: use viterbi algorithm on each word of the perturbed
# testset and check if the result match the real word in the original testset
testset_corrected = []
for line in testset_perturbed:
    words = line.split()
    line_corrected = []
    for word in words:
        # call viterbi algorithm on the sequence of word's chars
        hmm_prediction = model.predict(list(word), algorithm='viterbi')
        # convert most probable states sequence to chars
        corrected_word = ''.join([chr(s + 97) for s in hmm_prediction[1:-1]])
        line_corrected += [corrected_word]
    testset_corrected += [' '.join(line_corrected)]

# write in files the perturbed and corrected testsets
with open('testset_corrected.txt', 'w') as f:
    for line in testset_corrected:
        f.write(line + '\n')

with open('testset_perturbed.txt', 'w') as f:
    for line in testset_perturbed:
        f.write(line)



# analyze results
FF = 0 # perturbed and corrected in a non italian word
FT = 0 # perturbed corrected right
TF = 0 # not perturbed and corrected wrong
TT = 0 # not perturbed and not corrected

FF_inDict = 0

'''
# load external dictionary
with open('dictionary.txt', 'r') as f:
    dictionary = f.readlines()

dictionary = [w.lower()[:-1] for w in dictionary]
'''
dictionary = []


for i in range(len(testset_original)):

    words_original = testset_original[i].split()
    words_perturbed = testset_perturbed[i].split()
    words_corrected = testset_corrected[i].split()
    
    
    for j in range(len(words_original)):
    
        word_original = words_original[j]
        word_perturbed = words_perturbed[j]
        word_corrected = words_corrected[j]
        
        if (word_original == word_corrected):
            if (word_perturbed != word_original):
                FT += 1
            else:
                TT += 1
        else:
            if (word_perturbed == word_original):
                TF += 1
                #print(word_original + ' ' + word_perturbed + ' ' + word_corrected)
            else:
                if (word_corrected in dictionary):
                    FF_inDict += 1
                    FF += 1
                    #print(word_original + ' ' + word_perturbed + ' ' + word_corrected)
                else:
                    FF += 1
                    #print(word_original + ' ' + word_perturbed + ' ' + word_corrected)

print('RESULTS OF TEST',
      '\nPerturbed words not corrected or not corrected in words different from the real ones: ' + str(FF),
      '\nPerturbed words corrected in the right way: ' + str(FT),
      '\nPercentage of perturbed words corrected: ' + str(FT*100/(FF+FT)) + '%',
      '\nNot perturbed words but corrected by viterbi: ' + str(TF),
      '\nNot perturbed words not altered by viterbi: ' + str(TT),
      '\nPercentage of not perturbed words not altered by correction: ' + str(TT*100/(TT+TF)) + '%'
      )






















