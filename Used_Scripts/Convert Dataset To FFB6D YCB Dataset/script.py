import shutil
import os
import numpy as np

DATASET_FROM_DIR="/pfs/data5/home/kit/anthropomatik/yc5412/Sim2Real/Convert_Amira_2_YCB/OutputTrain/"
DATASET_TO_DIR="/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data_syn/"

PREFIX="data_syn/"

N_SYNTHETIC_SAMPlES=int(round(80_000+16189*0.9))
N_REAL_SAMPlES=int(round(16189*0.1))

FILE_ORI_TRAIN_DATA="/pfs/data5/home/kit/anthropomatik/yc5412/FFB6D/ffb6d/datasets/ycb/dataset_config/train_data_list_ori.txt"
FILE_TRAIN_DATA="/pfs/data5/home/kit/anthropomatik/yc5412/FFB6D/ffb6d/datasets/ycb/dataset_config/train_data_list.txt"

if __name__=="__main__":
    shutil.move(DATASET_FROM_DIR, DATASET_TO_DIR)

    l=[x.replace("-color.png","") for x in os.listdir(DATASET_TO_DIR) if "-color.png" in x]
    l=[PREFIX+x for x in l]
    np.random.shuffle(l)

    f=open(FILE_ORI_TRAIN_DATA, "r")
    content=[x for x in f.read().split("\n") if "data/" in x]
    np.random.shuffle(content)
    f.close()

    f=open(FILE_TRAIN_DATA, "w")
    for i in range(min(N_REAL_SAMPlES, len(content))):
        f.write(content[i]+"\n")

    for i in range(min(N_SYNTHETIC_SAMPlES, len(l))):
        f.write(l[i]+"\n")
    f.close()