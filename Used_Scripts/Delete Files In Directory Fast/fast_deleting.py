import os
from concurrent.futures import ThreadPoolExecutor
import threading

BASE_PATH="/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data_syn/"

l=os.listdir(BASE_PATH)
THREAD_LIMIT=40

class Worker:
    def __init__(self, i):
        self.i = i

    def delete(self):
        os.remove(BASE_PATH+l[self.i])

with ThreadPoolExecutor(max_workers=THREAD_LIMIT) as executor:
	for i in range(len(l)):
		executor.submit(Worker(i).delete)

#Worker(0).delete()