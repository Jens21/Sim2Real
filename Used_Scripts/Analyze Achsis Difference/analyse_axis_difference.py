import os
from concurrent.futures import ThreadPoolExecutor
import threading
import scipy.io
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d
import pickle

THREAD_LIMIT=40  #TODO 40

class Worker:
    def __init__(self, i):
        self.i = i

    def analyse(self):
        path_file=l[self.i]
        mat=scipy.io.loadmat(path_file)
        poses=mat['poses']

        translations=[]
        for i in range(max(len(mat["cls_indexes"]),len(mat["cls_indexes"][0]))):        #for own synthetic data samples
            pose=poses[:,:,i]
            translation=pose[0:3,3]
            translations.append(translation)
        
        return translations

def get_own_samples():
    BASE_DIR="/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data_syn/"

    l=os.listdir(BASE_DIR)
    l=[BASE_DIR+x for x in l if "-meta.mat" in x]

    return l

def get_synthetic_samples():
    with open("/pfs/data5/home/kit/anthropomatik/yc5412/FFB6D/ffb6d/datasets/ycb/dataset_config/train_data_list_ori.txt","r") as f:
        l=f.read().split("\n")  #example line: data/0048/000001
        l=[x for x in l if "data_syn/" in x]
        l=[x.replace("data_syn","data_syn_ori") for x in l]
        l=["/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/"+x+"-meta.mat" for x in l]

        return l

def get_test_samples():
    with open("/pfs/data5/home/kit/anthropomatik/yc5412/FFB6D/ffb6d/datasets/ycb/dataset_config/test_data_list_ori.txt","r") as f:
        l=f.read().split("\n")  #example line: data/0048/000001
        l=["/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/"+x+"-meta.mat" for x in l]

        return l

def get_train_samples():
    with open("/pfs/data5/home/kit/anthropomatik/yc5412/FFB6D/ffb6d/datasets/ycb/dataset_config/train_data_list_ori.txt","r") as f:
        l=f.read().split("\n")  #example line: data/0048/000001
        l=[x for x in l if "data/" in x]
        l=["/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/"+x+"-meta.mat" for x in l]

        return l

if __name__=="__main__":
    
    #l=get_synthetic_samples()
    #l=get_test_samples()
    #l=get_train_samples()
    l=get_own_samples()

    futures=[]
    
    with ThreadPoolExecutor(max_workers=THREAD_LIMIT) as executor:
        for i in range(len(l)):
            future=executor.submit(Worker(i).analyse)
            futures.append(future)

    positions=[]

    for future in futures:   
        for position in future.result():
            positions.append(position)

    with open('positions.txt','wb') as fp:
        pickle.dump(positions, fp)

