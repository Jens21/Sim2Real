import os
import cv2
import numpy as np

def get_max_of_image(path):
    img=cv2.imread(path, cv2.IMREAD_UNCHANGED)
    return np.max(img)

if __name__=="__main__":
    print("get_paths_to_images begin")
    BASE_PATH="/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data"
    l=[]
    dirs=os.listdir(BASE_PATH)
    np.random.shuffle(dirs)
    for i in range(len(dirs)):
        files=os.listdir(BASE_PATH+"/"+dirs[i])
        np.random.shuffle(files)
        for j in range(len(files)):
            l.append(BASE_PATH+"/"+dirs[i]+"/"+files[j])
    
    print("get_paths_to_images end")
    l=[x for x in l if "depth" in x]
    
    np.random.shuffle(l)
    
    max_value=0.0
    for i in range(1000):
        img=cv2.imread(l[i], cv2.IMREAD_UNCHANGED)
        max_value=max(max_value,np.max(img))
        print(max_value)

    print(max_value)