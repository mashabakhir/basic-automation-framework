# Problem Set 4B

import string

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
    word = word.strip(" !@#$%^&*()-_+={}[]|\:;'<>?,./\"")
    return word in word_list

def get_story_string():

    f = open("story.txt", "r")
    story = str(f.read())
    f.close()
    return story

### END HELPER CODE ###

WORDLIST_FILENAME = 'words.txt'

class Message(object):
    def __init__(self, text):
        self.message_text=text
        self.valid_words=load_words(WORDLIST_FILENAME)

    def get_message_text(self):

        return self.message_text

    def get_valid_words(self):

       return self.valid_words.copy()

    def build_shift_dict(self, shift):

        shift_dict = {}
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase

        for i in range(26):
            shift_dict[lowercase[i]] = lowercase[(i + shift) % 26]
            shift_dict[uppercase[i]] = uppercase[(i + shift) % 26]

        return shift_dict

    def apply_shift(self, shift):

        shift_dict = self.build_shift_dict(shift)
        encrypted_text = ""

        for char in self.message_text:
            if char in shift_dict:
                encrypted_text += shift_dict[char]
            else:
                encrypted_text += char  # punctuation, spaces, etc.

        return encrypted_text

class PlaintextMessage(Message):
    def __init__(self, text, shift):
        Message.__init__(self, text)
        self.shift = shift
        self.encryption_dict = self.build_shift_dict(shift)
        self.message_text_encrypted = self.apply_shift(shift)

    def get_shift(self):
        return self.shift

    def get_encryption_dict(self):

       return self.encryption_dict.copy()

    def get_message_text_encrypted(self):

        return self.message_text_encrypted

    def change_shift(self, shift):

        self.shift = shift
        self.encryption_dict = self.build_shift_dict(shift)
        self.message_text_encrypted = self.apply_shift(shift)


class CiphertextMessage(Message):
    def __init__(self, text):
        Message.__init__(self, text)

    def decrypt_message(self):

        best_shift = 0
        max_valid_words = 0
        best_decrypted_text = ""

        for s in range(26):
            decrypted_text = self.apply_shift(26 - s)
            words = decrypted_text.split()
            valid_count = sum([is_word(self.valid_words, w) for w in words])

            if valid_count > max_valid_words:
                max_valid_words = valid_count
                best_shift = 26 - s
                best_decrypted_text = decrypted_text

        return (best_shift % 26, best_decrypted_text)

if __name__ == '__main__':

    #test case1
    plaintext1 = PlaintextMessage('Attack at dawn!', 4)
    print('Input: "Attack at dawn!", shift=4')
    print('Expected Output: Exxego ex hear!')
    print('Actual Output:', plaintext1.get_message_text_encrypted())
    print()

    #test case2
    ciphertext1 = CiphertextMessage('Exxego ex hear!')
    print('Expected Output: (22, "Attack at dawn!")')
    print('Actual Output:', ciphertext1.decrypt_message())
    print()

    #test case3
    plaintext2 = PlaintextMessage('Python is fun!', 10)
    print('Input: "Python is fun!", shift=10')
    print('Expected Output: Zidryx sc pex!')
    print('Actual Output:', plaintext2.get_message_text_encrypted())
    print()

    #test case4
    ciphertext2 = CiphertextMessage('Zidryx sc pex!')
    print('Expected Output: (16, "Python is fun!")')
    print('Actual Output:', ciphertext2.decrypt_message())
    print()

    #decode story.txt
    story = get_story_string()
    story_cipher = CiphertextMessage(story)
    best_shift, decrypted_story = story_cipher.decrypt_message()

    print("Best shift value for story:", best_shift)
    print("Decrypted story:")
    print(decrypted_story)
