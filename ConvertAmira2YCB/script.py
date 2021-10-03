import os
import json
import numpy as np
import scipy.io
from PIL import Image
import concurrent.futures
import cv2
from scipy.spatial.transform import Rotation as R
from datetime import datetime
import argparse
import sys
import torchvision.transforms as transforms
import scenarios

parser = argparse.ArgumentParser()
parser.add_argument('--PRE_LABELING', type=str,default="", help='Pre labeling of the images.')
parser.add_argument('--NUMBER_OF_IMAGES', type=int,default=10000, help='Number of images to process')
parser.add_argument('--START_AT_IMAGE_NUMBER', type=int,default=0, help='Labeling images starting at number')
parser.add_argument('--THREAD_LIMIT', type=int,default=1, help='Number of threads to use')
parser.add_argument('--DIR_INPUT', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/ConvertAmira2YCB/TestInput/", help='where to take the files from')
parser.add_argument('--DIR_OUTPUT', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/ConvertAmira2YCB/Dataset/", help='where to save the files')
parser.add_argument('--DIR_BACKGROUND_TEXTURES', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/textures/", help='where to take the background textures from')

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"
args=parser.parse_args(argv)

list_annot=[]
list_textures=[]
dict_label_indices=dict()

class Worker():
    def __init__(self,i,direc,file):
        self.i=i
        self.direc=direc
        self.file=file
        
        self.rng=np.random
     
    def process_data(self):
        def get_composition_index(file):
            comp=str(file).split("_")[1]
            comp=comp.replace("c","")
            return int(comp)
        def get_scene_index(file):
            scene=str(file).split("_")[2]
            scene=scene.replace("s","")
            return int(scene)
        def get_view_index(file):
            view=str(file).split("_")[3]
            view=view.replace("v","")
            view=view.replace(".json","")
            return int(view)
        def load_dict(file):
            f=open(file, "r")
            return json.load(f)
      

        n_comp=get_composition_index(self.file)
        n_scene=get_scene_index(self.file)
        n_view=get_view_index(self.file)
            
        dict_annot=load_dict(self.direc+self.file)
        dict_annot=self.remove_invalid_objs(dict_annot)
        
        img_label=self.create_label_file(dict_annot,self.direc,n_comp,n_scene,n_view,self.i)
        meta_file=self.create_meta_file(dict_annot,self.direc,n_comp,n_scene,n_view,self.i)
        img_color=scenarios.Color().create_color_file(list_textures, args.DIR_OUTPUT, args.PRE_LABELING, direc, n_comp, n_scene, n_view, self.i)
        img_depth=scenarios.Depth().create_depth_file(list_textures, args.DIR_OUTPUT, args.PRE_LABELING, direc,n_comp,n_scene,n_view,self.i)
        #img_color=self.create_color_file(self.direc,n_comp,n_scene,n_view,self.i)
        #img_depth=self.create_depth_file(self.direc,n_comp,n_scene,n_view,self.i)
     
        try:
            if img_color!=None and img_depth!=None and img_label!=None and meta_file!=None:
                
                cv2.imwrite(img_label[0], img_label[1])
                scipy.io.savemat(meta_file[0], mdict=meta_file[1])
                cv2.imwrite(img_color[0], img_color[1])
                cv2.imwrite(img_depth[0], img_depth[1])
        except:
            print("Except: "+str(self.i)+"\t"+str(self.file),file=sys.stderr, flush=True)

    def remove_invalid_objs(self,dict_annot): 
        #more than 95 % of vertices are not visible
        return [x for x in dict_annot if float(x["n_pix_not_visible"][0]+x["n_pix_occluded"][0]-x["n_pix_not_visible_and_occluded"][0])/float(x["n_pix"][0])<=0.95]
       
    def create_meta_file(self,dict_annot,direc,n_comp, n_scene,n_view,index):
        def pose_and_translation_in_matrix(pose, translation):
            result=np.zeros((4,4), dtype="float64")
        
            result[0:3,0:3]=R.from_quat([pose[1],pose[2],pose[3],pose[0]]).as_matrix()        
            result[0:3,3]=np.asarray(translation)/1000  #to convert mm to m
            
            result[3,3]=1
            
            return result
        def get_object_pose_matrix(obj_pose, obj_translation):
            obj_matrix=pose_and_translation_in_matrix(obj_pose,obj_translation)                        
            mirror=np.asarray([[1,0,0,0],[0,-1,0,0],[0,0,-1,0],[0,0,0,1]])  #mirror z and y
                  
            obj_matrix=np.matmul(mirror,obj_matrix)
            
            return obj_matrix[0:3,:].tolist()
        def get_camera_matrix(camera_pose, camera_translation):
            camera_matrix=pose_and_translation_in_matrix(camera_pose,camera_translation)
                                    
            mirror=np.asarray([[1,0,0,0],[0,-1,0,0],[0,0,-1,0],[0,0,0,1]])  #mirror z and y
                    
            camera_matrix=np.matmul(camera_matrix,mirror)
                    
            return camera_matrix[0:3,:].tolist()


        try:
            cls_indexes=np.zeros((len(dict_annot),1), dtype="uint8")
            for i in range(len(dict_annot)):
                cls_indexes[i]=float(dict_label_indices[dict_annot[i]["object_class_name"]])
                
            intrinsic=np.zeros((3,3), dtype = "float64")
            intrinsic[0,0]=1066.77800000000
            intrinsic[1,1]=1067.48700000000
            intrinsic[0,2]=312.986900000000
            intrinsic[1,2]=241.310900000000
            intrinsic[2,2]=1

            center=np.zeros((len(dict_annot),2),dtype="float64")
            poses=np.zeros((3,4,len(dict_annot)), dtype = "float64")
            #vertmap=np.zeros((480,640,3),dtype="float32")

            camera_pose=dict_annot[0]["camera_pose"]["q"]
            camera_translation=dict_annot[0]["camera_pose"]["t"]
            camera_matrix=get_camera_matrix(camera_pose, camera_translation)
            
            for i,obj in enumerate(dict_annot):
                obj_pose=obj["pose"]["q"]
                obj_translation=obj["pose"]["t"]
                poses[:,:,i]=get_object_pose_matrix(obj_pose, obj_translation)
                
                center[i,0]=obj["center"][0]
                center[i,1]=480-obj["center"][1]
            
            #vertmap, not used by FFB6D, therefor not created

            dictionary=dict()
            dictionary['cls_indexes']=cls_indexes
            dictionary['factor_depth']=np.array([10000]).astype('uint16')[0]
            dictionary['intrinsic_matrix']=intrinsic
            dictionary['rotation_translation_matrix']=camera_matrix
            dictionary['poses']=poses
            #dictionary['vertmap']=vertmap
            dictionary['center']=center

            return (args.DIR_OUTPUT+args.PRE_LABELING+str(f'{index:06d}')+'-meta.mat', dictionary)
            #scipy.io.savemat(args.DIR_OUTPUT+str(f'{index:06d}')+'-meta.mat', mdict=dictionary)
        except:
            return None         

    def create_label_file(self,dict_annot,direc,n_comp, n_scene,n_view,index):
        try:
            img_label=np.zeros((480,640),dtype="uint8")
            file_label=args.DIR_OUTPUT+args.PRE_LABELING+str(f'{index:06d}')+"-label.png"
            
            for i,obj in enumerate(dict_annot):
                mask_file="mask_c"+str(n_comp)+"_s"+str(n_scene)+"_v"+str(n_view)+obj["mask_name"]+".png"
                mask_image=cv2.imread(direc+mask_file)[:,:,0]
                
                label_index=dict_label_indices[obj["object_class_name"]]
                
                mask_image=np.where(mask_image != 0, label_index, mask_image)
                img_label=np.maximum(img_label, mask_image)
             
            return (file_label,img_label)
            #cv2.imwrite(file_label, img_label)
        except:
            return None

    def create_color_file(self,direc,n_comp,n_scene,n_view,index):
        return scenarios.Color.create_color_file(list_textures, direc, n_comp, n_scene, n_view, index)
        """
        try:
            file_rgb="rgb_c"+str(n_comp)+"_s"+str(n_scene)+"_v"+str(n_view)+".png"
            file_depth="depth_c"+str(n_comp)+"_s"+str(n_scene)+"_v"+str(n_view)+".png"
            file_texture=list_textures[np.random.randint(len(list_textures))]
            file_output=args.DIR_OUTPUT+args.PRE_LABELING+str(f'{index:06d}')+"-color.png"
            file_backdrop="backdrop_c"+str(n_comp)+"_s"+str(n_scene)+"_v"+str(n_view)+".png"
            
            remove_background=False
            
            if remove_background:
                img_backdrop=255-cv2.imread(direc+file_backdrop,cv2.IMREAD_UNCHANGED)[:,:,0].astype('uint8')
                img_rgb=cv2.imread(direc+file_rgb)
                img_result=np.array(img_rgb,dtype="uint8")         
            
                img_result=cv2.cvtColor(img_result, cv2.COLOR_RGB2RGBA)
                img_result[:,:,3]=img_backdrop
            else:
                img_texture = cv2.imread(file_texture)  
                img_texture=cv2.resize(dsize=(640,480),src=img_texture)        
                img_depth=cv2.imread(direc+file_depth)
                img_rgb=cv2.imread(direc+file_rgb)
                
                img_result=np.array(img_texture,dtype="uint8")
                img_result=np.where(img_depth != 0, img_rgb, img_result)
            
            return (file_output, img_result)
        except:
            return None
        """

    def create_depth_file(self,direc,n_comp,n_scene,n_view,index):
        return None

        """
        try:  
            file_depth=direc+"range_c"+str(n_comp)+"_s"+str(n_scene)+"_v"+str(n_view)+".exr"
            file_backdrop=direc+"backdrop_c"+str(n_comp)+"_s"+str(n_scene)+"_v"+str(n_view)+".png"
            img_depth=cv2.imread(file_depth, cv2.IMREAD_UNCHANGED)[:,:,0]
           
            img_result=np.array(img_depth*10000, dtype = "uint16")
            
            remove_background=False
            
            if remove_background:
                zer=np.zeros((480,640), dtype = "uint16")
                img_backdrop=255-cv2.imread(file_backdrop,cv2.IMREAD_UNCHANGED)[:,:,0].astype('uint8')
                img_result=np.where(img_backdrop==0, zer, img_result)
            else:
                img_result=np.where(img_depth==10000000000.0, 0, img_result)
            
            file_result=args.DIR_OUTPUT+args.PRE_LABELING+str(f'{index:06d}')+"-depth.png"
                        
            return (file_result,img_result)
            #cv2.imwrite(file_result,img_result)
        except:
            return None
        """


def create_list_textures():
    for tex in os.listdir(args.DIR_BACKGROUND_TEXTURES):
        list_textures.append(args.DIR_BACKGROUND_TEXTURES+tex)
    
def create_list_of_annotation_files():
    direc=args.DIR_INPUT
    i=0
    for file in os.listdir(direc):            
        if str(file).startswith("annot"):
            if i>=args.START_AT_IMAGE_NUMBER and i<args.START_AT_IMAGE_NUMBER+args.NUMBER_OF_IMAGES:
                list_annot.append((direc,file))
            i+=1

def create_dict_label_indices():
    dict_label_indices["master_chef_can"]=1
    dict_label_indices["cracker_box"]=2
    dict_label_indices["sugar_box"]=3
    dict_label_indices["tomato_soup_can"]=4
    dict_label_indices["mustard_bottle"]=5
    dict_label_indices["tuna_fish_can"]=6
    dict_label_indices["pudding_box"]=7
    dict_label_indices["gelatin_box"]=8
    dict_label_indices["potted_meat_can"]=9
    dict_label_indices["banana"]=10
    dict_label_indices["pitcher_base"]=11
    dict_label_indices["bleach_cleanser"]=12
    dict_label_indices["bowl"]=13
    dict_label_indices["mug"]=14
    dict_label_indices["power_drill"]=15
    dict_label_indices["wood_block"]=16
    dict_label_indices["scissors"]=17
    dict_label_indices["large_marker"]=18
    dict_label_indices["large_clamp"]=19
    dict_label_indices["extra_large_clamp"]=20
    dict_label_indices["foam_brick"]=21

if __name__=="__main__":
    print(datetime.now())
    
    if not os.path.isdir(args.DIR_OUTPUT):
        os.mkdir(args.DIR_OUTPUT)
    
    create_list_of_annotation_files()
    create_list_textures()
    create_dict_label_indices()
    
    print("Length: "+str(len(list_annot)),file=sys.stderr, flush=True)
    
    #with concurrent.futures.ThreadPoolExecutor(max_workers=args.THREAD_LIMIT) as executor:
    #    for i,(direc,file) in enumerate(list_annot): 
    #        executor.submit(Worker(i+args.START_AT_IMAGE_NUMBER,direc,file).process_data)
    for i,(direc,file) in enumerate(list_annot): 
        Worker(i,direc,file).process_data()
    
    print(datetime.now())