import scipy.io
import numpy as np
import os
from concurrent.futures import ThreadPoolExecutor
from scipy.spatial.transform import Rotation as R

def calculate_angle_between_middle_point_and_camera(path):    
    def get_middle_point(poses):
        middle_loc=np.zeros(3)

        for i in range(len(mat['cls_indexes'])):
            pose=poses[:,:,i]
            pose=np.array([pose[0],pose[1],pose[2],[0,0,0,1]])
            pose=np.matmul(cam,pose)
            middle_loc+=pose[0:3,3]
            
        middle_loc/=len(mat['cls_indexes'])   
        return middle_loc

    mat = scipy.io.loadmat(path)
    cam=mat['rotation_translation_matrix']
    cam=np.array([cam[0],cam[1],cam[2],[0,0,0,1]])
    poses=mat['poses']

    middle_point=get_middle_point(poses)
    #print("Middle Point:",middle_point)
    camera_loc=cam[0:4,3]
    
    n=1
    matrix=None
    delta=100.000
    for i in range(len(mat['cls_indexes'])):
        pose=poses[:,:,i]
        pose=np.array([pose[0],pose[1],pose[2],[0,0,0,1]])
        pose=np.matmul(cam,pose)
        inverse=np.linalg.inv(pose)
        transformed_poses=[]

        num=1
        delt=0
        for j in range(len(mat['cls_indexes'])):
            p=poses[:,:,j]
            p=np.array([p[0],p[1],p[2],[0,0,0,1]])
            p=np.matmul(cam,p)
            transformed_pose=np.matmul(inverse, p)

            if i!=j:
                transformed_pose=transformed_pose[0:3,0:3]
                r = R.from_matrix(transformed_pose)

                euler=r.as_euler('xyz', degrees=True)
                if euler[0]<0:
                    euler[0]+=180
                if euler[1]<0:
                    euler[1]+=180

                if np.abs(180-euler[0])<euler[0]:
                        euler[0]=180-euler[0]
                if np.abs(180-euler[1])<euler[1]:
                        euler[1]=180-euler[1]

                if np.abs(euler[0])+np.abs(euler[1])<15:
                    delt+=np.abs(euler[0])+np.abs(euler[1])
                    num+=1

        if num>n or num==n and delt<delta:
            delta=delt
            n=num
            matrix=inverse
    
    if n==1:
        return None

    middle_point=np.array(middle_point.tolist()+[1])
    middle_point=np.matmul(matrix, middle_point)[0:3]
    camera_loc=np.matmul(matrix, camera_loc)[0:3]

    a=camera_loc-middle_point
    b=np.array(camera_loc[0:2].tolist()+[middle_point[2]])-middle_point

    angle=np.arccos(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)))
    angle=angle*180/np.pi

    return (angle,path)

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
    """
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
    #l=["/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/distractor within parts/OutputTrain/"+x for x in os.listdir("/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/distractor within parts/OutputTrain")]
    
    #base_path="/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/"
    #l=[base_path+x for x in os.listdir(base_path) if "-meta" in x]    
    
    #l=[x for x in l if x.endswith("-meta.mat")]
    
    l=["/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data/0059/000001-meta.mat"]

    np.random.shuffle(l)
    
    futures=[]   
    
    with ThreadPoolExecutor(max_workers=40) as executor:
        for l_item in l:
            future=executor.submit(calculate_angle_between_middle_point_and_camera, l_item)
            futures.append(future)
    #for l_item in l:
    #    calculate_angle_between_middle_point_and_camera(l_item)
     
    angles=[]
    mean=0
    le=0
    for future in futures:
        res=future.result()
        if res!=None:
            (angle,path)=res
            angles.append(angle)
            mean+=angle
            le+=1
    
    mean/=le
    angles.sort()
    
    print("Mean: ",mean)
    
    length=len(angles)
    for i in range(10):
        index=int(float(i)*length/10)
        print(i,"- 10: ",angles[index])
       
    print("10 - 10: ",angles[len(angles)-1])  
        
