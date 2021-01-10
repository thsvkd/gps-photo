from PIL import Image
from PIL.ExifTags import TAGS
import piexif
import os
import json
import time
import datetime


if __name__ == "__main__":
    src_img_path = 'img_src/IMG_2409.JPG'
    dst_img_path = 'img_dst/result.jpg'

    img = Image.open(os.path.join(src_img_path))
    exif = piexif.load(img.info['exif'])
    gps_info = exif['GPS']
    print(gps_info)

    # "latitudeE7" :  375127968,
    # "longitudeE7" : 1268820604,

    exif['GPS'][1] = b'N'
    exif['GPS'][2] = ((37, 1), (51, 1), (27968000, 1000000))
    exif['GPS'][3] = b'E'
    exif['GPS'][4] = ((126, 1), (88, 1), (20604000, 1000000))
    
    # 37°51'27.9"N 126°88'20.6"E

    exif_bytes = piexif.dump(exif)
    img.save(os.path.join(dst_img_path), "jpeg", exif=exif_bytes)