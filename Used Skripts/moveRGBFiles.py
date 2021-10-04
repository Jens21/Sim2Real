import os
import shutil

if __name__=="__main__":
    from_dir="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/distractor within parts on floor 80/Output/"
    to_dir="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/distractor within parts on floor 80/Output/RGB/"
    
    os.makedirs(to_dir)
    for file in os.listdir(from_dir):
        if str(file).startswith("rgb"):
            from_path=from_dir+file
            to_path=to_dir+file
            if os.path.isfile(from_path):
                shutil.copy(from_path, to_path)