This repo is to generate Reloc110 dataset from scratch. We manually collected poses from 15 scenes present in Matterport3D dataset. To increase the size of dataset, we randomly sampled 100 poses around each manually collected pose using habitat-sim. Finally images are generated corresponding to every pose.

# Dataset Generation


## Installing Habitat-sim nightly Version:

```
conda create -n habitat1 python=3.7 cmake=3.14.0
conda activate habitat1
```

- Make a bash file :

```jsx
conda install habitat-sim headless -c conda-forge -c aihabitat-nightly
conda install -c fastai opencv-python-headless
pip install pypng
conda install -c open3d-admin -c conda-forge open3d
conda install -c conda-forge scikit-learn==0.24.2
conda install -c conda-forge tqdm
```

- Run the bash file. Enter y(Yes) wherever asked

## Dataset 

- Clone the repo
```
git clone -- this repo
cd AirLoc_data
```

- Run the file get_dataset.sh to generate the appropriate directory structure for you and download the initial data in them containing manually collected poses.

```
./get_dataset.sh 
```
- Run utils/clean_poses.py (Script to generate clean poses form of initial poses)

```
python Image_extractor/clean_poses.py
```
- Run utils/random_pose_generator.py (To generate random poses)

```
python Image_extractor/random_pose_generatator.py
```

- Run utils/driver_sim.py (To generate the images corresponding to poses )

```
python Image_extractor/driver_sim.py
```
