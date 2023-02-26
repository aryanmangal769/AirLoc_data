import os 

if __name__ == '__main__':
	"""
	runs python scripts to generate raw data
	and semantic files for each scene
	"""
	x_view_path = "/user/amangal/projects/aryan/data_collection/x-view"
	datasets = ["mp3d"]
	for dataset in datasets:
		dataset_path = os.path.join(x_view_path, dataset)

		for scene in os.listdir(dataset_path):
			scene_path = os.path.join(dataset_path, scene)

			print("python get_scene_objects.py " + dataset + " " + scene)
			os.system("python Image_extractor/get_scene_objects.py " + dataset + " " + scene)
			for room in os.listdir(os.path.join(scene_path,"rooms")):

				print("python get_raw_data.py " + dataset + " " + scene + " " + room)
				os.system("python Image_extractor/get_raw_data.py " + dataset + " " + scene + " " + room)


