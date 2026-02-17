from collections import Counter
from typing import List, Tuple, Dict

# -----------------------------
# Load dictionary
# -----------------------------

def load_words(path: str) -> List[str]:
    with open(path) as f:
        return [w.strip().lower() for w in f if len(w.strip()) == 5 and w.strip().isalpha()]


# -----------------------------
# Core filters
# -----------------------------

def apply_greens(words: List[str], greens: Dict[int, str]) -> List[str]:
    return [
        w for w in words
        if all(w[pos] == letter for pos, letter in greens.items())
    ]


def apply_yellows(words: List[str], yellows: List[Tuple[int, str]]) -> List[str]:
    # must contain the letter
    required = {letter for _, letter in yellows}
    words = [w for w in words if all(l in w for l in required)]

    # must NOT be at those positions
    return [
        w for w in words
        if all(w[pos] != letter for pos, letter in yellows)
    ]


def apply_grays(words: List[str], grays: set[str]) -> List[str]:
    return [
        w for w in words
        if not any(c in grays for c in w)
    ]

def apply_letter_counts(
    words: List[str],
    min_counts: Dict[str, int],
    max_counts: Dict[str, int],
) -> List[str]:
    result = []

    for w in words:
        counts = Counter(w)

        if any(counts[l] < c for l, c in min_counts.items()):
            continue

        if any(counts[l] > c for l, c in max_counts.items()):
            continue

        result.append(w)

    return result


# -----------------------------
# Feedback parser
# -----------------------------
# feedback symbols:
#   'g' = green                                                                                                                                                               #   'y' = yellow
#   'b' = black / gray

def parse_feedback(guess: str, feedback: str):
    greens = {}
    yellows = []
    letter_hits = Counter()
    letter_total = Counter(guess)

    for i, (c, f) in enumerate(zip(guess, feedback)):
        if f == "c":
            greens[i] = c
            letter_hits[c] += 1
        elif f == "a":
            yellows.append((i, c))
            letter_hits[c] += 1

    min_counts = dict(letter_hits)
    max_counts = {}

    for c in letter_total:
        if letter_hits[c] < letter_total[c]:
            max_counts[c] = letter_hits[c]

    grays = {c for c in letter_total if c not in min_counts}

    return greens, yellows, grays, min_counts, max_counts


# -----------------------------
# Full engine step
# -----------------------------

def apply_feedback(
    words: List[str],
    guess: str,
    feedback: str,
) -> List[str]:

    greens, yellows, grays, min_counts, max_counts = parse_feedback(guess, feedback)

    words = apply_greens(words, greens)
    words = apply_yellows(words, yellows)
    words = apply_grays(words, grays)
    words = apply_letter_counts(words, min_counts, max_counts)

    return words


def best_next_guess(words):
    counts = Counter("".join(words))
    def score(word):
        return sum(counts[c] for c in set(word))
    try:
        return max(words, key=score)
    except ValueError:
        return words[0]

# -----------------------------                                                                                                                                               # Example run
# -----------------------------

if __name__ == "__main__":
    words = load_words("words.txt") # Remember that this file must have every 5-letter lowercase word per line in the English dictionary. Type 'best' instead of the word you used if your version of wordle doesn't recognize the word.
    #   (i)ncorrect ⬜
    #   (c)orrect 🟩
    #   (a)lmost 🟨

    previous_next_guess = None
    first_guess = True
    while True:
        print("Type 'best' instead of the word if you want the second best previous guess.")
        word = input("Word: ")
        if word == 'best' and (not first_guess):
            words.remove(best_next_guess(words))
            print("-" * 10)
            print(f"Best guess: {best_next_guess(words)}")
            print(f"New length: {len(words)}")
            print("-" * 5)
            if first_guess:
                first_guess = False
            continue
        elif first_guess and word == 'best':
            print("-" * 10)
            print(f"Best guess: {best_next_guess(words)}")
            print(f"New length (unchanged): {len(words)}")
            print("-" * 5)
            continue
        if first_guess:
            first_guess = False
        words = apply_feedback(words, word, input("Feedback: "))
        print("-" * 10)
        print(f"Best guess: {best_next_guess(words)}")
        print(f"New length: {len(words)}")
        print("-" * 5)
