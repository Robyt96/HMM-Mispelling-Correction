import random

def perturb(input_text):
    # generate the file 'perturbed_text.txt' simulating a person that write the
    # input text introducing some noise
    
    # set random seed
    random.seed(18)
    
    # define chars list -> states = ['a', 'b', ..., 'z']
    chars = [chr(code) for code in range(ord('a'), ord('z') + 1)]
    
    # dictionary that associate each char with the list of his adjacent chars 
    # in the keyboard
    adjacent_chars = {
        'a': ['q', 'w', 's', 'z'],
        'b': ['v', 'g', 'h', 'n'],
        'c': ['x', 'd', 'f', 'v'],
        'd': ['e', 'r', 'f', 'c', 'x', 's'],
        'e': ['r', 'd', 's', 'w'],
        'f': ['r', 't', 'g', 'v', 'c', 'd'],
        'g': ['t', 'y', 'h', 'b', 'v', 'f'],
        'h': ['y', 'u', 'j', 'n', 'b', 'g'],
        'i': ['o', 'k', 'j', 'u'],
        'j': ['u', 'i', 'k', 'm', 'n', 'h'],
        'k': ['i', 'o', 'l', 'm', 'j'],
        'l': ['o', 'p', 'k'],
        'm': ['j', 'k', 'n'],
        'n': ['h', 'j', 'm', 'b'],
        'o': ['p', 'l', 'k', 'i'],
        'p': ['l', 'o'],
        'q': ['w', 's', 'a'],
        'r': ['t', 'f', 'd', 'e'],
        's': ['w', 'e', 'd', 'x', 'z', 'a'],
        't': ['y', 'g', 'f', 'r'],
        'u': ['i', 'j', 'h', 'y'],
        'v': ['f', 'g', 'b', 'c'],
        'w': ['e', 's', 'a', 'q'],
        'x': ['s', 'd', 'c', 'z'],
        'y': ['u', 'h', 'g', 't'],
        'z': ['a', 's', 'x']
    }

    # initialize error probability distribution dictionary
    error_rate = 1
    prob_adj = 0.8

    error_probs = {}
    for char in chars:
        error_probs[char] = {}
        
        # probability of observation = state is always 1 - error_rate
        error_probs[char][char] = 1 - error_rate
        
        # whit prob prob_adj when there is a mistake it is adjacent chars
        adj = adjacent_chars[char]
        for char_obs in adj:
            error_probs[char][char_obs] = prob_adj * error_rate / len(adj)
        
        # in the other 20% of cases the observation is one of the rest of chars
        not_adj = [c for c in chars if c not in adj + [char]]
        for char_obs in not_adj:
            error_probs[char][char_obs] = (1 - prob_adj) * error_rate / len(not_adj)
    '''
    for char in chars:
        for c in chars:
            error_probs[char][c] = 1/26
    '''
    corrupted_text = open('perturbed_text.txt', 'w')
    
    with open(input_text, 'r') as it:
        lines = it.readlines()
        n = 0
        
        for line in lines:
            words = line.split()
            for word in words:
                for char in word:
                    if (n % 10 == 0):
                        new_char = random.choices(
                            list(error_probs[char].keys()),
                            error_probs[char].values()
                        )[0]
                    else:
                        new_char = char
                    corrupted_text.write(new_char)
                    n += 1
                corrupted_text.write(' ')
            corrupted_text.write('\n')



















