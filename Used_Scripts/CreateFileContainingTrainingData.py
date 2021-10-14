import os

if __name__=="__main__":
    FILE_OUT="/pfs/data5/home/kit/anthropomatik/yc5412/FFB6D/ffb6d/datasets/ycb/dataset_config/train_data_list.txt"
    DIR_DATASET="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/ConvertAmira2YCB/Dataset/"
    
    if os.path.isfile(FILE_OUT):
        os.remove(FILE_OUT)
    
    file=open(FILE_OUT,"w")
    
    for l in os.listdir(DIR_DATASET):
        if str(l).endswith("-label.png"):
            path=(DIR_DATASET+l).replace("-label.png","")
            file.write(path+"\n")
        
    file.close()