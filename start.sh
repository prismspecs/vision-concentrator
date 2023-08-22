#!/bin/bash

# terminal 1: docker container running 1111
gnome-terminal -- bash -c "docker compose --profile auto up" & sleep 5

# terminal 2: vision-concentrator.py (main script)
gnome-terminal -- bash -c "python3 vision-concentrator.py" &

# terminal 3: text input script (with larger font size and fullscreen)
gnome-terminal --zoom 3 --full-screen -- bash -c "python3 add-vision.py incoming.dat" &

# terminal 4: video player
gnome-terminal -- bash -c "python3 vision-player.py" &


# some more ideas...

# gnome-terminal -- bash -c "python3 add-vision.py incoming.dat"

# # Find the PID of the terminal with "add-vision.py" in its command line
# pid=$(pgrep -f "python3 add-vision.py incoming.dat")

# # Move the terminal to a specific monitor (adjust the monitor number as needed)
# DISPLAY=:0.1 wmctrl -r :ACTIVE: -e 0,1920,0,-1,-1

# # Resize the terminal (adjust dimensions as needed)
# DISPLAY=:0.1 wmctrl -r :ACTIVE: -e 0,-1,-1,1920,1080

# # Focus the terminal
# DISPLAY=:0.1 wmctrl -i -a "$pid"
