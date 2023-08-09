# TO DO:
#   loop by connecting last vid to first?
#   prompt "queue" for prompts already in incoming.dat
#   upscale

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
from PIL import Image, PngImagePlugin, ImageDraw
import datetime
import os
import numpy as np
import imageio
import random


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
current_seed = 1
num_interpolation_frames = 10
num_travel_frames = 50
ignore_next_modified = False
num_steps = 20
FINAL_WIDTH = 1280
FINAL_HEIGHT = 720
SCALED_WIDTH = FINAL_WIDTH/2
SCALED_HEIGHT = FINAL_HEIGHT/2
FPS = 15


# get current date and time and return string
def get_current_datetime_string():
    now = datetime.datetime.now()
    date_time_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    return date_time_string


def data_url_to_image(data_url):
    image_data = Image.open(io.BytesIO(
        base64.b64decode(data_url.split(",", 1)[0])))
    return image_data


def create_random_image():
    image_size = (FINAL_WIDTH, FINAL_HEIGHT)

    # create a new image with a white background then noise
    image = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(image)
    for y in range(image_size[1]):
        for x in range(image_size[0]):
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            draw.point((x, y), (r, g, b))

    image.save(os.path.join("output", "seed_t_lastframe.png"))

    return None


# when a new line is added to incoming.dat ...
class NewLineHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command

    def on_modified(self, event):

        global ignore_next_modified

        print(Color.GREEN + " -> on_modified called")
        print(Color.MAGENTA, "last line count:", self.last_line_count)

        

        if event.src_path.endswith('incoming.dat') and event.is_directory == False:

            if ignore_next_modified:
                ignore_next_modified = False
                return

            print(Color.RED + " -> incoming.dat was modified")

            # read first line of rendered.dat to previous_prompt
            with open('rendered.dat', 'r') as rendered:
                previous_prompt = rendered.readline().strip()
                print(Color.YELLOW + "previous prompt:",
                      previous_prompt, Color.BLUE)

            with open(event.src_path, 'r') as file:
                print("opening incoming.dat")
                # read all lines to a list
                lines = file.readlines()
                
                # if there is at least one line
                if len(lines) > 0:

                    # get only one new line
                    # new_line = lines[self.last_line_count:]
                    new_line = lines[0]
                    
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
                        incoming.writelines(lines[1:])
                        # since this will trigger on_modified again...
                        ignore_next_modified = True

                    # update last_line_count
                    self.last_line_count = len(lines) - 1
                    # run command on new lines
                    self.run_command_on_new_line(new_line, previous_prompt)

    def on_created(self, event):
        print(Color.GREEN + " -> on_created called")
        self.on_modified(event)

    def run_command_on_new_line(self, new_line, previous_prompt):
        print(Color.GREEN + " -> run_command_on_new_line called")
        global current_seed

        # for line in new_line:

        current_prompt = new_line.strip()

        filename = get_current_datetime_string() + "||" + current_prompt + ".mp4"

        dest_seed = 100 if current_seed == 1 else 1

        print(Color.YELLOW + "preparing new line:", current_prompt,
              Color.CYAN, "\nfilename:", filename, Color.MAGENTA + "\ncurrent seed:", current_seed, "destination seed:", dest_seed, Color.RESET)

        # payload for seed travel
        payload = {
            "prompt": current_prompt,
            "seed": current_seed,
            "width": SCALED_WIDTH,
            "height": SCALED_HEIGHT,
            "steps": num_steps,
            "sampler_index": "DPM++ 2M",
            "script_name": "Seed travel",
            "script_args": [
                "False",    # rnd_seed
                "4.0",      # seed count
                str(dest_seed),  # dest seed
                str(num_travel_frames),        # steps
                "Linear",   # curve
                "3",        # curve strength
                "False",    # loopback
                str(FPS),       # video fps
                "False",    # show images
                "False",    # compare paths
                "False",    # allow def sampler
                "0",        # bump_seed
                "0",        # lead in out
                "Lanczos",  # upscale method
                "2.0",      # upscale ratio -- was 2.0
                "True",     # use cache
                "0",        # ssim diff
                "0",        # ssim ccrop
                "0.001",    # substep min
                "75",       # ssim_diff_min
                "1",        # rife passes
                "False",    # rife drop
                "True",     # save stats
                "output/",     # save path -- not used
                filename,  # save filename -- not used
            ]
        }

        response = requests.post(
            url=f'{url}/sdapi/v1/txt2img', json=payload)
        r = response.json()

        # store r['images'] in a list seed_images
        seed_images = []
        for i in r['images']:
            seed_images.append(i)

        # save seed_images[-1] as seed_t_lastframe_next.png
        image = Image.open(io.BytesIO(
            base64.b64decode(seed_images[-1].split(",", 1)[0])))
        image = image.resize((FINAL_WIDTH, FINAL_HEIGHT))
        image.save(os.path.join("output", "seed_t_lastframe_next.png"))

        # got seed travel frames, let's make a video and save first/last frames

        # index = 0
        # writer = imageio.get_writer(os.path.join("output", "travel.mp4"), fps=FPS, quality=10)
        # for i in r['images']:
        #     image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
        #     image = image.resize((FINAL_WIDTH, FINAL_HEIGHT))
        #     image_np = np.array(image)  # Convert the image to a NumPy array
        #     if index == 0:
        #         image.save(os.path.join("output", "seed_t_firstframe.png"))
        #     if index == len(r['images']) - 1:
        #         image.save(os.path.join("output", "seed_t_lastframe_next.png"))
        #     writer.append_data(image_np)
        #     index += 1
        # writer.close()

        # now do interpolation if there is a previous prompt
        if previous_prompt != "":

            print("interpolating between",
                  previous_prompt, "and", current_prompt)

            interpolation_prompt = f"{previous_prompt}:1~0 AND {current_prompt}:0~1"

            # if seed_t_lastframe.png exists, use it as the previous image
            # otherwise, generate an image of noise
            if not os.path.exists(os.path.join("output", "seed_t_lastframe.png")):
                # generate an image of noise and save to seed_t_lastframe.png
                create_random_image()

            previous_image = os.path.join("output", "seed_t_lastframe.png")
            p_image_encoded = base64.b64encode(
                open(previous_image, 'rb').read()).decode('ascii')

            current_image = seed_images[0]  # the first seed image created

            payload = {
                "init_images": [
                    "data:image/png;base64," + p_image_encoded
                ],
                "prompt": interpolation_prompt,
                "seed": current_seed,
                "steps": num_steps,
                "width": FINAL_WIDTH,
                "height": FINAL_HEIGHT,
                "script_name": "Interpolate",
                "script_args": [
                    "data:image/png;base64," + current_image,    # init_img2
                    f'0-1[{num_interpolation_frames}]',         # i_values
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

            response = requests.post(
                url=f'{url}/sdapi/v1/img2img', json=payload)
            r = response.json()

            # store r['images'] in a list interpolate_images
            interpolate_images = []
            for i in r['images']:
                interpolate_images.append(i)

            # convert interpolate_images and seed_images to a video output.mp4
            interpolate_frames = [np.array(data_url_to_image(
                url).resize((FINAL_WIDTH, FINAL_HEIGHT))) for url in interpolate_images]
            seed_frames = [np.array(data_url_to_image(url).resize(
                (FINAL_WIDTH, FINAL_HEIGHT))) for url in seed_images]
            
 

            # save frames as a video using imageio
            # if the video already exists, append to it
            vid_path = os.path.join("output", "all_visions.mp4")
            if os.path.exists(vid_path):

                full_video = []
                full_video = imageio.get_reader(vid_path)

                with imageio.get_writer(vid_path, fps=FPS) as writer:
                    for frame in full_video:
                        writer.append_data(frame)
                    for frame in interpolate_frames:
                        writer.append_data(frame)
                    for frame in seed_frames:
                        writer.append_data(frame)
                    writer.close()

            # otherwise, create a new video
            else:

                with imageio.get_writer(vid_path, fps=FPS) as writer:
                    for frame in interpolate_frames + seed_frames:
                        writer.append_data(frame)
                    writer.close()


            print("Video saved:", vid_path)

            # rename seed_t_lastframe_next.png to seed_t_lastframe.png
            os.rename(os.path.join("output", "seed_t_lastframe_next.png"),
                      os.path.join("output", "seed_t_lastframe.png"))

            # set seed
            current_seed = dest_seed
            # write current_seed to seed.txt
            with open(os.path.join("output", "seed.txt"), 'w') as seed_file:
                seed_file.write(str(current_seed))

          

        subprocess.run(self.command, shell=True)


if __name__ == "__main__":

    print(Color.GREEN + " -> _main_ called")
    input_file = "incoming.dat"

    command_to_run = "echo 'done rendering'"
    event_handler = NewLineHandler(command_to_run)

    # load relevant configs
    # load seed from seed.txt
    if os.path.exists(os.path.join("output", "seed.txt")):
        with open(os.path.join("output", "seed.txt"), 'r') as seed_file:
            current_seed = int(seed_file.read())
    else:
        with open(os.path.join("output", "seed.txt"), 'w') as seed_file:
            seed_file.write(str(current_seed))

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
