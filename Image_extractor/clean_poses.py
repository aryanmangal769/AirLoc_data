import json
import os 
def clean_poses(filename):
	lines = []
	with open(filename) as fh:
		for line in fh:
			
			line = line.strip()
			if line:
				line_parts = line.split(']')
				position_part = line_parts[1]
				rotation_part = line_parts[2]
				
				position_part = position_part.split('[')[1]
				position_str = "position " + position_part.replace(","," ").strip() + "\n"
				rotation_part = rotation_part.split()
				rotation_str = "rotation "
				for i in rotation_part[2:]:
					rotation_str += i+" "
				rotation_str = rotation_str.strip() + "\n"
				# print(position_str)
				# print(rotation_str)
				lines.append(position_str)
				lines.append(rotation_str)

	save_file = filename.split('.txt')[0]      
	save_file = save_file + '_cleaned.txt'
	print(save_file)
	with open(save_file,"w") as wh:
		for line in lines:
			wh.write(line)

	return save_file

def convert_2_json(filename):
	dict1 = {'position':[], 'rotation':[]}
	with open(filename) as fh:
	    l = 1
	    for line in fh:
	        description = list(line.strip().split(None, 4))
	        #print(description)
	        if l%2 != 0:
	            dict1[description[0]].append([description[1], description[2], description[3]])
	        else:
	            dict1[description[0]].append([description[1], description[2], description[3], description[4]])
	        l = l + 1

	save_json_file = filename.split('.txt')[0] 
	save_json_file = save_json_file + '.json'
	print(save_json_file)
	with open(save_json_file, "w") as out_file:
	    json.dump(dict1, out_file, indent=4, sort_keys=False)



if __name__ == '__main__':
	#This script is to be run from within the utilities folder itself
	dataset_path = "../data_collection/x-view"


	datasets = ["mp3d"]
	for dataset in datasets:
		mp_path = os.path.join(dataset_path, dataset)

		for scene in os.listdir(mp_path):
			scene_path = os.path.join(mp_path, scene)
			rooms_path = os.path.join(scene_path, "rooms")
			
			for room in os.listdir(rooms_path):
				room_path = os.path.join(rooms_path, room)
				poses_path = os.path.join(room_path, "poses.txt")
				# print(poses_path, os.path.isfile(poses_path))
				save_file = clean_poses(poses_path)
				convert_2_json(save_file)

