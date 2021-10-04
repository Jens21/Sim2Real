import os
import scipy.io
import numpy as np
import shutil
from concurrent.futures import ThreadPoolExecutor
import threading

THREAD_LIMIT=80

DIR_FROM="/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data_syn_ori/"
DIR_TO="/pfs/data5/home/kit/anthropomatik/yc5412/Test/"

l=os.listdir(DIR_FROM)
l=[x for x in l if "mat" in x]
np.random.shuffle(l)
        
class Worker:
    def __init__(self, i):
        self.i = i

    def func(self):
        x=l[self.i]
        mat=scipy.io.loadmat(DIR_FROM+x)
        indices=mat['cls_indexes'][0]
        
        if 17 in indices and 16 in indices and 11 in indices and 4 in indices:
            index_scissors=0
            for index,a in enumerate(indices):
                if a==17:
                    index_scissors=index
                    break
                    
            center_scissors=mat['center'][index_scissors]
            if center_scissors[1]>200 and center_scissors[1]<300 and center_scissors[0]<350 and center_scissors[0]>250:
                file=x.replace("-meta.mat","-color.png")
                shutil.copy(DIR_FROM+file,DIR_TO+file)
     
with ThreadPoolExecutor(max_workers=THREAD_LIMIT) as executor:
	for i in range(len(l)):
		executor.submit(Worker(i).func)

#for i in range(len(l)):
#    Worker(i).func()