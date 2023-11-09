# Vision Concentrator art installation=
forked with love from [Stable Diffusion WebUI docker](https://github.com/AbdBarho/stable-diffusion-webui-docker/)

# Setup & Install
## Requirements
```bash
sudo ubuntu-drivers autoinstall
sudo apt install ffmpeg python3-pip nodejs npm
pip install -r requirements.txt
npx express && npm install --save @iamtraction/google-translate
```
+ Docker
```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# post install
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker

# verify installation
docker run hello-world

```
+ NVidia container toolkit
```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list \
  && \
    sudo apt-get update

sudo apt-get install -y nvidia-container-toolkit

# test installation
sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi


```

## Installation
```
docker compose --profile download up --build
docker compose --profile auto up --build
```

+ Install my fork of seed travel: https://github.com/prismspecs/seed_travel via the browser interface
+ Install my fork of interpolate: https://github.com/prismspecs/interpolate by placing it in the scripts folder directly
+ Add vision-concentrator to startup
```
gnome-terminal --working-directory=/home/grayson/workbench/vision-concentrator -- bash -c "/home/grayson/workbench/vision-concentrator/start.sh"
```

# Useage
```bash
./start.sh
```

# Technical overview
The start.sh script launches:
+ a Docker container which contains automatic1111
+ a Node.js server which has
    + a command menu (to select/create active project) at http://127.0.0.1:3000
    + an input interface for users to upload visions at http://127.0.0.1:3000/input
        + new visions goto the project directory's incoming.dat file
+ a Python video player which constantly looks for updates to all_visions.mp4 and plays this file on a loop
+ a Python script (vision_concentrator.py) which monitors the project directory specified in current_config.dat for changes to incoming.dat, and sends these as requests to A1111