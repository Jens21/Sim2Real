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
l=["/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/"+x.replace("data_syn","data_syn_ori")+"-meta.mat" for x in l if not "data/" in x]
#l=["/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/"+x+"-meta.mat" for x in l]

#l=get_all_files()
#l=[x for x in l if ".mat" in x]
#np.random.shuffle(l)

class Worker:
    def __init__(self, i):
        self.i = i

    def get_cls_indexes(self):
        path=l[self.i]
        mat=scipy.io.loadmat(path)
        return mat['cls_indexes']

def index_to_object_name(i):
    l=["master_chef_can","cracker_box","sugar_box","tomato_soup_can","mustard_bottle","tuna_fish_can","pudding_box","gelatin_box","potted_meat_can","banana","pitcher_base","bleach_cleanser","bowl","mug","power_drill","wood_block","scissors","large_marker","large_clamp","extra_large_clamp","foam_brick"]
        
    return l[int(i)]

if __name__=="__main__":
    futures=[]
    with ThreadPoolExecutor(max_workers=40) as executor:
        for i in range(len(l)):
            future=executor.submit(Worker(i).get_cls_indexes)
            futures.append((l[i],future))

    d=dict()
    ins=0
    for (path,future) in futures:
        try:
            indexes=future.result()
            indexes=indexes[:,0]
            
            for index in indexes:
                if not index in d:
                    d[index]=0
                    
                d[index]+=1
                ins+=1
        except OSError: 
            print("Exception: ",path)
            
    print("All original real training data examples:")
    for key in d.keys():
        object_name=index_to_object_name(key-1)
        print(object_name,":",d[key],",",float(d[key])/float(ins)*100,"%")
        
    print("Number of files:",len(l))