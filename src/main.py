from PIL import Image
from PIL.ExifTags import TAGS
import piexif
import os
import json
import time
import datetime


def append_GPSInfo(timeline, time, latitude, longitude):
    timeline.append({"time": time,
                     "latitudeE7": latitude,
                     "longitudeE7": longitude})
    return timeline


def make_timeline(timeline_json_path, json_path):

    # open json folder
    year_list = os.listdir(json_path)
    wholetimeline = []

    for year in year_list:
        print("processing %syear folder..." % year)
        month_list = os.listdir(os.path.join(json_path, year))

        yeartimeline = []

        for month in month_list:
            print("processing %s folder..." % month)

            monthtimeline = []

            if month.split('.')[1] != 'json':
                continue
            else:
                f = open(os.path.join(json_path, year, month), encoding='UTF8')
                json_obj = json.load(f)
                f.close()

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

                        try:
                            append_GPSInfo(
                                monthtimeline, startTimestampMs, startLocation['latitudeE7'], startLocation['longitudeE7'])
                        except KeyError:
                            continue

                        if 'simplifiedRawPath' in activitySegment:
                            simplifiedRawPath = activitySegment['simplifiedRawPath']

                            for j in simplifiedRawPath['points']:
                                append_GPSInfo(
                                    monthtimeline, j['timestampMs'], j['latE7'], j['lngE7'])

                        append_GPSInfo(
                            monthtimeline, endTimestampMs, endLocation['latitudeE7'], endLocation['longitudeE7'])

                    elif 'placeVisit' in i:
                        placeVisit = i['placeVisit']
                        location = placeVisit['location']
                        duration = placeVisit['duration']
                        startTimestampMs = duration['startTimestampMs']
                        endTimestampMs = duration['endTimestampMs']

                        append_GPSInfo(monthtimeline, startTimestampMs,
                                       location['latitudeE7'], location['longitudeE7'])
                        append_GPSInfo(
                            monthtimeline, endTimestampMs, location['latitudeE7'], location['longitudeE7'])

                # monthtimeline = {"%s" % month: monthtimeline}
                # wholetimeline.append(monthtimeline)

            # monthtimeline = sorted(monthtimeline, key=(lambda x: x['time']))
            yeartimeline += monthtimeline
        yeartimeline = sorted(yeartimeline, key=(lambda x: x['time']))
        wholetimeline += yeartimeline
        # yeartimeline = {"%s" % year: yeartimeline}
        # wholetimeline.append(yeartimeline)

    # save timeline.json

    # wholetimeline = sorted(wholetimeline, key=(lambda x: x['time']))

    wholetimeline = {"timelineObj": wholetimeline}
    f = open(timeline_json_path, "w")
    json.dump(wholetimeline, f, indent=4)


def make_gps_photo(img_dst_path, img_src_path, timeline_json_path='Timeline.json'):
    file_list = os.listdir(img_src_path)

    f = open(os.path.join(timeline_json_path), encoding='UTF8')
    json_obj = json.load(f)
    f.close()

    json_obj = json_obj['timelineObj']

    for img_name in file_list:
        img = Image.open(os.path.join(img_src_path, img_name))
        exif = piexif.load(img.info['exif'])
        time_stamped = exif['0th'][306].decode()
        time_stamped = time_stamped.split()
        time_stamped[0] = time_stamped[0].split(':')
        time_stamped[1] = time_stamped[1].split(':')

        unixtime = datetime.datetime.strptime("%s-%s-%s %s:%s:%s" % (time_stamped[0][0],
                                                                     time_stamped[0][1],
                                                                     time_stamped[0][2],
                                                                     time_stamped[1][0],
                                                                     time_stamped[1][1],
                                                                     time_stamped[1][2]),
                                              '%Y-%m-%d %H:%M:%S').timestamp()
        unixtime *= 1000
        # 한국은 UTC 기준 -9시간 시차가 있어서 출력되는 값은 ((UTC 기준 unixtime) - 9h) 가 출력 된다...
        # 1596185332.0
        # 1610274357575
        # 375268140
        #  10000000
        # 1268750210


        for i, point in enumerate(json_obj):
            if int(point['time']) < unixtime and int(json_obj[i + 1]['time']) > unixtime:
                print("%s -> %s -> %s" %
                      (point['time'], unixtime, json_obj[i + 1]['time']))

                latitudeE7 = point['latitudeE7'] / 10000000
                longitudeE7 = point['longitudeE7'] / 10000000
                latitudeE7_list = []
                longitudeE7_list = []

                # TODO: thsvkd
                # make degree translater
                latitudeE7 = latitudeE7 // 1
                latitudeE7_list.append(int(latitudeE7 // 1))
                latitudeE7 = latitudeE7 * 60 // 1
                latitudeE7_list.append(int(latitudeE7))
                latitudeE7 = latitudeE7 * 60 // 1
                latitudeE7_list.append(int(latitudeE7 * 10000))

                longitudeE7 //= 1
                longitudeE7_list.append(int(longitudeE7))
                longitudeE7 = longitudeE7 * 60 // 1
                longitudeE7_list.append(int(longitudeE7))
                longitudeE7 = longitudeE7 * 60 // 1
                longitudeE7_list.append(int(longitudeE7 * 10000))
                
                #####################################################


                exif['GPS'][1] = b'N'
                exif['GPS'][2] = ((latitudeE7_list[0], 1), (latitudeE7_list[1], 1), (latitudeE7_list[2], 1000000))
                exif['GPS'][3] = b'E'
                exif['GPS'][4] = ((longitudeE7_list[0], 1), (longitudeE7_list[1], 1), (longitudeE7_list[2], 1000000))

        exif_bytes = piexif.dump(exif)
        img.save(os.path.join(img_dst_path, img_name), "jpeg", exif=exif_bytes)


if __name__ == "__main__":

    gpsjson_path = r"Takeout/위치 기록/Semantic Location History"
    timeline_json_path = "Timeline.json"
    img_path = r"D:/OneDrive - SNU/추억/사진/G7X mark lll/2020_04_13/IMG_0058.JPG"
    img_export_path = r"C:/Users/thsxo/Desktop/test.jpg"
    img_src_path = "img_src"
    img_dst_path = "img_dst"

    # make_timeline(timeline_json_path, gpsjson_path)
    make_gps_photo(img_dst_path, img_src_path, timeline_json_path)
