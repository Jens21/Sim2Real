import os
import shutil
import numpy as np

DIR_IN="/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data/"
DIR_OUT="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/Test/"

for i in range(48,60):
    path_in=DIR_IN+"{:04d}".format(i)+"/"
    l=os.listdir(path_in)
    lmat=[x for x in l if "mat" in x]
    np.random.shuffle(lmat)
    lout=[x for x in l if lmat[0].replace("-meta.mat","") in x]
    
    path_out=DIR_OUT+"ReferenceReal"+str(i)+"/"
    os.mkdir(path_out)
    for x in lout:
        shutil.copy(path_in+x,path_out+x)