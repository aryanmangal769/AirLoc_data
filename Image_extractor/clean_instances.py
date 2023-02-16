import os 

def clean(filename):
    save_file = filename.split('.txt')[0]      
    save_file = save_file + '_cleaned.txt'
    cleaned_file=open(save_file,"w")
    with open(filename) as fh:
        for line in fh:
            l=line.split('_',2)
            if(l[-1].split(" ")[1]!=""):
                cleaned_file.write(l[-1])
    cleaned_file.close()

if __name__ == '__main__':
    #This script is to be run from within the utilities folder itself
    dataset_path = "../data_collection/x-view"


    datasets = ["mp3d"]
    for dataset in datasets:
        mp_path = os.path.join(dataset_path, dataset)

        for scene in os.listdir(mp_path):
            scene_path = os.path.join(mp_path, scene)
            instance_path=os.path.join(scene_path,"classes.txt")
            clean(instance_path) 
