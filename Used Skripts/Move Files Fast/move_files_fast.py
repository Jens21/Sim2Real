import os
from concurrent.futures import ThreadPoolExecutor
import threading
import shutil

FROM_DIR="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/distractor within parts/OutputTrain3/"
TO_DIR="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/distractor within parts/OutputTrain/"

l=os.listdir(FROM_DIR)
THREAD_LIMIT=40

class Worker:
    def __init__(self, i):
        self.i = i

    def move(self):
        shutil.move(FROM_DIR+l[self.i],TO_DIR+l[self.i])

with ThreadPoolExecutor(max_workers=THREAD_LIMIT) as executor:
	for i in range(len(l)):
		executor.submit(Worker(i).move)

#Worker(0).move()