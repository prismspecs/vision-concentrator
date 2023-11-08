#!/bin/bash

# docker container running 1111
gnome-terminal --title "Docker" -- bash -c "docker compose --profile auto up; exec bash"

# terminal 4: text input script (with larger font size and fullscreen)
# gnome-terminal --title "Add Vision" --zoom 3 --full-screen -- bash -c "python3 add-vision.py; exec bash"

# # terminal 2: vision-concentrator.py (main script)
gnome-terminal --title "Terminal 2 - Vision Concentrator" -- bash -c "python3 vision-concentrator.py; exec bash"

# # terminal 3: video player
gnome-terminal --title "Terminal 3 - Video Player" -- bash -c "python3 vision-player.py; exec bash"

gnome-terminal --title "Terminal 4 - Node" -- bash -c "node index.js; exec bash"

# open firefox to localhost:3000
gnome-terminal --title "Terminal 5 - Launch Firefox" -- bash -c "firefox localhost:3000; exec bash"

# close Terminal 5
wmctrl -c "Terminal 5 - Launch Firefox"

# # Introduce an x-second delay before opening the fourth terminal
# sleep 3

# # terminal 4: text input script (with larger font size and fullscreen)
# gnome-terminal --title "Terminal 4 - Text Input" --zoom 3 --full-screen -- bash -c "python3 add-vision.py incoming.dat; exec bash" &


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
