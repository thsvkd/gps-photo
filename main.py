from PIL import Image
from PIL.ExifTags import TAGS
import piexif
import os
import json
import time
import datetime

wholeTimeline = []

# def get_exif(path):
#     img = Image.open('C:/Users/thsxo/OneDrive/사진/카메라 앨범/20210102_152853.jpg')
#     exif_dict = piexif.load(img.info['exif'])

#     Altitude = exif_dict['GPS'][2]
#     exif_dict['GPS'][2] = ((30, 1), (31, 1), (32058120, 1000000))
#     print(Altitude)
#     longitude = exif_dict['GPS'][4]
#     exif_dict['GPS'][4] = ((100, 1), (55, 1), (31866240, 1000000))
#     print(longitude)

#     # ((37, 1), (31, 1), (32058120, 1000000))
#     # ((126, 1), (55, 1), (31866240, 1000000))

#     exif_bytes = piexif.dump(exif_dict)
#     img.save('C:/Users/thsxo/Desktop/test', "jpeg", exif=exif_bytes)


# def get_GPS(path):
#     jsonObj = json.load(path)

def append_GPSInfo(time, latitude, longitude):
    wholeTimeline.append({"time": time,
                          "latitudeE7": latitude,
                          "longitudeE7": longitude})


if __name__ == "__main__":
    json_path = r"Takeout/위치 기록/Semantic Location History/2021/2021_JANUARY.json"
    json_export_path = "wholeTimeline.json"
    img_path = r"D:/OneDrive - SNU/추억/사진/G7X mark lll/2020_04_13/IMG_0058.JPG"
    img_export_path = r"C:/Users/thsxo/Desktop/test.jpg"

    f = open(json_path, encoding='UTF8')
    json_obj = json.load(f)
    f.close()

    # if exif['GPS'][0] == (2, 3, 0, 0):
    #     print("No GPS info in the photo...")

    # {0: (2, 3, 0, 0), 8: b'', 9: b'V', 18: b'WGS-84'}

    timeline_obj = json_obj['timelineObjects']
    for i in timeline_obj:
        if 'activitySegment' in i:
            activitySegment = i['activitySegment']

            startLocation = activitySegment['startLocation']
            endLocation = activitySegment['endLocation']
            duration = activitySegment['duration']
            startTimestampMs = duration['startTimestampMs']
            endTimestampMs = duration['endTimestampMs']
            simplifiedRawPath = []

            append_GPSInfo(
                startTimestampMs, startLocation['latitudeE7'], startLocation['longitudeE7'])

            if 'simplifiedRawPath' in activitySegment:
                simplifiedRawPath = activitySegment['simplifiedRawPath']

                for j in simplifiedRawPath['points']:
                    append_GPSInfo(j['timestampMs'], j['latE7'], j['lngE7'])

            append_GPSInfo(
                endTimestampMs, endLocation['latitudeE7'], endLocation['longitudeE7'])

        elif 'placeVisit' in i:
            placeVisit = i['placeVisit']
            location = placeVisit['location']
            duration = placeVisit['duration']
            startTimestampMs = duration['startTimestampMs']
            endTimestampMs = duration['endTimestampMs']

            append_GPSInfo(startTimestampMs, location['latitudeE7'], location['longitudeE7'])
            append_GPSInfo(endTimestampMs, location['latitudeE7'], location['longitudeE7'])


    wholeTimeline = {"timelineObj": wholeTimeline}
    f = open(json_export_path, "w")
    json.dump(wholeTimeline, f, indent=4)


    img_src_path = "img_src"
    img_dst_path = "img_dst"

    file_list = os.listdir(img_src_path)

    for img_name in file_list:
        img = Image.open(os.path.join(img_src_path, img_name))
        exif = piexif.load(img.info['exif'])
        time_stamped = exif['0th'][306].decode()
        time_stamped = time_stamped.split()
        time_stamped[0] = time_stamped[0].split(':')
        time_stamped[1] = time_stamped[1].split(':')

        exif['GPS'][1] = b'N'
        exif['GPS'][2] = ((30, 1), (31, 1), (32058120, 1000000))
        exif['GPS'][3] = b'E'
        exif['GPS'][4] = ((100, 1), (55, 1), (31866240, 1000000))

        exif_bytes = piexif.dump(exif)
        img.save(os.path.join(img_dst_path, img_name), "jpeg", exif=exif_bytes)
