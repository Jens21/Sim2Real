import os
from concurrent.futures import ThreadPoolExecutor
import threading
import scipy.io
from scipy.spatial.transform import Rotation as R
import pickle

BASE_PATH="/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data_syn_ori/"

l=os.listdir(BASE_PATH)
l=[x for x in l if "-meta.mat" in x]
THREAD_LIMIT=40

class Worker:
    def __init__(self, i):
        self.i = i

    def summarize(self):
        path=BASE_PATH+l[self.i]
        mat=scipy.io.loadmat(path)
        poses=mat['poses']

        translations=[]
        rotations=[]

        for index in range(len(mat['poses'][0,0])):
            pose=poses[:,:,index]

            translation=pose[0:3,3]

            #r=R.from_matrix(pose[0:3,0:3])
            #rotation_euler=r.as_euler('xyz', degrees=False)

            translations.append(translation)
            #rotations.append(rotation_euler)
        
        return (translations, rotations)

if __name__=="__main__":
    
    futures=[]

    with ThreadPoolExecutor(max_workers=THREAD_LIMIT) as executor:
        for i in range(len(l)):
            future=executor.submit(Worker(i).summarize)
            futures.append(future)

    all_translations=[]

    for future in futures:
        (translations, rotations)=future.result()

        all_translations.extend(translations)

    with open("Translations.txt", 'wb') as f:
        pickle.dump(all_translations, f)
