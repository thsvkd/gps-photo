from PIL import Image
from PIL.ExifTags import TAGS
import piexif
import os
import json
import time
import datetime
from tqdm import tqdm


def AppendGPSInfo(timeline, time, latitude, longitude):
    timeline.append({"time": time,
                     "latitudeE7": latitude,
                     "longitudeE7": longitude})
    return timeline


def MakeTimeline(timeline_json_path, json_path):

    # open json folder
    year_list = os.listdir(json_path)
    wholetimeline = []

    for year in tqdm(year_list, desc='years parsing'):
        # print("processing %syear folder..." % year)
        month_list = os.listdir(os.path.join(json_path, year))

        yeartimeline = []

        for month in month_list:
            # print("processing %s folder..." % month)

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
                            AppendGPSInfo(
                                monthtimeline, startTimestampMs, startLocation['latitudeE7'], startLocation['longitudeE7'])
                        except KeyError:
                            continue

                        if 'simplifiedRawPath' in activitySegment:
                            simplifiedRawPath = activitySegment['simplifiedRawPath']

                            for j in simplifiedRawPath['points']:
                                AppendGPSInfo(
                                    monthtimeline, j['timestampMs'], j['latE7'], j['lngE7'])

                        AppendGPSInfo(
                            monthtimeline, endTimestampMs, endLocation['latitudeE7'], endLocation['longitudeE7'])

                    elif 'placeVisit' in i:
                        placeVisit = i['placeVisit']
                        location = placeVisit['location']
                        duration = placeVisit['duration']
                        startTimestampMs = duration['startTimestampMs']
                        endTimestampMs = duration['endTimestampMs']

                        AppendGPSInfo(monthtimeline, startTimestampMs,
                                      location['latitudeE7'], location['longitudeE7'])
                        AppendGPSInfo(
                            monthtimeline, endTimestampMs, location['latitudeE7'], location['longitudeE7'])

            yeartimeline += monthtimeline
        yeartimeline = sorted(yeartimeline, key=(lambda x: x['time']))
        wholetimeline += yeartimeline

    wholetimeline = {"timelineObj": wholetimeline}
    f = open(timeline_json_path, "w")
    json.dump(wholetimeline, f, indent=4)


def MakeGPSPhoto(img_dst_path, img_src_path, timeline_json_path='Timeline.json'):
    file_list = os.listdir(img_src_path)

    f = open(os.path.join(timeline_json_path), encoding='UTF8')
    json_obj = json.load(f)
    f.close()

    json_obj = json_obj['timelineObj']

    for img_name in tqdm(file_list, desc='processing images'):
        if img_name.split('.')[1] == 'md':
            continue
        img = Image.open(os.path.join(img_src_path, img_name))
        exif = piexif.load(img.info['exif'])

        unixtime = Date2Unixtime(exif['0th'][306].decode())

        for i, point in enumerate(json_obj):
            if int(point['time']) < unixtime and int(json_obj[i + 1]['time']) > unixtime:
                latitudeE7_list, longitudeE7_list = DegreeConversion(point)

                exif['GPS'][1] = b'N'
                exif['GPS'][2] = (
                    (latitudeE7_list[0], 1), (latitudeE7_list[1], 1), (latitudeE7_list[2], 1000000))
                exif['GPS'][3] = b'E'
                exif['GPS'][4] = (
                    (longitudeE7_list[0], 1), (longitudeE7_list[1], 1), (longitudeE7_list[2], 1000000))

                exif_bytes = piexif.dump(exif)
                img.save(os.path.join(img_dst_path, img_name),
                         "jpeg", exif=exif_bytes)
                break


def Date2Unixtime(time_stamp):
    time_stamp = time_stamp.split()
    time_stamp[0] = time_stamp[0].split(':')
    time_stamp[1] = time_stamp[1].split(':')

    unixtime = datetime.datetime.strptime("%s-%s-%s %s:%s:%s" % (time_stamp[0][0],
                                                                 time_stamp[0][1],
                                                                 time_stamp[0][2],
                                                                 time_stamp[1][0],
                                                                 time_stamp[1][1],
                                                                 time_stamp[1][2]),
                                          '%Y-%m-%d %H:%M:%S').timestamp()

    unixtime *= 1000
    unixtime = int(unixtime)
    return unixtime


def DegreeConversion(point):
    latitudeE7 = point['latitudeE7'] / 10000000
    longitudeE7 = point['longitudeE7'] / 10000000
    latitudeE7_list = []
    longitudeE7_list = []

    latitudeE7_list.append(int(latitudeE7 // 1))
    latitudeE7 = (latitudeE7 - latitudeE7 // 1) * 60
    latitudeE7_list.append(int(latitudeE7 // 1))
    latitudeE7 = (latitudeE7 - latitudeE7 // 1) * 60
    latitudeE7_list.append(int(latitudeE7 * 1000000))

    longitudeE7_list.append(int(longitudeE7 // 1))
    longitudeE7 = (longitudeE7 - longitudeE7 // 1) * 60
    longitudeE7_list.append(int(longitudeE7 // 1))
    longitudeE7 = (longitudeE7 - longitudeE7 // 1) * 60
    longitudeE7_list.append(int(longitudeE7 * 1000000))

    return latitudeE7_list, longitudeE7_list
