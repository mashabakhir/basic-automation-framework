import math
import random
import string
from random import choice

VOWELS = 'aeiou'
CONSONANTS = 'bcdfghjklmnpqrstvwxyz'
HAND_SIZE = 7

SCRABBLE_LETTER_VALUES = {
    'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4, 'i': 1, 'j': 8, 'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1, 'p': 3, 'q': 10, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8, 'y': 4, 'z': 10
}

# Helper code

WORDLIST_FILENAME = "words.txt"

def load_words():
    """
    Returns a list of valid words. Words are strings of lowercase letters.
    
    Depending on the size of the word list, this function may
    take a while to finish.
    """
    
    print("Loading word list from file...")
    # inFile: file
    inFile = open(WORDLIST_FILENAME, 'r')
    # wordlist: list of strings
    wordlist = []
    for line in inFile:
        wordlist.append(line.strip().lower())
    print("  ", len(wordlist), "words loaded.")
    return wordlist

def get_frequency_dict(sequence):
    """
    Returns a dictionary where the keys are elements of the sequence
    and the values are integer counts, for the number of times that
    an element is repeated in the sequence.

    sequence: string or list
    return: dictionary
    """
    
    # freqs: dictionary (element_type -> int)
    freq = {}
    for x in sequence:
        freq[x] = freq.get(x,0) + 1
    return freq
	

# (end of helper code)

# Problem #1: Scoring a word

def get_word_score(word, n):

    word=word.lower()

    if len(word)==0:
        return 0

    #1-st component (the sum of points for the letters in the word)
    letter_score=0

    for ch in word:

        letter_score += SCRABBLE_LETTER_VALUES[ch]

    #2-nd component (calculation by formula)

    wordlen=len(word)
    second_component=7*wordlen-3*(n-wordlen)
    if second_component<1:
        second_component=1

    #result
    return letter_score*second_component
    pass

# Make sure you understand how this function works and what it does!

def display_hand(hand):
    """
    Displays the letters currently in the hand.

    For example:
       display_hand({'a':1, 'x':2, 'l':3, 'e':1})
    Should print out something like:
       a x x l l l e
    The order of the letters is unimportant.

    hand: dictionary (string -> int)
    """
    
    for letter in hand.keys():
        for j in range(hand[letter]):
             print(letter, end=' ')      # print all on the same line
    print()                              # print an empty line

# Make sure you understand how this function works and what it does!
# You will need to modify this for Problem #4.

def deal_hand(n):
    hand = {}
    num_vowels = int(math.ceil(n / 3))

    wildcard_added = False
    for i in range(num_vowels):
        if not wildcard_added:
            x = '*'  #add wildcard
            wildcard_added = True
        else:
            x = random.choice(VOWELS)
        hand[x] = hand.get(x, 0) + 1

    for i in range(num_vowels, n):
        x = random.choice(CONSONANTS)
        hand[x] = hand.get(x, 0) + 1

    return hand

# Problem #2: Update a hand by removing letters

def update_hand(hand, word):

    new_hand=hand.copy()

    word=word.lower()

    for ch in word:
        if ch in new_hand and new_hand[ch]>0:
            new_hand[ch]-=1

    return new_hand

# Problem #3: Test word validity

def is_valid_word(word, hand, word_list):
    word = word.lower()

    if '*' not in word:
        if word not in word_list:
            return False
        word_freq = get_frequency_dict(word)
        for letter, count in word_freq.items():
            if hand.get(letter, 0) < count:
                return False
        return True

    else:
        for vowel in VOWELS:
            possible_word = word.replace('*', vowel)
            if possible_word in word_list:

                word_freq = get_frequency_dict(word)
                valid = True
                for letter, count in word_freq.items():
                    if hand.get(letter, 0) < count:
                        valid = False
                        break
                if valid:
                    return True
        return False
# Problem #5: Playing a hand

def calculate_handlen(hand):

 return sum(hand.values())

def play_hand(hand, word_list):

    total_score=0
    n=calculate_handlen(hand)

    while calculate_handlen(hand)>0:
        print("Current hand: ", end = " ")
        display_hand(hand)

        word=input('Enter word or "!!" to indicate that you are finished:')
        word=word.strip()

        if word=="!!":
            break

            if is_valid_word(word, hand, word_list):
                word_score = get_word_score(word, n)
                total_score += word_score
                print(f'"{word}" earned {word_score} points. Total: {total_score} points\n')
            else:
                 print("That is not a valid word. Please choose another word.\n")

            hand = update_hand(hand, word)

            print(f"Total score for this hand: {total_score} points")
            print("-" * 20)
            return total_score

    
    # BEGIN PSEUDOCODE <-- Remove this comment when you implement this function
    # Keep track of the total score
    
    # As long as there are still letters left in the hand:
    
        # Display the hand
        
        # Ask user for input
        
        # If the input is two exclamation points:
        
            # End the game (break out of the loop)

            
        # Otherwise (the input is not two exclamation points):

            # If the word is valid:

                # Tell the user how many points the word earned,
                # and the updated total score

            # Otherwise (the word is not valid):
                # Reject invalid word (print a message)
                
            # update the user's hand by removing the letters of their inputted word
            

    # Game is over (user entered '!!' or ran out of letters),
    # so tell user the total score

    # Return the total score as result of function



#
# Problem #6: Playing a game
# 


#
# procedure you will use to substitute a letter in a hand
#

def substitute_hand(hand, letter):
    if letter not in hand:
        return hand.copy()

    new_hand = hand.copy()
    count = new_hand[letter]
    del new_hand[letter]

    letters = VOWELS + CONSONANTS
    available_letters = [l for l in letters if l not in new_hand]
    if not available_letters:
        return new_hand

    new_letter = random.choice(available_letters)
    new_hand[new_letter] = count
    return new_hand
    
def play_game(word_list):

   total_score=0
   substituted=False
   replayed=False

   num_hands=int(input("Enter total number of hands: "))

   for _ in range(num_hands):
       hand = deal_hand(HAND_SIZE)
       print("Current hand: ", end="")
       display_hand(hand)

       if not substituted:
           choice = input("Would you like to substitute a letter? (yes/no) ").lower()
           if choice == "yes":
               letter = input("Which letter would you like to replace: ").lower()
               hand = substitute_hand(hand, letter)
               substituted = True

       hand_score = play_hand(hand, word_list)

   if not replayed:
       choice = input("Would you like to replay the hand? (yes/no) ").lower()
       if choice == "yes":
           replayed_score = play_hand(hand, word_list)
           hand_score = max(hand_score, replayed_score)
           replayed = True

   total_score += hand_score

   print(f"Total score over all hands: {total_score}")
   return total_score

# Build data structures used for entire session and play game
# Do not remove the "if __name__ == '__main__':" line - this code is executed
# when the program is run directly, instead of through an import statement

if __name__ == '__main__':
    word_list = load_words()
    play_game(word_list)



