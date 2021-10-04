import numpy as np
import matplotlib.pyplot as plt

FILE_TRAIN="/pfs/data5/home/kit/anthropomatik/yc5412/Ausführungen/Ausführung train syn ori 16/slurm-train.out"
TRANSPARENT=False
COLOR="orange"

keys=["loss_rgbd_seg","loss_kp_of","loss_ctr_of","loss_all","loss_target","acc_rgbd","val_loss"]

y_maxs=[0.3,3,0.2,4,4,100,3]
y_mins=[0,0,0,0,0,85,0.5]

def create_dictionary_from_lines(lines):
    d=dict()
    
    for key in keys:
        d[key]=[]
        
        for line in lines:
            if key in line:
                for i in range(len(line)):
                    if line[i:].startswith(key):
                        d[key].append(line[i:].replace(key+" ",""))

    return d

def write_eval_text_file(d):
    file_out=FILE_TRAIN[0:-4]+"_evaluations.txt"
    f_out=open(file_out,"w")
    
    length=len(d[keys[0]])
    for i in range(length):
        for key in keys:
            f_out.write(key+": "+d[key][i]+"\n")
            
        if i!=length-1:
            f_out.write("\n")
    
    f_out.close()

def create_graph_file(d,key,y_min,y_max):
    plt.clf()
    
    path_out=FILE_TRAIN[0:-4]+"_"+key+".png"
    
    length=int(len(d[key])/8)
    x=np.linspace(start=1,stop=length,num=length)

    y=[]
    values=d[key]
    for batch in range(length):
        summe=0
        
        for index in range(8):
            value=float(values[batch*8+index])
            summe+=value #TODO, uses the mean yet
        
        summe/=8
        
        y.append(float(summe))
    
    plt.xlabel(key)
    plt.ylim(y_min,y_max)
    plt.xlim(0, 64)
    plt.plot(x,y,color=COLOR)
    plt.show()
    
    if TRANSPARENT:
        plt.grid(False)
        plt.axis('off')   
        plt.savefig(path_out, transparent=True)
    else:   
        plt.grid(True)
        plt.axis('on')  
        plt.savefig(path_out, transparent=False)

if __name__=="__main__":
    f_in=open(FILE_TRAIN,"r")
    
    lines=f_in.read().split("\n")
    
    d=create_dictionary_from_lines(lines)
                
    write_eval_text_file(d)
    for i,key in enumerate(keys):
        y_max=y_maxs[i]
        y_min=y_mins[i]
        create_graph_file(d,key,y_min,y_max)
    
    f_in.close()