import shutil
import os
import numpy as np

DIR_IMAGES_FROM="/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data_syn/"
DIR_TRAINING_FILES_FROM="/pfs/data5/home/kit/anthropomatik/yc5412/FFB6D/ffb6d/"
DIR_TO="/pfs/data5/home/kit/anthropomatik/yc5412/Ausführungen/Ausführung train syn ori 60/"

def save_a_few_images():
    path=DIR_TO+"Example Images/"
    os.mkdir(path)

    l=[x.replace("-color.png","") for x in os.listdir(DIR_IMAGES_FROM) if "color" in x]
    np.random.shuffle(l)

    for i in range(100):
        shutil.copy(DIR_IMAGES_FROM+l[i]+"-color.png",path+l[i]+"-color.png")
        shutil.copy(DIR_IMAGES_FROM+l[i]+"-depth.png",path+l[i]+"-depth.png")
        shutil.copy(DIR_IMAGES_FROM+l[i]+"-label.png",path+l[i]+"-label.png")
        shutil.copy(DIR_IMAGES_FROM+l[i]+"-meta.mat",path+l[i]+"-meta.mat")

def save_training_files():
    l=[x for x in os.listdir(DIR_TRAINING_FILES_FROM) if "slurm" in x]
    for x in l:
        shutil.move(DIR_TRAINING_FILES_FROM+x,DIR_TO+x)
    
    path=DIR_TRAINING_FILES_FROM+"train_log/ycb/"
    l=[x for x in os.listdir(path)]
    for x in l:
        shutil.move(path+x,DIR_TO+x)

if __name__=="__main__":
    save_a_few_images()
    save_training_files()
