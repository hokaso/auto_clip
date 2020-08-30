from __future__ import print_function
import os

# Standard PySceneDetect imports:
from scenedetect.video_splitter import split_video_ffmpeg
from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
# For caching detection metrics and saving/loading to a stats file
from scenedetect.stats_manager import StatsManager

# For content-aware scene detection:
from scenedetect.detectors.content_detector import ContentDetector

input_dir = './input'
output_dir = 'output'
threshold=27.5

def find_scenes(video_path):

    video_manager = VideoManager([video_path])
    stats_manager = StatsManager()
    # Construct our SceneManager and pass it our StatsManager.
    scene_manager = SceneManager(stats_manager)

    # Add ContentDetector algorithm (each detector's constructor
    # takes detector options, e.g. threshold).
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    base_timecode = video_manager.get_base_timecode()

    try:

        # Set downscale factor to improve processing speed.
        video_manager.set_downscale_factor()

        # Start video_manager.
        video_manager.start()

        # Perform scene detection on video_manager.
        scene_manager.detect_scenes(frame_source=video_manager)

        # Obtain list of detected scenes.
        scene_list = scene_manager.get_scene_list(base_timecode)
        # Each scene is a tuple of (start, end) FrameTimecodes.

        print('List of scenes obtained:')
        final_scene_list = []
        for i, scene in enumerate(scene_list):
            temp = list(scene)
            # print(temp)
            temp[0] = temp[0] + 1
            temp[1] = temp[1] - 1
            scene = tuple(temp)
            final_scene_list.append(scene)

    finally:
        video_manager.release()

    return final_scene_list

def file_prepare():
    file_list = []
    for root, dirs, files in os.walk(input_dir):
        file_list = [input_dir+"/"+i for i in files]
    return file_list

_file_list = file_prepare()
for key in _file_list:
    scenes = find_scenes(key)
    print(scenes)
    file_path, full_name = os.path.split(key)
    f_name, ext = os.path.splitext(full_name)
    split_video_ffmpeg([key], scenes, "$VIDEO_NAME - Scene $SCENE_NUMBER.mp4", output_dir+"/"+f_name, arg_override='-c:v libx264 -preset slow -crf 20 -c:a aac', hide_progress=False, suppress_output=False)

