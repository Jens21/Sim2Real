import cv2
import numpy as np
import os

BASE_DIR="/pfs/data5/home/kit/anthropomatik/yc5412/Sim2Real/Used Skripts/Compare Images/"

FILE_COMP_1="New000000-depth.png"
FILE_COMP_2="Ref000000-depth.png"

#FILE_COMP_1="New000000-depth.png"
#FILE_COMP_2="Ref000000-depth.png"

#FILE_COMP_1="New000000-label.png"
#FILE_COMP_2="Ref000000-label.png"

def create_difference_images(img_comp_1, img_comp_2): 
    print("Shape img 1:",img_comp_1.shape)
    print("Shape img 2:",img_comp_2.shape)
    print()

    if img_comp_1.shape!=img_comp_2.shape:
        raise ValueError("Different shapes!")

    shape=img_comp_1.shape
    
    img_comp_1=img_comp_1.flatten()
    img_comp_2=img_comp_2.flatten()
    
    print("Type img 1:",type(img_comp_1[0]))
    print("Type img 2:",type(img_comp_2[0]))
        
    img_absolute=np.abs(img_comp_1.astype('float')-img_comp_2.astype('float'))
    max_value=np.max(img_absolute)
    img_absolute=img_absolute.reshape(shape)
    
    if len(img_absolute.shape)==2:
        img_absolute=np.expand_dims(img_absolute,2)
    
    if max_value>255:
        img_absolute=np.multiply(img_absolute,255/max_value)
        img_relative=img_absolute
    else:
        img_relative=np.multiply(np.copy(img_absolute),255/max_value)
        
    img_out=np.append(img_absolute,img_relative,axis=2)
    
    return img_out.astype('uint8')

def save_images(imgs, path, ending):
    shape=imgs.shape
    
    for channel in range(shape[-1]):
        cv2.imwrite(path+ending+"["+str(channel)+"].png",imgs[:,:,channel])

if __name__=="__main__":
    if not os.path.isfile(BASE_DIR+FILE_COMP_1) or not os.path.isfile(BASE_DIR+FILE_COMP_2):
        raise ValueError("The given files does not exist!")

    img_comp_1=cv2.imread(BASE_DIR+FILE_COMP_1,cv2.IMREAD_UNCHANGED)
    img_comp_2=cv2.imread(BASE_DIR+FILE_COMP_2,cv2.IMREAD_UNCHANGED)
    imgs_out=None
    ending=None
    
    if img_comp_1 is None or img_comp_2 is None:
        raise ValueError("The images could not be loaded!")
    
    if FILE_COMP_1.endswith("-color.png") and FILE_COMP_2.endswith("-color.png"):
        ending="compare-"+FILE_COMP_1.replace("-color.png","")+"-"+FILE_COMP_2.replace("-color.png","")+"-color"
    elif FILE_COMP_1.endswith("-depth.png") and FILE_COMP_2.endswith("-depth.png"):
        ending="compare-"+FILE_COMP_1.replace("-depth.png","")+"-"+FILE_COMP_2.replace("-depth.png","")+"-depth"
    elif FILE_COMP_1.endswith("-label.png") and FILE_COMP_2.endswith("-label.png"):
        ending="compare-"+FILE_COMP_1.replace("-label.png","")+"-"+FILE_COMP_2.replace("-label.png","")+"-label"
    else:
        raise ValueError("The given files are not comparable!")
            
    imgs_out=create_difference_images(img_comp_1, img_comp_2)
            
    if not imgs_out is None:
        save_images(imgs_out, BASE_DIR, ending)