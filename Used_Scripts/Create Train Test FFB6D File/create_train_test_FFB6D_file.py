import os
import numpy as np

BASE_DIR="data_syn/"

TRAIN_FILE=True #create train file: True, create test file: False

if __name__=="__main__":
    if TRAIN_FILE:
        n_images=80000
        f=open("/pfs/data5/home/kit/anthropomatik/yc5412/FFB6D/ffb6d/datasets/ycb/dataset_config/train_data_list.txt","w")
    else:
        n_images=2949
        f=open("/pfs/data5/home/kit/anthropomatik/yc5412/FFB6D/ffb6d/datasets/ycb/dataset_config/test_data_list.txt","w")
        
    l=os.listdir("/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/"+BASE_DIR)
    l=[x.replace("-color.png","") for x in l if "color" in x]
    
    np.random.shuffle(l)
       
    for i in range(n_images):
        f.write(BASE_DIR+l[i])
        
        if i!=n_images-1:
            f.write("\n")
        
    f.close()
        
    
