from PIL import Image
from PIL.ExifTags import TAGS
import piexif
import os
import json
import time
import datetime
import utils


if __name__ == "__main__":

    gpsjson_path = r"Takeout/위치 기록/Semantic Location History"
    timeline_json_path = "Timeline.json"
    img_path = r"D:/OneDrive - SNU/추억/사진/G7X mark lll/2020_04_13/IMG_0058.JPG"
    img_export_path = r"C:/Users/thsxo/Desktop/test.jpg"
    img_src_path = "img_src"
    img_dst_path = "img_dst"

    # utils.make_timeline(timeline_json_path, gpsjson_path)
    utils.MakeGPSphoto(img_dst_path, img_src_path, timeline_json_path)
