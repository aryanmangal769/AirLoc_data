import argparse
import glob
import os
import numpy as np
from pathlib import Path
from shutil import copy2 
import imageio
import cv2
from tqdm import tqdm
from typing import Dict, List, Optional, Tuple
import sys

def img_to_video(images: List[np.ndarray],
                output_dir: str,
                video_name: str,
                fps: int = 3,
                quality: Optional[float] = 5,
                **kwargs,):
    
    assert 0 <= quality <= 10
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    video_name = video_name.replace(" ", "_").replace("\n", "_") + ".mp4"
    writer = imageio.get_writer(
        os.path.join(output_dir, video_name),
        fps=fps,
        quality=quality,
        **kwargs,
    )
    # logger.info(f"Video created: {os.path.join(output_dir, video_name)}")
    for im in tqdm(images):
        writer.append_data(im)
    writer.close()

def rooms_combine(mp3d_path, scene_name):
    scene_path = mp3d_path + scene_name + "/"
    room_names = []
    rooms_path = Path(scene_path + 'rooms/')
    list_rooms_path = (list(rooms_path.iterdir()))
    for room in list_rooms_path:
        room_names.append(room.stem)
#    room_name = room_names[0] 
    images_for_video = []
    for room_name in room_names:
        room_path = 'rooms/' + room_name + '/viz_data/'

        full_path = scene_path + room_path

        org = (150, 50); color = (255, 0, 0); thickness = 4; fontScale = 1.5; font = cv2.FONT_HERSHEY_SIMPLEX
        for image_path in glob.glob(full_path + "*_rgb.png"):
            image = imageio.imread(image_path)
            image_vid = cv2.putText(image, "scene: " + scene_name + " room: " + room_name, \
                org, font, fontScale, color, thickness, cv2.LINE_AA)
            images_for_video.append(image_vid)


    img_to_video(images_for_video, scene_path, scene_name + "_video")

if __name__ == '__main__':
    scene_names = [
   "8WUmhLawc2A",
   "EDJbREhghzL",
   "i5noydFURQK",
   "jh4fc5c5qoQ",
   "mJXqzFtmKg4",
   "qoiz87JEwZ2",
   "RPmz2sHmrrY",
   "S9hNv5qa7GM",
   "ULsKaCPVFJR",
   "VzqfbhrpDEA",
   "wc2JMjhGNzB",
   "WYY7iVyf5p8",
   "X7HyMhZNoso",
   "YFuZgdQ5vWj",
   "yqstnuAEVhm"
]

    #scene_name = scene_names[0] 
    mp3d_path = '../data_collection/x-view/mp3d/'
    for scene_name in scene_names:
        rooms_combine(mp3d_path, scene_name)