import random
import string

def load_words(filename="words.txt"):
    with open(filename, "r") as f:
        words = f.read().split()
    return words

def choose_word(wordlist):
    return random.choice(wordlist)

def IsWordGuessed(secret_word, letters_guessed):
    return all(letter in letters_guessed for letter in secret_word)

def GetGuessedWord(secret_word, letters_guessed):
    return "".join(letter if letter in letters_guessed else "_ " for letter in secret_word)

def GetAvailableLetters(letters_guessed):
    return "".join(letter for letter in string.ascii_lowercase if letter not in letters_guessed)

def hangman(secret_word):
    print("Welcome to the game Hangman!")
    print(f"I am thinking of a word that is {len(secret_word)} letters long.")

    guesses_left = 10
    letters_guessed = []

    while guesses_left > 0 and not IsWordGuessed(secret_word, letters_guessed):
        print("-" * 15)
        print(f"You have {guesses_left} guesses left.")
        print("Available letters:", GetAvailableLetters(letters_guessed))

        guess = input("Please guess a letter: ").lower()

        if guess in letters_guessed:
            print("Oops! You've already guessed that letter:", GetGuessedWord(secret_word, letters_guessed))
        elif guess in secret_word:
            letters_guessed.append(guess)
            print("Good guess:", GetGuessedWord(secret_word, letters_guessed))
        else:
            letters_guessed.append(guess)
            guesses_left -= 1
            print("Oops! That letter is not in my word:", GetGuessedWord(secret_word, letters_guessed))

    print("-" * 15)
    if IsWordGuessed(secret_word, letters_guessed):
        print("Congratulations, you won! The word was:", secret_word)
    else:
        print("Sorry, you ran out of guesses. The word was:", secret_word)


if __name__ == "__main__":
    wordlist = load_words()
    secret_word = choose_word(wordlist)
    hangman(secret_word)
