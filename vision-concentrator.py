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

url = "http://127.0.0.1:7860"

payload = {
    "prompt": "puppy dog",
    "steps": 5
}


def get_current_datetime_string():
    now = datetime.datetime.now()
    date_time_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    return date_time_string


class NewLineHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command

    def on_modified(self, event):
        if event.src_path.endswith('inputs.csv') and event.is_directory == False:
            with open(event.src_path, 'r') as file:
                lines = file.readlines()
                if len(lines) > self.last_line_count:
                    new_lines = lines[self.last_line_count:]
                    self.last_line_count = len(lines)
                    self.run_command_on_new_lines(new_lines)

    def on_created(self, event):
        self.on_modified(event)

    def run_command_on_new_lines(self, new_lines):
        for line in new_lines:
            print("New line added to inputs.csv: ", line.strip())

            payload = {
                "prompt": line.strip(),
                "seed": 1,
                "width": 512,
                "height": 512,
                "steps": 20,
                "sampler_index": "DPM++ 2M",
                "script_name": "Seed travel",
                "script_args": [
                    "False",    # rnd_seed
                    "4.0",      # seed count
                    "2",        # dest seed
                    "3",       # steps
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
                    "output/new",     # save path
                    "filename2.mp4", # save filename
                ]
            }

            response = requests.post(
                url=f'{url}/sdapi/v1/txt2img', json=payload)
            r = response.json()

            # for i in r['images']:
            #     image = Image.open(io.BytesIO(
            #         base64.b64decode(i.split(",", 1)[0])))

            #     png_payload = {
            #         "image": "data:image/png;base64," + i
            #     }
            #     response2 = requests.post(
            #         url=f'{url}/sdapi/v1/png-info', json=png_payload)

            #     pnginfo = PngImagePlugin.PngInfo()
            #     pnginfo.add_text("parameters", response2.json().get("info"))

            #     filename = get_current_datetime_string() + ".png"

            #     image.save(filename, pnginfo=pnginfo)

            subprocess.run(self.command, shell=True)


if __name__ == "__main__":
    input_file = "inputs.csv"
    command_to_run = "echo 'New line added!'"
    event_handler = NewLineHandler(command_to_run)
    event_handler.last_line_count = 0

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
