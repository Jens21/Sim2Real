import os

from numpy.compat.py3k import npy_load_module
import cv2
import numpy as np

def convert_numpy_types(arr,to_type):
    if arr.dtype==np.dtype(np.uint16):
        return (arr/2**16*255.0).astype(np.dtype(to_type))
    else:
        raise ValueError("The array has the wrong dtype: "+str(arr.dtype))
        return None

class Color():
    def __init__(self):
        pass
    
    def create_color_file(self, list_textures, DIR_OUTPUT, PRE_LABELING, direc, n_comp, n_scene, n_view, index):
        file_rgb=direc+"rgb_c"+str(n_comp)+"_s"+str(n_scene)+"_v"+str(n_view)+".png"
        #file_texture=list_textures[np.random.randint(len(list_textures))]
        file_output=str(DIR_OUTPUT)+str(PRE_LABELING)+str(f'{index:06d}')+"-color.png"
        file_backdrop=direc+"backdrop_c"+str(n_comp)+"_s"+str(n_scene)+"_v"+str(n_view)+".png"

        img_result = self.scenario_1(file_rgb, file_backdrop)
        return (file_output, img_result)

    def scenario_1(self, file_rgb, file_backdrop):  #This scenario makes the background transparent
        if os.path.isfile(file_rgb) and os.path.isfile(file_backdrop): 
            img_rgb=convert_numpy_types(cv2.imread(file_rgb, cv2.IMREAD_UNCHANGED),np.uint8)
            img_backdrop=convert_numpy_types(cv2.imread(file_backdrop, cv2.IMREAD_UNCHANGED)[:,:,0],np.uint8)

            img_backdrop=255-img_backdrop
            img_rgb=cv2.cvtColor(img_rgb, cv2.COLOR_RGB2RGBA)

            img_rgb[:,:,3]=img_backdrop
            img_rgb[:,:,0]=np.where(img_backdrop==0,img_backdrop,img_rgb[:,:,0])
            img_rgb[:,:,1]=np.where(img_backdrop==0,img_backdrop,img_rgb[:,:,1])
            img_rgb[:,:,2]=np.where(img_backdrop==0,img_backdrop,img_rgb[:,:,2])

            return img_rgb

        return None

class Depth():
    def __init__(self):
        pass

    def create_depth_file(self, list_textures, DIR_OUTPUT, PRE_LABELING, direc, n_comp, n_scene, n_view, index):
        file_depth=direc+"range_c"+str(n_comp)+"_s"+str(n_scene)+"_v"+str(n_view)+".exr"
        #file_texture=list_textures[np.random.randint(len(list_textures))]
        file_backdrop=direc+"backdrop_c"+str(n_comp)+"_s"+str(n_scene)+"_v"+str(n_view)+".png"
        file_result=str(DIR_OUTPUT)+str(PRE_LABELING)+str(f'{index:06d}')+"-depth.png"

        return (file_result, self.scenario_1(file_depth, file_backdrop))

    def scenario_1(self,file_depth, file_backdrop):  #This scenario makes the background transparent
        if os.path.isfile(file_depth) and os.path.isfile(file_backdrop):
            img_depth=cv2.imread(file_depth, cv2.IMREAD_UNCHANGED)[:,:,0]
            img_backdrop=cv2.imread(file_backdrop, cv2.IMREAD_UNCHANGED)[:,:,0]

            img_depth=np.where(img_depth>10,0,img_depth)
            img_depth=img_depth*10000.0
            img_depth=img_depth.astype('uint16')

            img_backdrop=65535-img_backdrop
            img_depth=np.where(img_backdrop==0,0,img_depth)

            return img_depth

        return None