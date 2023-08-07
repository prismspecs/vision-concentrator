# watcher
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# requests etc
import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin
import datetime
import os
import numpy as np
import imageio



class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'


url = "http://127.0.0.1:7860"


path = "output/txt2img/dreams"
current_prompt = ""
previous_prompt = ""
current_image = ""
previous_image = ""
current_seed = 1
WIDTH = 512
HEIGHT = 512
FPS = 15

# get current date and time and return string


def get_current_datetime_string():
    now = datetime.datetime.now()
    date_time_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    return date_time_string

# when a new line is added to incoming.dat ...


class NewLineHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command

    def on_modified(self, event):

        global previous_prompt

        if event.src_path.endswith('incoming.dat') and event.is_directory == False:

            # read first line of rendered.dat to previous_prompt
            with open('rendered.dat', 'r') as rendered:
                previous_prompt = rendered.readline().strip()
                print(Color.YELLOW + "previous prompt:",
                      previous_prompt, Color.BLUE)

            with open(event.src_path, 'r') as file:
                print("opening incoming.dat")
                # read all lines to a list
                lines = file.readlines()
                # if there are more lines than last time we checked
                if len(lines) > self.last_line_count:
                    # get only one new line
                    new_line = lines[self.last_line_count:]
                    print("got this:", repr(new_line))

                    # if rendered.dat does not exist, create it
                    if not os.path.exists('rendered.dat'):
                        open('rendered.dat', 'w').close()
                    # add new_line to rendered.dat at top of file, plus a newline character
                    with open('rendered.dat', 'r+') as rendered:
                        content = rendered.read()
                        rendered.seek(0, 0)
                        rendered.write(''.join(new_line) + content)
                    # remove only the new lines from incoming.dat
                    with open('incoming.dat', 'w') as incoming:
                        incoming.writelines(lines[:-len(new_line)])

                    # update last_line_count
                    self.last_line_count = len(lines) - 1
                    # run command on new lines
                    self.run_command_on_new_line(new_line[0])

    def on_created(self, event):
        self.on_modified(event)

    def run_command_on_new_line(self, new_line):
        # for line in new_line:

        vision_text = new_line.strip()

        filename = get_current_datetime_string() + "||" + vision_text + ".mp4"

        print(Color.YELLOW + "preparing new line:", vision_text,
              Color.CYAN, "\nfilename:", filename, Color.RESET)

        dest_seed = "2" if current_seed == 1 else "1"

        print("the current prev prompt is " + previous_prompt)

        # now do interpolation if there is a previous prompt
        if previous_prompt != "":

            current_image = os.path.join(path, "test2.png")
            previous_image = os.path.join(path, "test.png")

            print("interpolating between", previous_image, "and", current_image)

            # init_img2, i_values, loopback_alpha, border_alpha, loopback_loops, blend_strides, loopback_toggle, reuse_seed, one_grid, interpolate_varseed, paste_on_mask, inpaint_all, interpolate_latent

            interpolation_prompt = f"{previous_prompt}:1~0 AND {current_prompt}:0~1"

            p_image_encoded = base64.b64encode(
                open(previous_image, 'rb').read()).decode('ascii')
            c_image_encoded = base64.b64encode(
                open(current_image, 'rb').read()).decode('ascii')

            
            payload = {
                "init_images": [
                    "data:image/png;base64," + p_image_encoded
                ],
                "prompt": interpolation_prompt,
                "seed": current_seed,
                "steps": 25,
                "width": 512,
                "height": 512,
                "script_name": "Interpolate",
                "script_args": [
                    "data:image/png;base64," + c_image_encoded,    # init_img2
                    "0-1[30]",         # i_values
                    "0.0",             # loopback_alpha
                    "0.0",             # border_alpha
                    "0",               # loopback_loops
                    "0",               # blend_strides
                    "False",           # loopback_toggle
                    "False",           # reuse_seed
                    "False",           # one_grid
                    "False",           # interpolate_varseed
                    "False",           # paste_on_mask
                    "False",           # inpaint_all
                    "False",           # interpolate_latent
                ]
            }

            # i_values, Value: 0-1[3], Type: str
            # loopback_loops, Value: 1, Type: int
            # loopback_toggle, Value: False, Type: bool
            # reuse_seed, Value: True, Type: bool
            # paste_on_mask, Value: False, Type: bool
            # blend_strides, Value: 1, Type: int
            # border_alpha, Value: 0.1, Type: float
            # init_img2, Value: <PIL.Image.Image image mode=RGB size=512x512 at 0x7F98D2840460>, Type: Image
            # inpaint_all, Value: False, Type: bool
            # interpolate_latent, Value: False, Type: bool
            # interpolate_varseed, Value: False, Type: bool
            # loopback_alpha, Value: 0.2, Type: float
            # one_grid, Value: False, Type: bool
            # p, Value: <modules.processing.StableDiffusionProcessingImg2Img object at 0x7f993afeacb0>, Type: StableDiffusionProcessingImg2Img


            response = requests.post(
                url=f'{url}/sdapi/v1/img2img', json=payload)
            r = response.json()
            
            
            # create a video from the images in r
            writer = imageio.get_writer(os.path.join("output", "test.mp4"), fps=FPS, quality=10)
            for i in r['images']:
                image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
                image = image.resize((WIDTH, HEIGHT))
                image_np = np.array(image)  # Convert the image to a NumPy array
                writer.append_data(image_np)
            writer.close()

        # os.chown(os.path.join(path, filename), 1000, 1000)

        subprocess.run(self.command, shell=True)


if __name__ == "__main__":
    input_file = "incoming.dat"
    command_to_run = "echo 'done rendering'"
    event_handler = NewLineHandler(command_to_run)
    event_handler.last_line_count = 0
    # set last line count to number of lines in incoming.dat
    # with open(input_file, 'r') as file:
    #     event_handler.last_line_count = len(file.readlines()) - 1

    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    print(f"Watching {input_file} for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
