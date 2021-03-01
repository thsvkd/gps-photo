import os
import argparse
import utils

parser = argparse.ArgumentParser(description='gps-photo')
parser.add_argument('--src', '-s', default='img_src', help='src image path')
parser.add_argument('--dst', '-d', default='img_dst', help='dst image path')
parser.add_argument('--gpsjsonpath', '-gps', default='Takeout',
                    help='Takeout folder path')
parser.add_argument('--timelinepath', '-tl', default='Timeline.json',
                    help='timeline file path')

if __name__ == "__main__":

    gpsjson_path = "Takeout"
    timeline_json_path = "Timeline.json"
    img_src_path = "img_src"
    img_dst_path = "img_dst"

    if not os.path.isfile(timeline_json_path):
        utils.MakeTimeline(timeline_json_path, os.path.join(
            gpsjson_path, '위치 기록', 'Semantic Location History'))
    utils.MakeGPSPhoto(img_dst_path, img_src_path, timeline_json_path)
