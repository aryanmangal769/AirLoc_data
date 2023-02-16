# @title Colab Setup and Imports { display-mode: "form" }
# @markdown (double click to see the code)

import math
import os
import random
import sys

import git
import imageio
import magnum as mn
import numpy as np
import quaternion
import json

from matplotlib import pyplot as plt

# function to display the topdown map
from PIL import Image

import habitat_sim
from habitat_sim.utils import common as utils
from habitat_sim.utils import viz_utils as vut

"""
This scripts is to generate random poses. These poses are generated around some already present poses in form of input.

Input : Already present poses Format : json file
        .glb file of the scnene
Output :Updated json file for every room in the dataset.

"""

def make_cfg(settings):
    sim_cfg = habitat_sim.SimulatorConfiguration()
    sim_cfg.gpu_device_id = 0
    sim_cfg.scene_id = settings["scene"]
    sim_cfg.enable_physics = settings["enable_physics"]

    # Note: all sensors must have the same resolution
    sensor_specs = []

    color_sensor_spec = habitat_sim.CameraSensorSpec()
    color_sensor_spec.uuid = "color_sensor"
    color_sensor_spec.sensor_type = habitat_sim.SensorType.COLOR
    color_sensor_spec.resolution = [settings["height"], settings["width"]]
    color_sensor_spec.position = [0.0, settings["sensor_height"], 0.0]
    color_sensor_spec.sensor_subtype = habitat_sim.SensorSubType.PINHOLE
    sensor_specs.append(color_sensor_spec)

    depth_sensor_spec = habitat_sim.CameraSensorSpec()
    depth_sensor_spec.uuid = "depth_sensor"
    depth_sensor_spec.sensor_type = habitat_sim.SensorType.DEPTH
    depth_sensor_spec.resolution = [settings["height"], settings["width"]]
    depth_sensor_spec.position = [0.0, settings["sensor_height"], 0.0]
    depth_sensor_spec.sensor_subtype = habitat_sim.SensorSubType.PINHOLE
    sensor_specs.append(depth_sensor_spec)

    semantic_sensor_spec = habitat_sim.CameraSensorSpec()
    semantic_sensor_spec.uuid = "semantic_sensor"
    semantic_sensor_spec.sensor_type = habitat_sim.SensorType.SEMANTIC
    semantic_sensor_spec.resolution = [settings["height"], settings["width"]]
    semantic_sensor_spec.position = [0.0, settings["sensor_height"], 0.0]
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

def start_sim(glb):
    """
    This function generates a simulator and agent instance given a glb file for the scene.
    """

    test_scene = glb
    
    rgb_sensor = True  # @param {type:"boolean"}
    depth_sensor = True  # @param {type:"boolean"}
    semantic_sensor = True  # @param {type:"boolean"}

    sim_settings = {
        "width": 256,  # Spatial resolution of the observations
        "height": 256,
        "scene": test_scene,  # Scene path
        "default_agent": 0,
        "sensor_height": 1.5,  # Height of sensors in meters
        "color_sensor": rgb_sensor,  # RGB sensor
        "depth_sensor": depth_sensor,  # Depth sensor
        "semantic_sensor": semantic_sensor,  # Semantic sensor
        "seed": 1,  # used in the random navigation
        "enable_physics": False,  # kinematics only
    }
    
    cfg = make_cfg(sim_settings)
    # Needed to handle out of order cell run in Colab
    try:  # Got to make initialization idiot proof
        sim.close()
    except NameError:
        pass
    sim = habitat_sim.Simulator(cfg)
    
    random.seed(sim_settings["seed"])
    sim.seed(sim_settings["seed"])

    # Set agent state
    agent = sim.initialize_agent(sim_settings["default_agent"])
    agent_state = habitat_sim.AgentState()
    agent_state.position = np.array([-0.6, 0.0, 0.0])  # world space
    agent.set_state(agent_state)
    
    return sim,agent


def uniform_quat(original_angle):
    """
    Given a angle in form of quaternion. This script generated random quaternion angles arounf the given angle.
    """
    original_euler = quaternion.as_euler_angles(original_angle)
    euler_angles = np.array([(np.random.rand() - 0.5) * np.pi / 4. + original_euler[0],
                             (np.random.rand() - 0.5) * np.pi / 4. + original_euler[1],
                             (np.random.rand() - 0.5) * np.pi / 4. + original_euler[2]])
    quaternions = quaternion.from_euler_angles(euler_angles)
    
    
    return quaternions

def generate_random_viewpoints(init_pos,init_rot,pose_std,rot_std):
    """
    Driver script to generate random poses.
    Input : init_pose = Initial position around which random poses are required.
            init_rot = Initial rotation around which random poses are required.
            pose_std = No. of random position to be generated around given position
            rot_std = No. of random rotation to be generated around given rotation

    Position are only generated on navigable points (Not inside walls and all) using navmesh given in habitat_sim.

    For a complete overview go to : https://colab.research.google.com/github/facebookresearch/habitat-sim/blob/main/examples/tutorials/colabs/ECCV_2020_Navigation.ipynb#scrollTo=q7mFt6VnQLgB

    """
    global dict1
    observations = []    
    agent_state.position = init_pos
    agent_state.rotation = init_rot
    agent.set_state(agent_state)
    
                      
    for i in range(pose_std):
        #  print(agent.get_state())
        
        agent_state.rotation = init_rot
        agent.set_state(agent_state)
        
        for j in range(rot_std):
            
            #Append the observations to get the images
            observations.append(sim.get_sensor_observations())
            
            state = agent.get_state()

            pos = state.position
            rot = state.rotation
            rot = habitat_sim.utils.common.quat_to_coeffs(rot)
            
            dict1["position"].append(pos.tolist())
            dict1["rotation"].append(rot.tolist())
            
            rotation = uniform_quat(init_rot)
            agent_state.rotation = rotation
            agent.set_state(agent_state)
            
        position = sim.pathfinder.get_random_navigable_point_near(init_pos, 1 , max_tries=100)
        agent_state.position = position 
        agent.set_state(agent_state)
        
    print(dict1)
                   
    return observations


def modify_json(room_path):
    global dict1
    
    poses_json = os.path.join(room_path,"poses_cleaned.json")
    save_json_file =  os.path.join(room_path,"poses_cleaned_updated.json")
    
    with open(poses_json) as f:
        poses_data = json.load(f)
        
        position_array = [list(map(float,i)) for i in poses_data['position']]
        rotation_array = [list(map(float,i)) for i in poses_data['rotation']]

    poses_path = {
    'position': np.array(position_array),
    'rotation': np.array(rotation_array)
    }

    for i in range(len(poses_path["position"])):
        raw_position = poses_path['position'][i]
        raw_rotation = habitat_sim.utils.common.quat_from_coeffs(poses_path['rotation'][i])
        obs = generate_random_viewpoints(raw_position,raw_rotation,10,10) 
        
        

if __name__ == '__main__':
    # This script is to be run from within the utilities folder itself
    dataset_path = "../data_collection/x-view"

    # global dictionay
    
    dict1 = {'position':[], 'rotation':[]}
    
    datasets = ["mp3d"]
    for dataset in datasets:
        mp_path = os.path.join(dataset_path, dataset)

        for scene in os.listdir(mp_path):
            scene_path = os.path.join(mp_path, scene)
            glb_file = os.path.join(scene_path, "habitat", scene + '.glb')
            
            sim,agent = start_sim(glb_file)
            agent_state = agent.get_state()
                        
            rooms_path = os.path.join(scene_path, "rooms")
            
            for room in os.listdir(rooms_path):
                dict1 = {'position':[], 'rotation':[]}
                
                room_path = os.path.join(rooms_path, room)
                save_json_file =  os.path.join(room_path,"poses_cleaned_updated.json")
                
                modify_json(room_path)
                
                #Dict1 got updted in modify json function
                print(save_json_file)
                with open(save_json_file, "w") as out_file:
                    json.dump(dict1, out_file, indent=4, sort_keys=False)
                
            sim.close()