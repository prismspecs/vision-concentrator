#!/usr/bin/env python3

import sys
import os

import subprocess

# translation
from langdetect import detect
from googletrans import Translator  

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


projects_dir = "output/projects"


def write_prompt_to_file(file_path, prompt, original_prompt):
    try:
        with open(file_path, 'a') as f:  # Open the file in append mode ('a')
            f.write(prompt + '\n')

        print("Successfully recorded your dream " +
              Color.YELLOW + original_prompt + Color.RESET)
        print("\n")

    except IOError as e:
        print(f"Error: {e}")
        sys.exit(1)



def translate_to_english(text):
    # Detect the language of the input text
    detected_language = detect(text)
    # print("Detected language:", detected_language)

    if detected_language == "en":
        # The text is already in English
        # print("The text is already in English.")
        return text
    else:
        try:
            # Translate the text to English
            translator = Translator()
            translated_text = translator.translate(text, dest='en').text
            # print("Translated text to English:")
            # print(translated_text)
            return translated_text
        except Exception as e:
            print("Error:", e)
            return text

    


if __name__ == "__main__":

    # check if projects directory exists
    if not os.path.exists(projects_dir):
        os.mkdir(projects_dir)

    # setup
    while True:
        print("Choose an option:")
        print("1) Create a new vision project")
        print("2) Add to an existing vision project")
        choice = input("Enter the number of your choice (1/2): ")

        if choice == "1":
            # Code to create a new vision project goes here
            print("You chose to create a new vision project.")

            while True:
                project_name = input("Enter a name for new vision project: ")

                # sanitize project_name
                project_name = project_name.replace(" ", "_")

                # check if project_name already exists in projects_dir
                if project_name in os.listdir(projects_dir):
                    print("That project name already exists. Please choose another.")
                    continue

                # create project directory
                project_dir = os.path.join(projects_dir, project_name)
                os.mkdir(project_dir)

                # write project_dir to current_config.dat
                with open("current_config.dat", "w") as f:
                    f.write(project_dir)

                print("Created new vision project: " + Color.YELLOW +
                        project_name + Color.RESET)

                break

            break
        elif choice == "2":
            # Code to add to an existing vision project goes here
            print("You chose to add to an existing vision project.")

            # select from existing projects
            existing_projects = os.listdir(projects_dir)
            if not existing_projects:
                print("No existing projects found.")
                continue
            else:
                print("Existing projects:")
                for index, project in enumerate(existing_projects, start=1):
                    print(f"{index}) {project}")

                while True:
                    try:
                        project_index = int(input("Select the project by entering its number: "))
                        if 1 <= project_index <= len(existing_projects):
                            selected_project = existing_projects[project_index - 1]
                            print("You selected the existing project:", selected_project)

                            # write project_dir to current_config.dat
                            project_dir = os.path.join(projects_dir, selected_project)
                            with open("current_config.dat", "w") as f:
                                f.write(project_dir)

                            break
                        else:
                            print("Invalid project number. Please select a valid project.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")


            break
        else:
            print("Invalid choice. Please enter 1 or 2.")
    

    file_path = os.path.join(project_dir, "incoming.dat")

    # open the other terminal windows
    command = 'gnome-terminal --title "Video Player" -- bash -c "python3 vision-player.py; exec bash"'
    subprocess.Popen(command, shell=True)

    command = 'gnome-terminal --title "Vision Concentrator" -- bash -c "python3 vision-concentrator.py; exec bash"'
    subprocess.Popen(command, shell=True)

    # clear incoming.dat
    with open(file_path, 'w') as f:
        f.write("")

    # change text size
    print("\033[8;50;100t")

    while True:
        original_prompt = input(Color.MAGENTA +
                       "Enter your vision here: " + Color.RESET)
        
        # translate to english
        prompt = translate_to_english(original_prompt)

        write_prompt_to_file(file_path, prompt, original_prompt)
