import habitat_sim

import random
import matplotlib.pyplot as plt
import PyQt5
import os

import numpy as np
import json
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



if __name__ == '__main__':
	"""
	usage example:
	python get_scene_objects.py mp3d 8WUmhLawc2A
	This script will save semantic information 
	in the corresponding scene folder
	"""
	if len(sys.argv) < 2:
		print("not enough arguments. Please refer to usage")
		exit()
	args = sys.argv
	print(args)
	dataset = args[1]
	scene_name = args[2]
	print(dataset, scene_name)

	data_folder = "../data_collection/x-view"
	data_folder = os.path.join(data_folder, dataset)
	test_scene = os.path.join(data_folder, scene_name)

	file_save_path = os.path.join(test_scene,"classes.txt")

	test_scene_habitat = os.path.join(test_scene, "habitat")
	test_scene_habitat = os.path.join(test_scene_habitat, scene_name + ".glb")
	
	print(test_scene_habitat, os.path.isfile(test_scene_habitat))
	print(file_save_path)

	# test_scene = "/media/aryan/DATA/Gibson_structured/mp3d_habitat/mp3d/mJXqzFtmKg4/mJXqzFtmKg4.glb"
	rgb_sensor = True  # @param {type:"boolean"}
	depth_sensor = True  # @param {type:"boolean"}
	semantic_sensor = True  # @param {type:"boolean"}
	#TODO 2: Set settings like spatial resolution
	sim_settings = {
		"width": 1920,  # Spatial resolution of the observations    
		"height": 1080,
		"scene": test_scene_habitat,  # Scene path
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
	scene = sim.semantic_scene
	i=0
	with open(file_save_path,"w") as file1:
		while i < len(scene.objects): 
			if scene.objects[i] and scene.objects[i].category is not None:
				print(i)
				L = (f"{scene.objects[i].id} {scene.objects[i].category.name()} \n")
				file1.writelines(L)
			i = i+1