import cv2
import os
from concurrent.futures import ThreadPoolExecutor
import scipy.io
import numpy as np
import sys

def calculate_min_max_of_image(path_mat): 
        
    mat = scipy.io.loadmat(path_mat)
      
    min_dist=100_000
    mean_dist=0
    max_dist=-100_000
      
    for i in range(len(mat["cls_indexes"])):
        loc_camera=np.array(mat["rotation_translation_matrix"][0:3,3])
    
        camera=np.array(mat["rotation_translation_matrix"])
        camera=np.vstack([camera,(0,0,0,1)])
        
        poses=np.mat(mat["poses"][:,:,i])
        poses=np.vstack([poses,(0,0,0,1)])
        
        mat_object=np.matmul(camera,poses)
        
        loc_object=np.array(mat_object[0:3,3])
        loc_object=np.array([loc_object[0,0],loc_object[1,0],loc_object[2,0]])
        
        diff=loc_camera-loc_object
    
        #min_dist=min(min_dist,np.linalg.norm(diff))
        dist=np.linalg.norm(diff)
        mean_dist+=dist
        min_dist=min(min_dist,dist)
        max_dist=max(max_dist,dist)

    mean_dist/=len(mat["cls_indexes"])

    return (min_dist, mean_dist, max_dist)

def concat(s,l):
    l2=[]
    for l_item in l:
        l2.append(s+l_item)
    
    return l2

if __name__=="__main__":
    l=[]

    
    BASE_PATH="/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data/"
    #BASE_PATH="/pfs/data5/home/kit/anthropomatik/yc5412/Test/"
    
    #l=l+concat(BASE_PATH,os.listdir(BASE_PATH))
    
    l=l+concat(BASE_PATH+"0048/",os.listdir(BASE_PATH+"0048/"))
    l=l+concat(BASE_PATH+"0049/",os.listdir(BASE_PATH+"0049/"))
    l=l+concat(BASE_PATH+"0050/",os.listdir(BASE_PATH+"0050/"))
    l=l+concat(BASE_PATH+"0051/",os.listdir(BASE_PATH+"0051/"))
    l=l+concat(BASE_PATH+"0052/",os.listdir(BASE_PATH+"0052/"))
    l=l+concat(BASE_PATH+"0053/",os.listdir(BASE_PATH+"0053/"))
    l=l+concat(BASE_PATH+"0054/",os.listdir(BASE_PATH+"0054/"))
    l=l+concat(BASE_PATH+"0055/",os.listdir(BASE_PATH+"0055/"))
    l=l+concat(BASE_PATH+"0056/",os.listdir(BASE_PATH+"0056/"))
    l=l+concat(BASE_PATH+"0057/",os.listdir(BASE_PATH+"0057/"))
    l=l+concat(BASE_PATH+"0058/",os.listdir(BASE_PATH+"0058/"))
    l=l+concat(BASE_PATH+"0059/",os.listdir(BASE_PATH+"0059/"))
   
    #l=["/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/distractor within parts/OutputTrain/"+x for x in os.listdir("/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/distractor within parts/OutputTrain")]
    
    #base_path="/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/"
    #l=[base_path+x for x in os.listdir(base_path) if x.endswith("-meta.mat")]
    
    l=[x for x in l if x.endswith("-meta.mat")]
    
    np.random.shuffle(l)
    
    futures=[]   
    min_distances=[]
    mean_distances=[]
    max_distances=[]
    
    with ThreadPoolExecutor(max_workers=40) as executor:
        for l_item in l:
            future=executor.submit(calculate_min_max_of_image, l_item)
            futures.append(future)
     
    for future in futures:
        (min_dist, mean_dist, max_dist)=future.result()
        
        min_distances.append(min_dist)
        mean_distances.append(mean_dist)
        max_distances.append(max_dist)
    
    min_distances.sort()
    mean_distances.sort()
    max_distances.sort()
        
    print("Min:")
    for i in range(10):
        index=int(float(i)*len(min_distances)/10)
        print(i,"/ 10: ",min_distances[index])
    
    print("10 / 10: ",min_distances[len(min_distances)-1])

    
    print("\nMean:")
    for i in range(10):
        index=int(float(i)*len(mean_distances)/10)
        print(i,"/ 10: ",mean_distances[index])
    
    print("10 / 10: ",mean_distances[len(mean_distances)-1])
    
    print("\nMax:")
    for i in range(10):
        index=int(float(i)*len(max_distances)/10)
        print(i,"/ 10: ",max_distances[index])
    
    print("10 / 10: ",max_distances[len(max_distances)-1])
