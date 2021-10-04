import os
import shutil
import numpy as np
import scipy.io
from scipy.spatial.transform import Rotation as R
import subprocess

DIR_REPLICATED_DATA="Result/"
DIR_REPLICATED_REF="Ref/"
DIR_TEMPORARY="Temporary/"
FILE_OWN_SCENARIO="/pfs/data5/home/kit/anthropomatik/yc5412/amira_blender_rendering/src/amira_blender_rendering/scenes/own scenarios distractor within parts.py"

N_TO_REPLICATE=10

l_files_syn=[]
l_files_real=[]
l_files=[]

class Creator():
    def __init__(self):
        np.random.seed(12345)
    
        self.create_list_of_files()
        self.get_n_random_files()
        self.create_dirs_and_copy_files()
        
    def get_n_random_files(self):
        global l_files
        global l_files_syn
        global l_files_real
        
        for i in range(N_TO_REPLICATE):
            l_files.append(l_files_syn[i])
        
        for i in range(N_TO_REPLICATE):
            l_files.append(l_files_real[i])
            
    def create_list_of_files(self):
        global l_files_real
        global l_files_syn
    
        path="/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data/"
        path_syn="/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data_syn/"
        
        for i in range(48,60):
            p=path+f"{i:04d}"+"/"
            l_files_real=l_files_real+[(p,file.replace("-meta.mat","")) for file in os.listdir(p) if "-meta.mat" in file]
        
        np.random.shuffle(l_files_real) 
        np.random.shuffle(l_files_syn)        

        l_files_syn=[(path_syn,file.replace("-meta.mat","")) for file in os.listdir(path_syn) if "-meta.mat" in file]
    
    def create_dirs_and_copy_files(self):    
        if not os.path.isdir(DIR_REPLICATED_DATA):
            os.makedirs(DIR_REPLICATED_DATA)
            
        if not os.path.isdir(DIR_REPLICATED_REF):
            os.makedirs(DIR_REPLICATED_REF)
    
        if not os.path.isdir(DIR_TEMPORARY):
            os.makedirs(DIR_TEMPORARY)
    
    def copy_temporary_files(self):
        shutil.copy("config_template.cfg",DIR_TEMPORARY+"config_template.cfg")
        shutil.copy("scene_template.blend",DIR_TEMPORARY+"scene_template.blend")
        
        shutil.copy(FILE_OWN_SCENARIO,"Temporary/scenario.py")
        
    def remove_temporary_files(self):
        shutil.copy("Temporary/scenario.py",FILE_OWN_SCENARIO)
        
        shutil.rmtree(DIR_TEMPORARY)
        shutil.rmtree("ResultAmira")
        shutil.rmtree("TemporaryAmira")
        
    def copy_ref_files(self, path, file,index):        
        shutil.copy(path+file+"-meta.mat",DIR_REPLICATED_REF+"Ref"+f"{index:06d}"+"-meta.mat")
        shutil.copy(path+file+"-depth.png",DIR_REPLICATED_REF+"Ref"+f"{index:06d}"+"-depth.png")
        shutil.copy(path+file+"-color.png",DIR_REPLICATED_REF+"Ref"+f"{index:06d}"+"-color.png")
        shutil.copy(path+file+"-label.png",DIR_REPLICATED_REF+"Ref"+f"{index:06d}"+"-label.png")
        
    def change_amira(self, index, path, file,syn_object):
        def get_str_target_objects(mat):
            content="targets=["
                        
            for i in range(len(mat['cls_indexes'])-1):
                content=content+"list(all_target_objects)["+str(mat['cls_indexes'][i][0]-1)+"], "
                
            content=content+"list(all_target_objects)["+str(mat['cls_indexes'][len(mat['cls_indexes'])-1][0]-1)+"]"
            
            content=content+"]"
                        
            return content
        def get_str_camera_coords(mat):
            row_to_be_added = np.array([0,0,0,1])
            if not 'rotation_translation_matrix' in mat:
                mat['rotation_translation_matrix']=np.array([[1,0,0,0],[0,-1,0,0],[0,0,-1,0]])
            
            R.from_matrix(np.vstack((mat['rotation_translation_matrix'], row_to_be_added))[0:3,0:3]).as_euler('xyz', degrees=True)
            mat['rotation_translation_matrix']

            loc="obj.location=("+str(mat['rotation_translation_matrix'][0,3])+", "+str(mat['rotation_translation_matrix'][1,3])+", "+str(mat['rotation_translation_matrix'][2,3])+")\n"
            rot="obj.rotation_euler=self.to_radian"+str((R.from_matrix(np.vstack((mat['rotation_translation_matrix'], row_to_be_added))[0:3,0:3]).as_euler('xyz', degrees=True)[0],R.from_matrix(np.vstack((mat['rotation_translation_matrix'], row_to_be_added))[0:3,0:3]).as_euler('xyz', degrees=True)[1],R.from_matrix(np.vstack((mat['rotation_translation_matrix'], row_to_be_added))[0:3,0:3]).as_euler('xyz', degrees=True)[2]))
            
            return (loc,rot)
        def change_run_amira(index):
            f=open("runAmira.sh","r")
            content=f.read()
            f.close()
            
            content=content.replace("#START_AT_IMAGE_NUMBER",str(index))
            
            f=open(DIR_TEMPORARY+"runAmira.sh","w")
            f.write(content)
            f.close()
        def change_amira_script(path,file,mat):
            f=open("amira.py","r")
            content=f.read()
            f.close()
            
            str_target_objects=get_str_target_objects(mat)
            (loc,rot)=get_str_camera_coords(mat)
            content=content.replace("#change_target_objects_here", str_target_objects)
            content=content.replace("#change_camera_loc_here", loc)
            content=content.replace("#change_camera_rot_here", rot)
            
            f=open(DIR_TEMPORARY+"amira.py","w")
            f.write(content)
            f.close()
        def get_str_objects_loc_rot(mat):        
            row_to_be_added = np.array([0,0,0,1])
            content=""
                   
            length=len(mat['cls_indexes'])
            for i in range(length):
                rot_x=R.from_matrix(np.matmul(np.vstack((mat['rotation_translation_matrix'], row_to_be_added)),np.vstack((mat['poses'][:,:,i], row_to_be_added)))[0:3,0:3]).as_euler('xyz', degrees=True)[0]
                rot_y=R.from_matrix(np.matmul(np.vstack((mat['rotation_translation_matrix'], row_to_be_added)),np.vstack((mat['poses'][:,:,i], row_to_be_added)))[0:3,0:3]).as_euler('xyz', degrees=True)[1]
                rot_z=R.from_matrix(np.matmul(np.vstack((mat['rotation_translation_matrix'], row_to_be_added)),np.vstack((mat['poses'][:,:,i], row_to_be_added)))[0:3,0:3]).as_euler('xyz', degrees=True)[2]
                
                loc_x=np.matmul(np.vstack((mat['rotation_translation_matrix'], row_to_be_added)),np.vstack((mat['poses'][:,:,i], row_to_be_added)))[0:3,3:4][0]
                loc_y=np.matmul(np.vstack((mat['rotation_translation_matrix'], row_to_be_added)),np.vstack((mat['poses'][:,:,i], row_to_be_added)))[0:3,3:4][1]
                loc_z=np.matmul(np.vstack((mat['rotation_translation_matrix'], row_to_be_added)),np.vstack((mat['poses'][:,:,i], row_to_be_added)))[0:3,3:4][2]
                
                content=content+"            self.objs["+str(i)+"]['bpy'].location="+str((loc_x[0],loc_y[0],loc_z[0]))+"\n"
                content=content+"            self.objs["+str(i)+"]['bpy'].rotation_euler=self.to_radian"+str((rot_x,rot_y,rot_z))+"\n\n"
                
            return content
        def change_scenario(mat):
            f=open("Temporary/scenario.py","r")
            content=f.read()
            f.close()
            
            str_change_objects_loc_rot=get_str_objects_loc_rot(mat)
                        
            content=content.replace("self.change_camera_location_randomly(dist, alpha)","#self.change_camera_location_randomly(dist, alpha)")
            content=content.replace("#change_objects_loc_rot_here",str_change_objects_loc_rot)
                        
            f=open(FILE_OWN_SCENARIO,"w")
            f.write(content)
            f.close()
        
        mat = scipy.io.loadmat(path+file+'-meta.mat')
        
        if syn_object:
            mat['cls_indexes']=np.array([[int(x)] for x in mat['cls_indexes']])
                               
        change_run_amira(index)
        change_amira_script(path,file,mat)
        change_scenario(mat)
       
    def run_amira(self):   
        subprocess.run(["sh", "Temporary/runAmira.sh"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)#,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL
    
    def run_convert(self):
        subprocess.run(["sh", "runConvert.sh"]) #,stdout=subprocess.DEVNULL
       
    def create_data(self):        
        global l_files
        
        self.copy_temporary_files()
                
        for i,(path,file) in enumerate(l_files):
            self.copy_ref_files(path,file,i)
            self.change_amira(i,path,file,"data_syn" in path)
            self.run_amira()
            
            print((i+1),"/",len(l_files))
            
        self.run_convert()
            
        self.remove_temporary_files()
    
if __name__=="__main__":
    Creator().create_data()