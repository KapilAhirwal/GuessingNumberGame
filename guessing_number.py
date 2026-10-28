import json
import random
from pathlib import Path


QUESTIONS = [
    "I am thinking of an even number from {low} to {high}. Can you guess it?",
    "Which even number did I choose between {low} and {high}?",
    "Can you find my secret even number? It is between {low} and {high}.",
    "A hidden even number is waiting between {low} and {high}. What is it?",
    "Guess the even number I picked from {low} to {high}.",
    "Can you crack this number? It is even and between {low} and {high}.",
    "One even number between {low} and {high} is my secret. Can you find it?",
    "What even number am I hiding between {low} and {high}?",
]

LEADERBOARD_FILE = Path(__file__).with_name("leaderboard.json")


def load_leaderboard():
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as file:
            scores = json.load(file)
            return scores if isinstance(scores, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_winner(name, rounds, guesses):
    scores = load_leaderboard()

    scores.append({
        "name": name,
        "rounds": rounds,
        "guesses": guesses,
    })

    scores.sort(key=lambda score: (score["rounds"], score["guesses"]))

    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as file:
        json.dump(scores[:10], file, indent=2)


def show_leaderboard():
    print("\nLEADERBOARD — TOP 10")
    print("-" * 40)

    scores = load_leaderboard()

    if not scores:
        print("No winners yet. Be the first!")
        return

    for place, score in enumerate(scores, start=1):
        print(
            f"{place}. {score['name']} — "
            f"{score['rounds']} rounds, {score['guesses']} guesses"
        )


def show_puzzle(size, revealed_pieces):
    print(f"\nPUZZLE: {len(revealed_pieces)} of {size * size} pieces")

    for row in range(size):
        line = ""

        for column in range(size):
            if (row, column) in revealed_pieces:
                line += " 🧩 "
            else:
                line += " □ "

        print(line)


def make_random_range(used_ranges):
    while True:
        low = random.randint(15, 70)
        high = random.randint(low + 5, 75)
        number_range = (low, high)

        if number_range not in used_ranges:
            used_ranges.add(number_range)
            return low, high


def get_next_question(question_deck, previous_question):
    if not question_deck:
        question_deck = QUESTIONS.copy()
        random.shuffle(question_deck)

        if len(question_deck) > 1 and question_deck[-1] == previous_question:
            question_deck[0], question_deck[-1] = (
                question_deck[-1],
                question_deck[0],
            )

    question = question_deck.pop()
    return question, question_deck


def get_guess(previous_guesses, low, high):
    while True:
        entry = input("Your guess: ")

        try:
            guess = int(entry)
        except ValueError:
            print("Please enter a whole number.")
            continue

        if guess < low or guess > high:
            print(f"Enter a number from {low} to {high}.")
            continue

        if guess in previous_guesses:
            print("You already tried that number. Choose another one.")
            continue

        return guess


def add_puzzle_piece(size, revealed_pieces):
    for row in range(size):
        for column in range(size):
            if (row, column) not in revealed_pieces:
                revealed_pieces.add((row, column))
                return


def grow_puzzle(size, revealed_pieces):
    if size < 8:
        size = min(size * 2, 8)
        print(f"\nThree guesses used. The puzzle has grown to {size}x{size}!")
        show_puzzle(size, revealed_pieces)
    else:
        print("\nThree guesses used. The puzzle is already at its maximum size: 8x8.")

    return size


def play_round(
    round_number,
    used_ranges,
    question_deck,
    previous_question,
    puzzle_size,
    revealed_pieces,
):
    low, high = make_random_range(used_ranges)

    question, question_deck = get_next_question(
        question_deck,
        previous_question,
    )

    even_numbers = [
        number
        for number in range(low, high + 1)
        if number % 2 == 0
    ]
    answer = random.choice(even_numbers)
    wrong_guesses = []

    print(f"\nROUND {round_number}")
    print(question.format(low=low, high=high))
    print("You have 3 guesses.")

    for attempt in range(1, 4):
        guess = get_guess(wrong_guesses, low, high)

        if guess == answer:
            print("Correct! One puzzle piece has been filled.")
            add_puzzle_piece(puzzle_size, revealed_pieces)
            show_puzzle(puzzle_size, revealed_pieces)

            return (
                True,
                attempt,
                question,
                question_deck,
                puzzle_size,
            )

        wrong_guesses.append(guess)

        if attempt == 1:
            if guess < answer:
                print("Small hint: the secret number is higher.")
            else:
                print("Small hint: the secret number is lower.")

        elif attempt == 2:
            if answer % 4 == 0:
                print("Big hint: the number is divisible by 4.")
            else:
                print("Big hint: the number is not divisible by 4.")

        else:
            print(f"Three guesses used. The number was {answer}.")
            puzzle_size = grow_puzzle(puzzle_size, revealed_pieces)

    return (
        False,
        3,
        question,
        question_deck,
        puzzle_size,
    )


def main():
    print("=" * 40)
    print("         GUESSING NUMBER")
    print("=" * 40)
    print("Guess numbers and complete the puzzle!")

    player_name = input("Enter your name: ").strip()

    if player_name == "":
        player_name = "Player"

    show_leaderboard()

    puzzle_size = 2
    revealed_pieces = set()
    used_ranges = set()
    question_deck = []
    previous_question = None
    round_number = 0
    total_guesses = 0

    show_puzzle(puzzle_size, revealed_pieces)

    while len(revealed_pieces) < puzzle_size * puzzle_size:
        round_number += 1

        (
            won_round,
            guesses_used,
            previous_question,
            question_deck,
            puzzle_size,
        ) = play_round(
            round_number,
            used_ranges,
            question_deck,
            previous_question,
            puzzle_size,
            revealed_pieces,
        )

        total_guesses += guesses_used

    print(f"\nCongratulations, {player_name}! You completed the puzzle.")

    save_winner(player_name, round_number, total_guesses)
    show_leaderboard()

    print("\nThanks for playing!")


if __name__ == "__main__":
    main()