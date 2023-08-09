#!/usr/bin/env python3

import sys


class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'


# clear the terminal
print("\033c", end="")
# change text size
print("\033[8;50;100t")


def write_prompt_to_file(file_path, prompt):
    try:
        with open(file_path, 'a') as f:  # Open the file in append mode ('a')
            f.write(prompt + '\n')

        print("Successfully recorded your dream " +
              Color.YELLOW + prompt + Color.RESET)
        print("\n")

    except IOError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python write_prompt.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    while True:
        prompt = input(Color.MAGENTA +
                       "Enter your vision here: " + Color.RESET)

        write_prompt_to_file(file_path, prompt)
