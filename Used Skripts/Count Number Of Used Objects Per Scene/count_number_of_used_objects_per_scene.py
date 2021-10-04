import os
from concurrent.futures import ThreadPoolExecutor
import threading
import scipy.io
import numpy as np

THREAD_LIMIT=40

def get_all_base_paths():
    paths=[]
    
    for i in range(92):
        if i>=48 and i<=59:
            continue
            
        paths.append("/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data/"+str(i).zfill(4)+"/")
    """   
    
    for i in range(92):
        if i<48 or i>59:
            continue
            
        paths.append("/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data/"+str(i).zfill(4)+"/")
    """
    return paths

#BASE_PATHS=get_all_base_paths()
#BASE_PATHS=["/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data_syn/"]
#BASE_PATHS=["/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data_syn_ori/"]
#BASE_PATHS=["/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data/DatasetTest/"]
#BASE_PATHS=get_all_base_paths()
#print(BASE_PATHS)

def get_all_files():
    files=[]
    for base_path in BASE_PATHS:
        for x in os.listdir(base_path):
            files.append(base_path+x)
    
    return files

f=open("/pfs/data5/home/kit/anthropomatik/yc5412/FFB6D/ffb6d/datasets/ycb/dataset_config/train_data_list_ori.txt","r")
l=f.read()
l=l.split("\n")
l=["/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/"+x+"-meta.mat" for x in l if not "data_syn/" in x]
#l=["/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/"+x.replace("data_syn","data_syn_ori")+"-meta.mat" for x in l if not "data/" in x]
#l=["/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/"+x+"-meta.mat" for x in l]

#l=get_all_files()
#l=[x for x in l if ".mat" in x]
#np.random.shuffle(l)

class Worker:
    def __init__(self, i):
        self.i = i

    def get_n_cls_indexes(self):
        path=l[self.i]
        mat=scipy.io.loadmat(path)
        return len(mat['cls_indexes'])

if __name__=="__main__":
    futures=[]
    with ThreadPoolExecutor(max_workers=40) as executor:
        for i in range(len(l)):
            future=executor.submit(Worker(i).get_n_cls_indexes)
            futures.append(future)

    d=dict()
    for future in futures:
        try:
            n_indexes=future.result()
            
            if not n_indexes in d:
                d[n_indexes]=0
                
            d[n_indexes]+=1
            
        except OSError: 
            print("Exception: ",path)
            
    for key in d.keys():
        print("Scenes with",key,"objects:",d[key])
        