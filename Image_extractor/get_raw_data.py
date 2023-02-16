import habitat_sim
import random
#get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
import cv2
import PyQt5
import os

import numpy as np
import json
import png
from PIL import Image
from habitat_sim.utils.common import d3_40_colors_rgb


# Code for saving the video

import imageio
import tqdm
# from habitat_sim import logger #initially habitat was there
from typing import Dict, List, Optional, Tuple
import sys




def make_cfg(settings):
    sim_cfg = habitat_sim.SimulatorConfiguration()
    sim_cfg.gpu_device_id = 0
    sim_cfg.scene_id = settings["scene"]
    sim_cfg.enable_physics = settings["enable_physics"]
    # Note: all sensors must have the same resolution
    # Note: all sensors must have the same resolution
    sensor_specs = []

    color_sensor_spec = habitat_sim.CameraSensorSpec()
    color_sensor_spec.uuid = "color_sensor"
    color_sensor_spec.sensor_type = habitat_sim.SensorType.COLOR
    color_sensor_spec.resolution = [settings["height"], settings["width"]]
    color_sensor_spec.postition = [0.0, settings["sensor_height"], 0.0]
    color_sensor_spec.sensor_subtype = habitat_sim.SensorSubType.PINHOLE
    sensor_specs.append(color_sensor_spec)

    depth_sensor_spec = habitat_sim.CameraSensorSpec()
    depth_sensor_spec.uuid = "depth_sensor"
    depth_sensor_spec.sensor_type = habitat_sim.SensorType.DEPTH
    depth_sensor_spec.resolution = [settings["height"], settings["width"]]
    depth_sensor_spec.postition = [0.0, settings["sensor_height"], 0.0]
    depth_sensor_spec.sensor_subtype = habitat_sim.SensorSubType.PINHOLE
    sensor_specs.append(depth_sensor_spec)

    semantic_sensor_spec = habitat_sim.CameraSensorSpec()
    semantic_sensor_spec.uuid = "semantic_sensor"
    semantic_sensor_spec.sensor_type = habitat_sim.SensorType.SEMANTIC
    semantic_sensor_spec.resolution = [settings["height"], settings["width"]]
    semantic_sensor_spec.postition = [0.0, settings["sensor_height"], 0.0]
    semantic_sensor_spec.sensor_subtype = habitat_sim.SensorSubType.PINHOLE
    sensor_specs.append(semantic_sensor_spec)
            
    # Here you can specify the amount of displacement in a forward action and the turn angle
    agent_cfg = habitat_sim.agent.AgentConfiguration()
    agent_cfg.sensor_specifications = sensor_specs
    agent_cfg.action_space = {
        "move_forward": habitat_sim.agent.ActionSpec(
            "move_forward", habitat_sim.agent.ActuationSpec(amount=0.25)
        ),
        "turn_left": habitat_sim.agent.ActionSpec(
            "turn_left", habitat_sim.agent.ActuationSpec(amount=30.0)
        ),
        "turn_right": habitat_sim.agent.ActionSpec(
            "turn_right", habitat_sim.agent.ActuationSpec(amount=30.0)
        ),
    }
    
    return habitat_sim.Configuration(sim_cfg, [agent_cfg])


def print_scene_recur(scene, limit_output=10):
    print(f"House has {len(scene.levels)} levels, {len(scene.regions)} regions and {len(scene.objects)} objects")
    print(f"House center:{scene.aabb.center} dims:{scene.aabb.sizes}")
    
    count = 0
    for level in scene.levels:
        print(
            f"Level id:{level.id}, center:{level.aabb.center},"
            f" dims:{level.aabb.sizes}"
        )
        for region in level.regions:
            print(
                f"Region id:{region.id}, category:{region.category.name()},"
                f" center:{region.aabb.center}, dims:{region.aabb.sizes}"
            )
            for obj in region.objects:
                print(
                    f"Object id:{obj.id}, category:{obj.category.name()},"
                    f" center:{obj.aabb.center}, dims:{obj.aabb.sizes}"
                )
                count += 1
                if count >= limit_output:
                    return None

def display_save_sample(rgb_obs, semantic_obs, depth_obs, obs_id, save=True, save_viz = False, visualize=False):
    # Modified this function from GradGR: Now acc to xview
    # not using heavy np arrays. Just save
    # RGB: Same as before
    # Semantic: as one channel 16 bit image: values are unique instance ids, see "instance-labels-ALL-apartment_0.txt"
    # Depth: as one channel 16 bit image with values in cm (centimeters)


    # Save raw data
    if save:
        #np.save(raw_data_folder + str(obs_id) + "_rgb",rgb_obs)
        #np.save(raw_data_folder + str(obs_id) + "_instance-seg",semantic_obs)
        #np.save(raw_data_folder + str(obs_id) + "_depth",depth_obs)
        rgb_img_save = Image.fromarray(rgb_obs, mode="RGBA")
        rgb_img_save.save(raw_data_folder + str(obs_id) + "_rgb.png")

        semantic_obs_uint16 = semantic_obs.astype(np.uint16)
        depth_obs_cm_uint16 = (depth_obs*100).astype(np.uint16)


        with open(raw_data_folder + str(obs_id) + "_instance-seg.png", 'wb') as fsem:
            writer = png.Writer(width=semantic_obs_uint16.shape[1], height=semantic_obs_uint16.shape[0], bitdepth=16, greyscale=True)
            semantic_gray2list = semantic_obs_uint16.tolist()
            writer.write(fsem, semantic_gray2list)

        with open(raw_data_folder + str(obs_id) + "_depth.png", 'wb') as fdep:
            writer = png.Writer(width=depth_obs_cm_uint16.shape[1], height=depth_obs_cm_uint16.shape[0], bitdepth=16, greyscale=True)
            depth_gray2list = depth_obs_cm_uint16.tolist()
            writer.write(fdep, depth_gray2list)
    
    rgb_img = Image.fromarray(rgb_obs, mode="RGBA")
    
    semantic_img = Image.new("P", (semantic_obs.shape[1], semantic_obs.shape[0]))
    semantic_img.putpalette(d3_40_colors_rgb.flatten())
    semantic_img.putdata((semantic_obs.flatten() % 40).astype(np.uint8))
    semantic_img = semantic_img.convert("RGBA")
    
    depth_img = Image.fromarray((depth_obs / 10 * 255).astype(np.uint8), mode="L")

    # Save visualization data
    if save_viz:
        rgb_img.save(viz_data_folder + str(obs_id) + "_rgb.png")
        semantic_img.save(viz_data_folder + str(obs_id) + "_instance-seg.png")
        depth_img.save(viz_data_folder + str(obs_id) + "_depth.png")
        print()
    # visualize first 3 frames
    if visualize and (obs_id < 3):
        arr = [rgb_img, semantic_img, depth_img]
        titles = ['rgb', 'semantic', 'depth']
        plt.figure(figsize=(12 ,8))
        for i, data in enumerate(arr):
            ax = plt.subplot(1, 3, i+1)
            ax.axis('off')
            ax.set_title(titles[i])
            plt.imshow(data, cmap='gray')
        plt.show()
    


def img_to_video(images: List[np.ndarray],
                output_dir: str,
                video_name: str,
                fps: int = 60,
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
    for im in tqdm.tqdm(images):
        writer.append_data(im)
    writer.close()



if __name__ == '__main__':
    """
    Usage
    python get_raw_data.py <dataset> <scene> <room>
    """
    if len(sys.argv) < 2:
        print("not enough arguments. Please refer to usage")
        exit()
    args = sys.argv
    dataset_name = args[1]
    scene_name = args[2]
    room_name = args[3]
    

    x_view_path = "../data_collection/x-view/"
    dataset_path = os.path.join(x_view_path, dataset_name)
    scene_path = os.path.join(dataset_path, scene_name)
    glb_file = os.path.join(scene_path, "habitat", scene_name + '.glb')
    test_scene = glb_file

    room_path = os.path.join(scene_path, "rooms", room_name)
    print(room_path, os.path.isdir(room_path))
    # Whether you want to save a video correpsonding to robot trajectory, its path and name.
    save_video = False
    video_path = os.path.join(room_path,'video/')
    video_name = 'data_run_video'
    # Set poses file path (corresponding to which data will be extracted)
    poses_json = os.path.join(room_path,"poses_cleaned_updated.json")
    # poses_json = os.path.join(room_path,"poses_cleaned.json")
    # # Set to which paths you want to save raw data and visualization data  
    raw_data_folder = os.path.join(room_path,"raw_data/") 
    if not os.path.isdir(raw_data_folder):
        os.makedirs(raw_data_folder)
    viz_data_folder = os.path.join(room_path,"viz_data/")
    if not os.path.isdir(viz_data_folder):
        os.makedirs(viz_data_folder)
    print(video_path)
    print(poses_json, os.path.isfile(poses_json))
    print(raw_data_folder)
    print(viz_data_folder)


    # print(raw_data_folder,"\n\n printing this \n\n")
    rgb_sensor = True  # @param {type:"boolean"}
    depth_sensor = True  # @param {type:"boolean"}
    semantic_sensor = True  # @param {type:"boolean"}
    #TODO 2: Set settings like spatial resolution
    sim_settings = {
        "width": 1920,  # Spatial resolution of the observations    
        "height": 1080,
        "scene": test_scene,  # Scene path
        "default_agent": 0,  
        "sensor_height": 1.5,  # Height of sensors in meters
        "color_sensor": rgb_sensor,  # RGB sensor
        "semantic_sensor": semantic_sensor,  # Semantic sensor
        "depth_sensor": depth_sensor,  # Depth sensor
        "seed": 1,
        "enable_physics": False,
    }

    cfg = make_cfg(sim_settings)
    sim = habitat_sim.Simulator(cfg)
    # Print semantic annotation information (id, category, bounding box details) 
    # about levels, regions and objects in a hierarchical fashion
    scene = sim.semantic_scene
    print_scene_recur(scene)

    # Set agent state
    with open(poses_json) as f:
        poses_data = json.load(f)
        
        position_array = [list(map(float,i)) for i in poses_data['position']]
        rotation_array = [list(map(float,i)) for i in poses_data['rotation']]

    poses_path = {
    'position': np.array(position_array),
    'rotation': np.array(rotation_array)
    }

    agent = sim.initialize_agent(sim_settings["default_agent"])
    agent_state = habitat_sim.AgentState()
    agent_state.position = poses_path['position'][0]
    agent_state.rotation = habitat_sim.utils.common.quat_from_coeffs(poses_path['rotation'][0])
    agent.set_state(agent_state)

    # Get agent state
    agent_state = agent.get_state()
    print("AGENT'S INITIAL STATE: position", agent_state.position, "rotation", (agent_state.rotation))



    total_frames = 0
    action_names = list(
        cfg.agents[
            sim_settings["default_agent"]
        ].action_space.keys()
    )

    images_for_video = []

    # TODO 4: Set how many datapoints you want to extract. If all the poses, then uncomment len() in the next line..
    max_frames = len(poses_path['position']) 
    print("\n\nSAVING FIRST {} DATAPOINTS (RGB, DEPTH & INSTANCE) HAS STARTED. THE FOLLOWING ARE THE POSES CORRESPONDING TO WHICH DATA IS BEING EXTRACTED.\n\n".format(max_frames))
    while total_frames < max_frames:
        agent_state.position = poses_path['position'][total_frames]
        agent_state.rotation = habitat_sim.utils.common.quat_from_coeffs(poses_path['rotation'][total_frames])
        agent.set_state(agent_state)
        
        observations = sim.get_sensor_observations()
        rgb = observations["color_sensor"]
        semantic = observations["semantic_sensor"]
        depth = observations["depth_sensor"]
        

        # Saving video: adding ID on top of every frame
        org = (50, 50); color = (255, 0, 0); thickness = 4; fontScale = 1; font = cv2.FONT_HERSHEY_SIMPLEX
        rgb_vid = cv2.putText(rgb, "ID: " + str(total_frames), org, font, fontScale, color, thickness, cv2.LINE_AA)
        images_for_video.append(rgb_vid)
        

        display_save_sample(rgb, semantic, depth, total_frames, save=True, visualize=False)
        
        agent_state = agent.get_state()
        print("AGENT_STATE: position", agent_state.position, "rotation", agent_state.rotation)

        total_frames += 1

    if save_video:
        print(" \n \n VIDEO CORRESPONDING TO THE DATAPOINTS EXTRACTED IS BEING WRITTEN NOW --\n\n")
        img_to_video(images_for_video, video_path, video_name)