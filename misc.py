from string import ascii_letters
from random import choice


def generate_random_string(length=30):
    result = ""
    for _ in range(length):
        result += choice(ascii_letters)

    return result
