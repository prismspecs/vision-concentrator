#!/usr/bin/env python3

import sys


def write_prompt_to_file(file_path, prompt):
    try:
        with open(file_path, 'r') as f:
            existing_content = f.read()

        with open(file_path, 'w') as f:
            f.write(prompt + '\n')
            f.write(existing_content)

        print(
            f"Successfully wrote '{prompt}' as the first line in {file_path}")
    except IOError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python write_prompt.py <file_path> <prompt>")
        sys.exit(1)

    file_path = sys.argv[1]
    prompt = sys.argv[2]

    write_prompt_to_file(file_path, prompt)
