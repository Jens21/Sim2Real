import scipy.io
import numpy as np
import os
from concurrent.futures import ThreadPoolExecutor

def calculate_angle_between_middle_point_and_camera(path):    
    mat = scipy.io.loadmat(path)
    cam=mat['rotation_translation_matrix']
    cam=np.array([cam[0],cam[1],cam[2],[0,0,0,1]])
    poses=mat['poses']

    middle_loc=np.zeros(3)
    for i in range(len(mat['cls_indexes'])):
        pose=poses[:,:,i]
        pose=np.array([pose[0],pose[1],pose[2],[0,0,0,1]])
        pose=np.matmul(cam,pose)
        middle_loc+=pose[0:3,3]
        
    middle_loc/=len(mat['cls_indexes'])    
    camera_loc=cam[0:3,3]
    
    angle=np.arccos(np.dot(camera_loc,middle_loc)/(np.linalg.norm(camera_loc)*np.linalg.norm(middle_loc)))
    angle=angle*180/np.pi
    
    if angle>180:
        print("Angle: ",angle)
    
        angle=360-angle
    
    return (angle,path)

def concat(s,l):
    l2=[]
    for l_item in l:
        l2.append(s+l_item)
    
    return l2

if __name__=="__main__":
    l=[]
    
    """
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
    """
    
    l=["/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/distractor within parts/OutputTrain/"+x for x in os.listdir("/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/distractor within parts/OutputTrain")]
    
    
    l=[x for x in l if x.endswith("-meta.mat")]
    
    np.random.shuffle(l)
    
    futures=[]   
    
    with ThreadPoolExecutor(max_workers=40) as executor:
        for l_item in l:
            future=executor.submit(calculate_angle_between_middle_point_and_camera, l_item)
            futures.append(future)
     
    angles=[]
    mean=0
    for future in futures:
        (angle,path)=future.result()
        angles.append(angle)
        mean+=angle
    
    mean/=len(l)
    angles.sort()
    
    print("Mean: ",mean)
    
    length=len(angles)
    for i in range(10):
        index=int(float(i)*length/10)
        print(i,"- 10: ",angles[index])
       
    print("10 - 10: ",angles[len(angles)-1])  
        