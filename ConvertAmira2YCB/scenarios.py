import os

from numpy.compat.py3k import npy_load_module
import cv2
import numpy as np

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
            img_rgb=cv2.imread(file_rgb, cv2.IMREAD_UNCHANGED)
            img_backdrop=cv2.imread(file_backdrop, cv2.IMREAD_UNCHANGED)

            img_result=np.zeros((480,640,4), dtype="uint8")
            img_backdrop=np.subtract(255,img_backdrop)
            img_result[:,:,0:3]=np.where(img_backdrop[:,:]==0, img_result[:,:,0:3], np.multiply(img_rgb,255.0/2**16))
            img_result[:,:,3]=img_backdrop[:,:,0]

            """
            for y in range(480):
                for x in range(640):
                    back=255-img_backdrop[y,x,0]

                    if back!=0:
                        img_result[y,x,0]=img_rgb[y,x,0]/2**16*255.0
                        img_result[y,x,1]=img_rgb[y,x,1]/2**16*255.0
                        img_result[y,x,2]=img_rgb[y,x,2]/2**16*255.0
                        img_result[y,x,3]=back

            
            img_backdrop=np.subtract(255,img_backdrop)
            img_rgb=cv2.cvtColor(img_rgb, cv2.COLOR_RGB2RGBA)

            img_rgb[:,:,3]=img_backdrop
            img_rgb[:,:,0]=np.where(np.equal(img_backdrop,0),img_backdrop,img_rgb[:,:,0])
            img_rgb[:,:,1]=np.where(np.equal(img_backdrop,0),img_backdrop,img_rgb[:,:,1])
            img_rgb[:,:,2]=np.where(np.equal(img_backdrop,0),img_backdrop,img_rgb[:,:,2])
            """
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
            img_depth=cv2.imread(file_depth, cv2.IMREAD_UNCHANGED)[:,:,0]
            img_backdrop=cv2.imread(file_backdrop, cv2.IMREAD_UNCHANGED)[:,:,0]

            img_depth=np.where(np.greater(img_depth,10),0,img_depth)
            img_depth=np.multiply(img_depth,10000.0)

            img_result=np.zeros((480,640),dtype="uint16")
            img_backdrop=np.subtract(65535,img_backdrop)

            img_result=np.where(np.equal(img_backdrop,0),img_result,img_depth)

            return img_result

            """
            img_depth=cv2.imread(file_depth, cv2.IMREAD_UNCHANGED)[:,:,0]
            img_backdrop=cv2.imread(file_backdrop, cv2.IMREAD_UNCHANGED)[:,:,0]

            img_depth=np.where(np.greater(img_depth,10),0,img_depth)
            img_depth=np.multiply(img_depth,10000.0)
            img_depth=img_depth.astype('uint16')

            #img_backdrop=65535-img_backdrop
            img_backdrop=np.subtract(65535,img_backdrop)
            img_depth=np.where(np.equal(img_backdrop,0),0,img_depth)

            return img_depth
            """
        return None