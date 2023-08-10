cat *.mp4 | ffmpeg -i pipe -c:a copy -c:v copy all.mp4
