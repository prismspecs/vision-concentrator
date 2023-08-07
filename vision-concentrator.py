# TO DO:
#   send prompts on run
#   seed
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
current_seed = 1
num_interpolation_frames = 30
num_travel_frames = 30
FINAL_WIDTH = 1024
FINAL_HEIGHT = 1024
WIDTH = 512
HEIGHT = 512
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


# when a new line is added to incoming.dat ...
class NewLineHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command

    def on_modified(self, event):

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
                    self.run_command_on_new_line(new_line[0], previous_prompt)

    def on_created(self, event):
        self.on_modified(event)

    def run_command_on_new_line(self, new_line, previous_prompt):
        # for line in new_line:

        current_prompt = new_line.strip()

        filename = get_current_datetime_string() + "||" + current_prompt + ".mp4"

        print(Color.YELLOW + "preparing new line:", current_prompt,
              Color.CYAN, "\nfilename:", filename, Color.RESET)

        dest_seed = "2" if current_seed == 1 else "1"

        # payload for seed travel
        payload = {
            "prompt": current_prompt,
            "seed": current_seed,
            "width": 512,
            "height": 512,
            "steps": 20,
            "sampler_index": "DPM++ 2M",
            "script_name": "Seed travel",
            "script_args": [
                "False",    # rnd_seed
                "4.0",      # seed count
                dest_seed,  # dest seed
                f'0-1[{num_travel_frames}]',        # steps
                "Linear",   # curve
                "3",        # curve strength
                "False",    # loopback
                "15",       # video fps
                "False",    # show images
                "False",    # compare paths
                "False",    # allow def sampler
                "0",        # bump_seed
                "0",        # lead in out
                "Lanczos",  # upscale method
                "2.0",      # upscale ratio
                "True",     # use cache
                "0",        # ssim diff
                "0",        # ssim ccrop
                "0.001",    # substep min
                "75",       # ssim_diff_min
                "1",        # rife passes
                "False",    # rife drop
                "True",     # save stats
                "output/",     # save path -- not used
                filename,  # save filename
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

        print("the current prev prompt is " + previous_prompt)

        # now do interpolation if there is a previous prompt
        if previous_prompt != "":

            print("interpolating between",
                  previous_prompt, "and", current_prompt)

            interpolation_prompt = f"{previous_prompt}:1~0 AND {current_prompt}:0~1"

            # current_image = os.path.join("output", "seed_t_firstframe.png")
            # c_image_encoded = base64.b64encode(
            #     open(current_image, 'rb').read()).decode('ascii')

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
                "steps": 25,
                "width": 512,
                "height": 512,
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
            if os.path.exists(os.path.join("output", "all_visions.mp4")):
                output_path = os.path.join("output", "all_visions.mp4")

                full_video = imageio.get_reader(
                    os.path.join("output", "all_visions.mp4"))

                with imageio.get_writer(output_path, fps=FPS) as writer:
                    for frame in interpolate_frames + seed_frames:
                        writer.append_data(frame)
                    for frame in full_video:
                        writer.append_data(frame)
                    writer.close()

            # otherwise, create a new video
            else:
                output_path = os.path.join("output", "all_visions.mp4")

                with imageio.get_writer(output_path, fps=FPS) as writer:
                    for frame in interpolate_frames + seed_frames:
                        writer.append_data(frame)
                    writer.close()

            print("Video saved:", output_path)

            # rename seed_t_lastframe_next.png to seed_t_lastframe.png
            os.rename(os.path.join("output", "seed_t_lastframe_next.png"),
                      os.path.join("output", "seed_t_lastframe.png"))
            
            # set seed
            current_seed = dest_seed

            # create a video from the images in r
            # index = 0
            # writer = imageio.get_writer(os.path.join(
            #     "output", "interpolate.mp4"), fps=FPS, quality=10)
            # for i in r['images']:
            #     image = Image.open(io.BytesIO(
            #         base64.b64decode(i.split(",", 1)[0])))
            #     # image = image.resize((WIDTH, HEIGHT))
            #     # NEED TO DO UPSCALING !!!
            #     image = image.resize((FINAL_WIDTH, FINAL_HEIGHT))
            #     # Convert the image to a NumPy array
            #     image_np = np.array(image)
            #     if index == 0:
            #         image.save(os.path.join("output", "interp_firstframe.png"))
            #     if index == len(r['images']) - 1:
            #         image.save(os.path.join("output", "interp_lastframe.png"))
            #     writer.append_data(image_np)
            #     index += 1
            # writer.close()

            # # join interpolate.mp4 and travel.mp4
            # # REPLACE THIS WITH USING MEMORY RATHER THAN DISK IO
            # # Read the input videos
            # interpolate_video = imageio.get_reader(os.path.join("output", "interpolate.mp4"))
            # travel_video = imageio.get_reader(os.path.join("output", "travel.mp4"))

            # # Get the frames from each video
            # interpolate_frames = list(interpolate_video)
            # travel_frames = list(travel_video)

            # # Combine the frames from both videos
            # combined_frames = interpolate_frames + travel_frames

            # # Create the output video using the combined frames
            # output_video = imageio.get_writer(imageio.get_reader(os.path.join("output", "combined_new.mp4")), fps=FPS)

            # # Write each frame to the output video
            # for frame in combined_frames:
            #     output_video.append_data(frame)

            # # Close the output video
            # output_video.close()

            # # now add combined_new.mp4 to combined.mp4
            # # Read the input videos
            # # if combined.mp4 exists
            # if os.path.exists(imageio.get_reader(os.path.join("output", "combined.mp4"))):

            #     combined_video = imageio.get_reader(os.path.join("output", "combined.mp4"))
            #     combined_new_video = imageio.get_reader(os.path.join("output", "combined_new.mp4"))
            #     combined_frames = list(combined_video)
            #     combined_new_frames = list(combined_new_video)
            #     combined_frames = combined_frames + combined_new_frames
            #     output_video = imageio.get_writer(os.path.join("output", "combined.mp4"), fps=FPS)
            #     for frame in combined_frames:
            #         output_video.append_data(frame)
            #     output_video.close()

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
