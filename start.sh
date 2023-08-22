#!/bin/bash

# terminal 1: docker container running 1111
gnome-terminal -- bash -c "docker compose --profile auto up"

# terminal 2: vision-concentrator.py (main script)
gnome-terminal -- bash -c "python3 vision-concentrator.py"

# terminal 3: text input script
python3 add-vision.py incoming.dat

# terminal 4: video player
python3 vision-player.py