import os

from numpy.compat.py3k import npy_load_module
import cv2
import numpy as np

def convert_uint16_to_uint8(img):
    if img.dtype!=np.dtype('uint16'):
        raise ValueError("The given image is not dtype=uint16!")

    if img.dtype==np.dtype('uint8'):
        return img

    return np.round(np.multiply(img,255.0/2**16)).astype('uint8')

class Color():
    def __init__(self):
        pass
    
    def create_color_file(self, list_textures, DIR_OUTPUT, PRE_LABELING, direc, n_comp, n_scene, n_view, index):
        file_rgb=direc+"rgb_c"+str(n_comp)+"_s"+str(n_scene)+"_v"+str(n_view)+".png"
        file_texture=list_textures[np.random.randint(len(list_textures))]
        file_output=str(DIR_OUTPUT)+str(PRE_LABELING)+str(f'{index:06d}')+"-color.png"
        file_backdrop=direc+"backdrop_c"+str(n_comp)+"_s"+str(n_scene)+"_v"+str(n_view)+".png"
        file_depth=direc+"range_c"+str(n_comp)+"_s"+str(n_scene)+"_v"+str(n_view)+".exr"

        img_result = self.scenario_1(file_rgb, file_backdrop)
        #img_result = self.scenario_2(file_rgb, file_backdrop, file_texture, file_depth)

        return (file_output, img_result)

    def scenario_1(self, file_rgb, file_backdrop):  #This scenario makes the background transparent
        if os.path.isfile(file_rgb) and os.path.isfile(file_backdrop): 
            img_rgb=cv2.imread(file_rgb, cv2.IMREAD_UNCHANGED)
            img_rgb=convert_uint16_to_uint8(img_rgb)
            img_backdrop=cv2.imread(file_backdrop, cv2.IMREAD_UNCHANGED)
            img_backdrop=convert_uint16_to_uint8(img_backdrop)

            img_result=np.zeros((480,640,4), dtype="uint8")
            img_backdrop=np.subtract(255,img_backdrop)
            img_result[:,:,0:3]=np.where(img_backdrop[:,:]==0, img_result[:,:,0:3], img_rgb)
            img_result[:,:,3]=img_backdrop[:,:,0]

            return img_result

        return None

    def scenario_2(self, file_rgb, file_backdrop, file_texture, file_depth):    #This scenario doesn't make the background transparent and adds a random texture as background to it
        if os.path.isfile(file_rgb) and os.path.isfile(file_texture) and os.path.isfile(file_depth): 
            img_texture=cv2.imread(file_texture, cv2.IMREAD_UNCHANGED)  #is already type 'uint8'
            img_texture=cv2.resize(img_texture, (640,480))
            img_depth=cv2.imread(file_depth, cv2.IMREAD_UNCHANGED)      #is type 'float32'
            img_rgb=cv2.imread(file_rgb, cv2.IMREAD_UNCHANGED)          #is type 'uint16'
            img_rgb=convert_uint16_to_uint8(img_rgb)

            img_result=np.ones((480,640,4), dtype="uint8")*255
            img_result[:,:,0:3]=np.where(img_depth==10000000000.0, img_texture, img_rgb)

            return img_result
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

            img_depth=cv2.imread(file_depth, cv2.IMREAD_UNCHANGED)[:,:,0]       #dtype=float32
            img_backdrop=cv2.imread(file_backdrop, cv2.IMREAD_UNCHANGED)[:,:,0] #dtype=uint16

            img_depth=np.where(np.greater(img_depth,10),0.0,img_depth)    #this way also 10000000000.0 gets removed
            img_depth=np.multiply(img_depth,10000.0)

            img_depth=np.where(np.equal(img_backdrop,0),img_depth,0)

            img_depth=np.round(img_depth).astype('uint16')    #img_depth has to be dtype=uint16

            return img_depth
            
        return None

class Label():
    def __init__(self):
        pass

    def create_label_file(self, DIR_OUTPUT, PRE_LABELING, index, dict_annot, n_comp, n_scene, n_view, direc, dict_label_indices):
        file_label=DIR_OUTPUT+PRE_LABELING+str(f'{index:06d}')+"-label.png"
        img_label=self.scenario_1(index, dict_annot, n_comp, n_scene, n_view, direc, dict_label_indices)

        return (file_label,img_label)

    def scenario_1(self, index, dict_annot, n_comp, n_scene, n_view, direc, dict_label_indices):
        try:
            img_label=np.zeros((480,640),dtype="uint8")
            
            for i,obj in enumerate(dict_annot):
                mask_file="mask_c"+str(n_comp)+"_s"+str(n_scene)+"_v"+str(n_view)+obj["mask_name"]+".png"
                mask_image=cv2.imread(direc+mask_file, cv2.IMREAD_UNCHANGED)[:,:,0] #dtype=uint16
                
                label_index=dict_label_indices[obj["object_class_name"]]
                
                mask_image=np.where(mask_image != 0, label_index, mask_image).astype('uint8')
                img_label=np.maximum(img_label, mask_image)     #taking the max is correct (due to blenders output), checked it 
             
            return img_label
        except:
            return None