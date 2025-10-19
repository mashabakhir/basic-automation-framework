# Problem Set 4C

import string
from ps4a import get_permutations

### HELPER CODE ###
def load_words(file_name):

    print("Loading word list from file...")
    # inFile: file
    inFile = open(file_name, 'r')
    # wordlist: list of strings
    wordlist = []
    for line in inFile:
        wordlist.extend([word.lower() for word in line.split(' ')])
    print("  ", len(wordlist), "words loaded.")
    return wordlist

def is_word(word_list, word):

    word = word.lower()
    word = word.strip(r" !@#$%^&*()-_+={}[]|\:;'<>?,./\"")
    return word in word_list


### END HELPER CODE ###

WORDLIST_FILENAME = 'words.txt'

# you may find these constants helpful
VOWELS_LOWER = 'aeiou'
VOWELS_UPPER = 'AEIOU'
CONSONANTS_LOWER = 'bcdfghjklmnpqrstvwxyz'
CONSONANTS_UPPER = 'BCDFGHJKLMNPQRSTVWXYZ'

class SubMessage(object):
    def __init__(self, text):
        self.message_text = text
        self.valid_words = load_words(WORDLIST_FILENAME)
    
    def get_message_text(self):
        return self.message_text

    def get_valid_words(self):
        return self.valid_words.copy()
                
    def build_transpose_dict(self, vowels_permutation):

        transpose_dict={}

        # map lowercase vowels
        for i in range(len(VOWELS_LOWER)):
            transpose_dict[VOWELS_LOWER[i]] = vowels_permutation[i]
        # map uppercase vowels
        for i in range(len(VOWELS_UPPER)):
            transpose_dict[VOWELS_UPPER[i]] = vowels_permutation[i].upper()
        # consonants remain unchanged
        for c in CONSONANTS_LOWER:
            transpose_dict[c] = c
        for c in CONSONANTS_UPPER:
            transpose_dict[c] = c
        return transpose_dict
    
    def apply_transpose(self, transpose_dict):

        encrypted = ""
        for char in self.message_text:
            if char in transpose_dict:
                encrypted += transpose_dict[char]
            else:
                encrypted += char
        return encrypted
        
class EncryptedSubMessage(SubMessage):
    def __init__(self, text):
       SubMessage.__init__(self, text)

    def decrypt_message(self):

        permutations = get_permutations(VOWELS_LOWER)
        max_valid = 0
        best_message = self.message_text

        for perm in permutations:
            transpose_dict = self.build_transpose_dict(perm)
            decrypted = self.apply_transpose(transpose_dict)
            words = decrypted.split()
            valid_count = sum([is_word(self.valid_words, w) for w in words])

            if valid_count > max_valid:
                max_valid = valid_count
                best_message = decrypted

        return best_message

if __name__ == '__main__':

    # Example test case
    message = SubMessage("Hello World!")
    permutation = "eaiuo"
    enc_dict = message.build_transpose_dict(permutation)
    print("Original message:", message.get_message_text(), "Permutation:", permutation)
    print("Expected encryption:", "Hallu Wurld!")
    print("Actual encryption:", message.apply_transpose(enc_dict))
    enc_message = EncryptedSubMessage(message.apply_transpose(enc_dict))
    print("Decrypted message:", enc_message.decrypt_message())
     
    #test case1
    msg1 = SubMessage("I love programming!")
    perm1 = "ouiae"
    enc1 = msg1.apply_transpose(msg1.build_transpose_dict(perm1))
    print("\nOriginal:", msg1.get_message_text(), "Permutation:", perm1)
    print("Encrypted:", enc1)
    enc_obj1 = EncryptedSubMessage(enc1)
    print("Decrypted:", enc_obj1.decrypt_message())

    #test case2
    msg2 = SubMessage("Computers are fun!")
    perm2 = "eaiuo"
    enc2 = msg2.apply_transpose(msg2.build_transpose_dict(perm2))
    print("\nOriginal:", msg2.get_message_text(), "Permutation:", perm2)
    print("Encrypted:", enc2)
    enc_obj2 = EncryptedSubMessage(enc2)
    print("Decrypted:", enc_obj2.decrypt_message())
