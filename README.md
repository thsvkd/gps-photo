# gps-photo

In this project you can insert location information using our location information collected by Google in photos without gps information.

## requirements

- PIL.Image
- PIL.ExifTags
- piexif
- tqdm.tqdm

## install

`pip install -r requirements.txt`

## use gps-photo

### window

`python.exe .\src\main.py -s img_src -d img_dst -gps Takeout -tl Timeline.json`

### linux

`python src/main.py -s img_src -d img_dst -gps Takeout -tl Timeline.json`

## parameter

python src/main.py -s [image source folder path] -d [image destination folder path] -gps [google's Takeout folder path] -tl [Timeline.json's path]
