# gps-photo

In this project you can insert location information using our location information collected by Google in photos without gps information.

## requirements

- PIL.Image
- PIL.ExifTags
- piexif
- tqdm.tqdm

## install

`pip install -r requirements.txt`

## using gps-photo

### window

`python.exe .\src\main.py -s img_src -d img_dst -gps Takeout -tl Timeline.json`

### linux

`python src/main.py -s img_src -d img_dst -gps Takeout -tl Timeline.json`

## parameter

### --src, -s

image source folder path

ex) `-s img_src`

### --dst, -d

image destination folder path

ex) `-d img_dst`

### --gpsjsonpath, -gps

google's Takeout folder's path

ex) `-gps Takeout`

### --timelinepath, -tl

Timeline.json's path

ex) `-tl Timeline.json`
