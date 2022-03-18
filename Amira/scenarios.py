import bpy
import numpy as np
import sys
import bpy_extras
import math
import mathutils
import os
import pickle

sys.path+=['/pfs/data5/software_uc2/bwhpc/common/vis/blender/2.90.1/2.90/scripts/startup', '/pfs/data5/software_uc2/bwhpc/common/vis/blender/2.90.1/2.90/scripts/modules', '/pfs/data5/software_uc2/bwhpc/common/vis/blender/2.90.1/2.90/python/lib/python37.zip', '/pfs/data5/software_uc2/bwhpc/common/vis/blender/2.90.1/2.90/python/lib/python3.7', '/pfs/data5/software_uc2/bwhpc/common/vis/blender/2.90.1/2.90/python/lib/python3.7/lib-dynload', '/pfs/data5/software_uc2/bwhpc/common/vis/blender/2.90.1/2.90/python/lib/python3.7/site-packages', '/pfs/data5/software_uc2/bwhpc/common/vis/blender/2.90.1/2.90/scripts/freestyle/modules', '/pfs/data5/software_uc2/bwhpc/common/vis/blender/2.90.1/2.90/scripts/addons/modules', '/home/kit/anthropomatik/yc5412/.config/blender/2.90/scripts/addons/modules', '/pfs/data5/software_uc2/bwhpc/common/vis/blender/2.90.1/2.90/scripts/addons', '/home/kit/anthropomatik/yc5412/.conda/envs/amira_venv/lib/python3.7/site-packages']

#sys.path.append("/home/kit/anthropomatik/yc5412/.conda/envs/amira_venv/lib/python3.7/site-packages")

import scipy.io
from scipy.spatial.transform import Rotation as R

#amira Script

BASE_PATH_TO_READ_FILES_IN="/pfs/data5/home/kit/anthropomatik/yc5412/YCB_Video_Dataset/data_syn_ori"

def degree_to_radian(degree):
    return degree/180.0*np.pi

def angle_between_vectors(v_1,v_2):
    if np.linalg.norm(v_1)==0:
        raise ValueError("v_1 has norm 0")
    if np.linalg.norm(v_2)==0:
        raise ValueError("v_2 has norm 0")

    return np.dot(v_1,v_2)/np.linalg.norm(v_1)/np.linalg.norm(v_2)

class Lights():
    def __init__(self, index):
        self.index=index
        np.random.seed()
        
    def change_lights_properties(self, lights):
        print("change light poperties")
        self.scenario_2(lights)
        
    def scenario_1(self,lights):    #scenario parts (target, distractor) on floor
        def change_light_color_randomly(light, brightness):
            r = np.random.uniform()*brightness
            g = np.random.uniform(r/2,min(1.0,r*2))*brightness
            b = np.random.uniform(max(r,g)/2,min(r,g)*2)*brightness
            
            light.data.color=(r,g,b)
        
        def place_lights_randomly(light):
            x = np.random.uniform()*2-1
            y = np.random.uniform()*2-1
            z = np.random.uniform()*2-1

            light.location.x =1.5*x+0
            light.location.y =1.5*y+0
            light.location.z =0.5*z+1.5
                    
        #bpy.context.scene.world.light_settings.ao_factor = 0.19 * np.random.uniform() + 0.01  # random ambient occlusion
        bpy.context.scene.world.light_settings.ao_factor = 0.15
        brightness=np.random.uniform(0.5,1)
        
        for light in lights:   
            change_light_color_randomly(light, brightness)
            place_lights_randomly(light)
        
    def scenario_2(self,lights):    #scenario parts (target, distractor) in air
        def change_light_color_randomly(light, brightness):
            r = np.random.uniform()*brightness
            g = np.random.uniform(r/2,min(1.0,r*2))*brightness
            b = np.random.uniform(max(r,g)/2,min(r,g)*2)*brightness
            
            light.data.color=(r,g,b)
        
        def place_lights_randomly(light):
            x = np.random.uniform()*2-1
            y = np.random.uniform()*2-1
            z = np.random.uniform()*2-1

            light.location.x =1.5*x+0
            light.location.y =1.5*y-(0.617447 + 1.259349)/2
            light.location.z =0.5*z+2.5
                    
        bpy.context.scene.world.light_settings.ao_factor = 0.19 * np.random.uniform() + 0.01  # random ambient occlusion
        brightness=np.random.uniform(0.5,1)
        
        for light in lights:   
            change_light_color_randomly(light, brightness)
            place_lights_randomly(light)
       
    def scenario_3(self,lights):    #this scenario darkens the lights and sets the ambient occlusion value to a fixed one
        bpy.context.scene.world.light_settings.ao_factor = 0.22
        
        for light in lights:
            light.data.color=(0,0,0)

    def scenario_4(self,lights):    #scenario parts (target, distractor) in air 2
        def change_light_color_randomly(light, brightness):
            r = np.random.uniform()*brightness
            g = np.random.uniform(r/2,min(1.0,r*2))*brightness
            b = np.random.uniform(max(r,g)/2,min(r,g)*2)*brightness
            
            light.data.color=(r,g,b)
        
        def place_lights_randomly(light):
            x = np.random.uniform()*2-1
            y = np.random.uniform()*2-1
            z = np.random.uniform()*2-1

            light.location.x =1.5*x+0
            light.location.y =1.5*y+0
            light.location.z =0.5*z+1.5
          
        bpy.context.scene.world.light_settings.ao_factor = 0.19 * np.random.uniform() + 0.01  # random ambient occlusion
        brightness=np.random.uniform(0.5,1)
        
        for light in lights:   
            change_light_color_randomly(light, brightness)
            place_lights_randomly(light)

class ObjectComposition():
    def __init__(self,index):
        self.index=index
        np.random.seed()
    
    def get_object_composition(self, all_target_objects, all_distractor_objects):   #(list_of_target_objects, list_of_distractor_objects)
        #return self.scenario_1(all_target_objects, all_distractor_objects)
        return self.scenario_6(all_target_objects, all_distractor_objects)
      
    def scenario_1(self, all_target_objects, all_distractor_objects):   #4 - 8 uniformly distributed target objects, no distractor objects
        targets=[]
        distractors=[]
    
        n_target_obj=np.random.randint(4,8)
                
        while len(targets)<n_target_obj:
            i=np.random.randint(0,len(all_target_objects)) 
            if not list(all_target_objects)[i] in targets:   
                targets.append(list(all_target_objects)[i])  
    
        return (targets, distractors)
    
    def scenario_2(self, all_target_objects, all_distractor_objects):   #6 - 15 uniformly distributed target objects, no distractor objects
        targets=[]
        distractors=[]
    
        n_target_obj=np.random.randint(6,15)
                
        while len(targets)<n_target_obj:
            i=np.random.randint(0,len(all_target_objects)) 
            if not list(all_target_objects)[i] in targets:   
                targets.append(list(all_target_objects)[i])  
    
        return (targets, distractors)

    def scenario_3(self, all_target_objects, all_distractor_objects):   #this scenario reproduces the orignal synthetic dataset
        targets=[]
        distractors=[]

        l=[os.path.join(BASE_PATH_TO_READ_FILES_IN,x) for x in os.listdir(BASE_PATH_TO_READ_FILES_IN) if "meta" in x]
        l.sort()

        if self.index>=len(l):
            return None

        mat=scipy.io.loadmat(l[self.index])
        indices=mat['cls_indexes'][0]
        indices=[int(x) for x in indices]


        for index in indices:
            targets.append(list(all_target_objects)[index-1])

        return (targets, distractors)

    def scenario_4(self, all_target_objects, all_distractor_objects):   #11 - 15 uniformly distributed target objects, no distractor objects
        targets=[]
        distractors=[]
    
        n_target_obj=np.random.randint(11,15)
                
        while len(targets)<n_target_obj:
            i=np.random.randint(0,len(all_target_objects)) 
            if not list(all_target_objects)[i] in targets:   
                targets.append(list(all_target_objects)[i])  
    
        return (targets, distractors)
    
    def scenario_5(self, all_target_objects, all_distractor_objects):   #4 - 8 uniformly distributed target objects, no distractor objects
        targets=[]
        distractors=[]
    
        n_target_obj=np.random.randint(4,8)
                
        while len(targets)<n_target_obj:
            i=np.random.randint(0,len(all_target_objects)) 
            if not list(all_target_objects)[i] in targets:   
                targets.append(list(all_target_objects)[i])  
    
        return (targets, distractors)

    def scenario_6(self, all_target_objects, all_distractor_objects):   #8 - 12 uniformly distributed target objects, no distractor objects
        targets=[]
        distractors=[]
    
        n_target_obj=np.random.randint(8,12)
                
        while len(targets)<n_target_obj:
            i=np.random.randint(0,len(all_target_objects)) 
            if not list(all_target_objects)[i] in targets:   
                targets.append(list(all_target_objects)[i])  
    
        return (targets, distractors)
    

#own scenario

class Objects():
    def __init__(self, synthetic_sample):
        self.synthetic_sample=synthetic_sample
        np.random.seed()

    def randomize_object_transforms(self, target_objs, distractor_objs):
        self.scenario_2(target_objs, distractor_objs)

    def scenario_1(self, target_objs, distractor_objs): #places objects     
        def add_keyframes(obj):
            for i in range(int(1000/20)):
                obj.rigid_body.enabled=False
                obj.keyframe_insert(data_path="rigid_body.enabled", frame=i*20)
                obj.rigid_body.enabled=True
                obj.keyframe_insert(data_path="rigid_body.enabled", frame=i*20+1)
        def calculate_z_coordinate(obj, height_map, height_map_size, height_map_resolution):
            min_height=-min([(obj.matrix_world @ mathutils.Vector(corner))[2] for corner in obj.bound_box])

            height_map_resolution/=2

            h=0
            for vertex in obj.data.vertices:
                a=vertex.co.copy()
                a.resize_4d()
                a[3]=1

                co_final = obj.matrix_world @ a
                co_final_xy=np.array(co_final[0:2])

                height_map_xy=co_final_xy*height_map_resolution/height_map_size+height_map_resolution

                h=max(h,height_map[int(np.floor(height_map_xy[0])),int(np.floor(height_map_xy[1]))])
                h=max(h,height_map[int(np.floor(height_map_xy[0])),int(np.ceil(height_map_xy[1]))])
                h=max(h,height_map[int(np.ceil(height_map_xy[0])),int(np.floor(height_map_xy[1]))])
                h=max(h,height_map[int(np.ceil(height_map_xy[0])),int(np.ceil(height_map_xy[1]))])

            return min_height + h + 0.005

        def update_height_map(obj, height_map, height_map_size, height_map_resolution):
            max_height=max([(obj.matrix_world @ mathutils.Vector(corner))[2] for corner in obj.bound_box])

            height_map_resolution/=2

            for vertex in obj.data.vertices:
                a=vertex.co.copy()
                a.resize_4d()
                a[3]=1

                co_final = obj.matrix_world @ a
                co_final_xy=np.array(co_final[0:2])

                height_map_xy=co_final_xy*height_map_resolution/height_map_size+height_map_resolution

                height_map[int(np.floor(height_map_xy[0])),int(np.floor(height_map_xy[1]))]=max_height
                height_map[int(np.floor(height_map_xy[0])),int(np.ceil(height_map_xy[1]))]=max_height
                height_map[int(np.ceil(height_map_xy[0])),int(np.floor(height_map_xy[1]))]=max_height
                height_map[int(np.ceil(height_map_xy[0])),int(np.ceil(height_map_xy[1]))]=max_height
        
        objs=target_objs+distractor_objs

        height_map_size=1
        height_map_resolution=1000
        height_map=np.zeros((height_map_resolution, height_map_resolution))
        
        bpy.context.view_layer.update()

        for i,obj in enumerate(objs):
            bpy.context.view_layer.update()

            obj.rotation_euler[2]=np.random.uniform(0,2 * np.pi)

            loc_xy=(np.random.beta(1.7,1.7,size=2) * 2 - 1) * 0.20
            obj.location=(loc_xy[0],loc_xy[1],0)

            bpy.context.view_layer.update()

            loc_z=calculate_z_coordinate(obj, height_map, height_map_size, height_map_resolution)
            obj.location[2]=loc_z

            bpy.context.view_layer.update()

            update_height_map(obj, height_map, height_map_size, height_map_resolution)
            
            add_keyframes(obj)

        #TODO, for correct placement, study max distance between camera and object
        #place objects in [-0.2, 0.2] x [-0.2, 0.2] beta distributed, evtl doch nicht

    def scenario_2(self,target_objects, distractor_objects): #this scenario places objects at random positions in the air
        objs=target_objects+distractor_objects

        for obj in objs:
            bpy.context.view_layer.update()
            y=np.random.uniform(-0.617447, -1.259498)     

            max_dist_x=-0.31*y
            x=np.random.uniform(-max_dist_x,max_dist_x)

            max_dist_z=-0.23*y
            z=np.random.uniform(-max_dist_z,max_dist_z)+1

            obj.matrix_world.translation=(x,y,z)

            rot=np.random.uniform(0,np.pi*2,size=3)
            obj.rotation_euler=(rot[0],rot[1],rot[2])
        
        bpy.context.view_layer.update()

    def scenario_3(self,target_objects, distractor_objects):   #This scenario places the object directly like in the synthetic samples
        l=[os.path.join(BASE_PATH_TO_READ_FILES_IN,x) for x in os.listdir(BASE_PATH_TO_READ_FILES_IN) if "-meta.mat" in x]
        l.sort()

        if len(l)<=self.synthetic_sample:
            print("Too many images are created for this scenario!",file=sys.stderr)
            return

        for i,obj in enumerate(target_objects):
            mat=scipy.io.loadmat(l[self.synthetic_sample])
            pose=mat['poses'][:,:,i]
            pose=np.array([pose[0],pose[1],pose[2],[0,0,0,1]])
            
            if 'rotation_translation_matrix' in mat:
                cam_matrix=mat['rotation_translation_matrix']    
                cam_matrix=np.array([cam_matrix[0],cam_matrix[1],cam_matrix[2],[0,0,0,1]])
                #mirror=np.asarray([[1,0,0,0],[0,-1,0,0],[0,0,-1,0],[0,0,0,1]])  #mirror z and y                    
                #cam_matrix=np.matmul(cam_matrix,mirror)
            else:
                cam_matrix=np.array([[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]])

            pose=np.matmul(cam_matrix,pose)

            obj.matrix_world=pose.transpose()

        bpy.context.view_layer.update()

    def scenario_4(self,target_objects, distractor_objects):   #This scenario trys to recreate the distibution of the location of the samples of the original synthetic dataset
        def get_val(relative_value, arr):
            index=relative_value*float(len(arr)-1)

            up=int(np.ceil(index))
            down=int(np.floor(index))

            return (1.0-(index-down))*arr[down] + (1.0-(up-index))*arr[up]
        
        objs=target_objects+distractor_objects

        synthetic_x_locations=[-0.38443, -0.253749, -0.227297, -0.214775, -0.203392, -0.19465, -0.188454, -0.183379, -0.178722, -0.17408, -0.169947, -0.165729, -0.162209, -0.158902, -0.155884, -0.153092, -0.150274, -0.147532, -0.14465, -0.141954, -0.139634, -0.137319, -0.134982, -0.132752, -0.130476, -0.128112, -0.125957, -0.123843, -0.121681, -0.119622, -0.117507, -0.115248, -0.113032, -0.110943, -0.108986, -0.106916, -0.10471, -0.102699, -0.100661, -0.098802, -0.096914, -0.095058, -0.093202, -0.091455, -0.089604, -0.087812, -0.086116, -0.084433, -0.082766, -0.081093, -0.079364, -0.077674, -0.075989, -0.074278, -0.072526, -0.070864, -0.06915, -0.067455, -0.065667, -0.063812, -0.061972, -0.060276, -0.058616, -0.056816, -0.055044, -0.053214, -0.051572, -0.049877, -0.048179, -0.046559, -0.044905, -0.043142, -0.041516, -0.03959, -0.037895, -0.036234, -0.034537, -0.03288, -0.031167, -0.029329, -0.027477, -0.025725, -0.023949, -0.022121, -0.020116, -0.018226, -0.01628, -0.014405, -0.012607, -0.010729, -0.008829, -0.007003, -0.005112, -0.003269, -0.00139, 0.000502, 0.00236, 0.00425, 0.006221, 0.008257, 0.010289, 0.012151, 0.01406, 0.015848, 0.017716, 0.019541, 0.021325, 0.023197, 0.025007, 0.026873, 0.028737, 0.030642, 0.032454, 0.034186, 0.036029, 0.037924, 0.039783, 0.041572, 0.043273, 0.045035, 0.046797, 0.048562, 0.050285, 0.052002, 0.053663, 0.055251, 0.056801, 0.058457, 0.060166, 0.061937, 0.063729, 0.065459, 0.067217, 0.068921, 0.07059, 0.0722, 0.073741, 0.075418, 0.077166, 0.078838, 0.080516, 0.082169, 0.083971, 0.085827, 0.08757, 0.089365, 0.091146, 0.092846, 0.094666, 0.096539, 0.098298, 0.100024, 0.101857, 0.103666, 0.105489, 0.107406, 0.109375, 0.111358, 0.113518, 0.115895, 0.118292, 0.120488, 0.122693, 0.124856, 0.126874, 0.129055, 0.131004, 0.133032, 0.135203, 0.137405, 0.139603, 0.141958, 0.144184, 0.146437, 0.148928, 0.15141, 0.154131, 0.156841, 0.159448, 0.162314, 0.165222, 0.168105, 0.171271, 0.174482, 0.178017, 0.181475, 0.184893, 0.189299, 0.193381, 0.197736, 0.202781, 0.208884, 0.215181, 0.22187, 0.229131, 0.237448, 0.247651, 0.263751, 0.283056, 0.310114]
        synthetic_y_locations=[-0.301121, -0.223364, -0.203119, -0.189939, -0.179939, -0.171358, -0.164597, -0.158941, -0.154012, -0.149287, -0.144738, -0.140413, -0.136113, -0.132415, -0.128556, -0.124737, -0.121411, -0.11796, -0.114443, -0.110853, -0.10777, -0.104775, -0.101848, -0.099108, -0.096672, -0.094401, -0.092039, -0.089842, -0.087493, -0.085396, -0.083267, -0.081209, -0.079272, -0.077246, -0.075406, -0.07355, -0.07174, -0.069849, -0.067953, -0.066163, -0.064413, -0.062595, -0.060813, -0.059092, -0.057533, -0.056075, -0.054603, -0.053195, -0.051817, -0.050348, -0.04897, -0.047613, -0.046282, -0.044933, -0.04343, -0.041991, -0.040597, -0.039108, -0.037742, -0.03645, -0.035095, -0.033717, -0.032428, -0.031134, -0.02986, -0.028622, -0.027305, -0.026009, -0.024721, -0.023525, -0.022327, -0.020995, -0.019696, -0.018416, -0.017157, -0.015913, -0.01476, -0.013543, -0.012321, -0.011138, -0.009897, -0.008752, -0.00762, -0.006449, -0.005287, -0.004185, -0.003028, -0.001861, -0.000728, 0.000411, 0.001523, 0.002596, 0.003693, 0.004769, 0.005832, 0.006892, 0.00799, 0.009028, 0.010081, 0.011093, 0.012086, 0.013162, 0.014236, 0.015236, 0.016242, 0.017302, 0.018282, 0.01928, 0.020284, 0.021241, 0.022211, 0.023232, 0.02421, 0.025199, 0.026179, 0.02718, 0.028179, 0.029156, 0.030182, 0.031121, 0.03215, 0.03317, 0.034248, 0.035372, 0.036538, 0.037716, 0.038816, 0.039997, 0.041106, 0.042227, 0.043308, 0.044408, 0.045496, 0.046502, 0.04757, 0.048656, 0.049696, 0.050821, 0.051891, 0.05303, 0.054085, 0.055131, 0.056231, 0.057383, 0.058517, 0.059658, 0.060805, 0.062009, 0.063237, 0.064368, 0.065581, 0.06677, 0.068059, 0.069353, 0.070705, 0.072081, 0.073411, 0.074793, 0.076116, 0.077367, 0.078673, 0.080088, 0.081443, 0.082875, 0.084197, 0.085551, 0.086951, 0.088443, 0.089936, 0.091434, 0.092959, 0.094524, 0.096141, 0.09789, 0.099795, 0.101729, 0.103538, 0.105519, 0.107575, 0.109759, 0.112003, 0.114337, 0.116528, 0.118777, 0.121191, 0.124063, 0.126936, 0.130308, 0.134088, 0.137564, 0.14141, 0.146079, 0.151285, 0.157467, 0.163942, 0.172107, 0.180919, 0.192593, 0.206693, 0.240767]
        synthetic_z_locations=[-0.284354, -0.401648, -0.445126, -0.46843, -0.487161, -0.501761, -0.512732, -0.524467, -0.534835, -0.543585, -0.551038, -0.55838, -0.564808, -0.569943, -0.57511, -0.580325, -0.585186, -0.589411, -0.593528, -0.598055, -0.602521, -0.607322, -0.611935, -0.61707, -0.62265, -0.627236, -0.632013, -0.636481, -0.641058, -0.645431, -0.650409, -0.655015, -0.659539, -0.663836, -0.668571, -0.673084, -0.67742, -0.681594, -0.68597, -0.690278, -0.694334, -0.698105, -0.702415, -0.706956, -0.711011, -0.714919, -0.718902, -0.722663, -0.726518, -0.730489, -0.734204, -0.737795, -0.741323, -0.744516, -0.747834, -0.751217, -0.754587, -0.757705, -0.760844, -0.764515, -0.767916, -0.771256, -0.774668, -0.778165, -0.782007, -0.785292, -0.788738, -0.791846, -0.795129, -0.798411, -0.801749, -0.80507, -0.808645, -0.812069, -0.815417, -0.818937, -0.822443, -0.825907, -0.829319, -0.832912, -0.836437, -0.839711, -0.843219, -0.846569, -0.850009, -0.853547, -0.856993, -0.860277, -0.863439, -0.866812, -0.870327, -0.873411, -0.87666, -0.880386, -0.88361, -0.886317, -0.889507, -0.892807, -0.89626, -0.899884, -0.903492, -0.906756, -0.910056, -0.913316, -0.916485, -0.91993, -0.923051, -0.926258, -0.929122, -0.932336, -0.935826, -0.939539, -0.94335, -0.946629, -0.949956, -0.953317, -0.956778, -0.960152, -0.963325, -0.966695, -0.970179, -0.973323, -0.976013, -0.9791, -0.982434, -0.985329, -0.988536, -0.992038, -0.995596, -0.998955, -1.00254, -1.006243, -1.010221, -1.014246, -1.018029, -1.021809, -1.025533, -1.029226, -1.032898, -1.036615, -1.040448, -1.044371, -1.048525, -1.052602, -1.056849, -1.060914, -1.065112, -1.069075, -1.073412, -1.077055, -1.081282, -1.08561, -1.089902, -1.09426, -1.098431, -1.102177, -1.105978, -1.11024, -1.114266, -1.118451, -1.122758, -1.127628, -1.132364, -1.137293, -1.142038, -1.146479, -1.150469, -1.154953, -1.159475, -1.163854, -1.169115, -1.175008, -1.180282, -1.185141, -1.189939, -1.195572, -1.201604, -1.207642, -1.21297, -1.218161, -1.22499, -1.232457, -1.239958, -1.245646, -1.250368, -1.255408, -1.26245, -1.270238, -1.277885, -1.287277, -1.296419, -1.305319, -1.31561, -1.3253, -1.336004, -1.356799, -1.383766, -1.423508, -1.477195, -1.560456]
                
        for obj in objs:
            bpy.context.view_layer.update()            
            
            relative_location=np.random.uniform(1e-5,1-1e-5, size=3)

            x=get_val(relative_location[0],synthetic_x_locations)
            y=get_val(relative_location[1],synthetic_y_locations)
            z=get_val(relative_location[2],synthetic_z_locations)

            obj.matrix_world.translation=(x,y,z)

            rot=np.random.uniform(0,np.pi*2,size=3)
            obj.rotation_euler=(rot[0],rot[1],rot[2])
        
        bpy.context.view_layer.update()

    def scenario_5(self,target_objects, distractor_objects):    #This scenario selects randomly locations from the original synthetic dataset
        with open("Translations.txt", 'rb') as f:
            l = pickle.load(f)
        
        objs=target_objects+distractor_objects

        for obj in objs:
            bpy.context.view_layer.update()    

            location=l[np.random.randint(0,len(l))]

            obj.matrix_world.translation=tuple(location)

            rot=np.random.uniform(0,np.pi*2,size=3)
            obj.rotation_euler=(rot[0],rot[1],rot[2])

        bpy.context.view_layer.update()

    def scenario_6(self, target_objs, distractor_objs): #places objects     
        def add_keyframes(obj):
            for i in range(int(1000/20)):
                obj.rigid_body.enabled=False
                obj.keyframe_insert(data_path="rigid_body.enabled", frame=i*20)
                obj.rigid_body.enabled=True
                obj.keyframe_insert(data_path="rigid_body.enabled", frame=i*20+1)
        def calculate_z_coordinate(obj, height_map, height_map_size, height_map_resolution):
            min_height=-min([(obj.matrix_world @ mathutils.Vector(corner))[2] for corner in obj.bound_box])

            height_map_resolution/=2

            h=0
            for vertex in obj.data.vertices:
                a=vertex.co.copy()
                a.resize_4d()
                a[3]=1

                co_final = obj.matrix_world @ a
                co_final_xy=np.array(co_final[0:2])

                height_map_xy=co_final_xy*height_map_resolution/height_map_size+height_map_resolution

                h=max(h,height_map[int(np.floor(height_map_xy[0])),int(np.floor(height_map_xy[1]))])
                h=max(h,height_map[int(np.floor(height_map_xy[0])),int(np.ceil(height_map_xy[1]))])
                h=max(h,height_map[int(np.ceil(height_map_xy[0])),int(np.floor(height_map_xy[1]))])
                h=max(h,height_map[int(np.ceil(height_map_xy[0])),int(np.ceil(height_map_xy[1]))])

            return min_height + h + 0.005

        def update_height_map(obj, height_map, height_map_size, height_map_resolution):
            max_height=max([(obj.matrix_world @ mathutils.Vector(corner))[2] for corner in obj.bound_box])

            height_map_resolution/=2

            for vertex in obj.data.vertices:
                a=vertex.co.copy()
                a.resize_4d()
                a[3]=1

                co_final = obj.matrix_world @ a
                co_final_xy=np.array(co_final[0:2])

                height_map_xy=co_final_xy*height_map_resolution/height_map_size+height_map_resolution

                height_map[int(np.floor(height_map_xy[0])),int(np.floor(height_map_xy[1]))]=max_height
                height_map[int(np.floor(height_map_xy[0])),int(np.ceil(height_map_xy[1]))]=max_height
                height_map[int(np.ceil(height_map_xy[0])),int(np.floor(height_map_xy[1]))]=max_height
                height_map[int(np.ceil(height_map_xy[0])),int(np.ceil(height_map_xy[1]))]=max_height
        
        objs=target_objs+distractor_objs

        height_map_size=1
        height_map_resolution=1000
        height_map=np.zeros((height_map_resolution, height_map_resolution))
        
        bpy.context.view_layer.update()

        for i,obj in enumerate(objs):
            bpy.context.view_layer.update()

            obj.rotation_euler[2]=np.random.uniform(0,2 * np.pi)

            if np.random.choice([True,False]):
                obj.rotation_euler[0]=np.random.uniform(0,2 * np.pi)
                obj.rotation_euler[1]=np.random.uniform(0,2 * np.pi)

            loc_xy=(np.random.beta(1.7,1.7,size=2) * 2 - 1) * 0.35
            obj.location=(loc_xy[0],loc_xy[1],0)

            bpy.context.view_layer.update()

            loc_z=calculate_z_coordinate(obj, height_map, height_map_size, height_map_resolution)
            obj.location[2]=loc_z

            bpy.context.view_layer.update()

            update_height_map(obj, height_map, height_map_size, height_map_resolution)
            
            add_keyframes(obj)

        #TODO, for correct placement, study max distance between camera and object
        #place objects in [-0.2, 0.2] x [-0.2, 0.2] beta distributed, evtl doch nicht

class Camera():

    def __init__(self, synthetic_sample):
        self.synthetic_sample=synthetic_sample
        np.random.seed()

    def randomize_camera_transforms(self, cam, target_objects, distractor_objects):
        self.scenario_3(cam, target_objects)

    def scenario_1(self,cam):
        dist=0.8
        alpha=50
        rad=degree_to_radian(alpha)

        y=-np.cos(rad)*dist
        z=np.sin(rad)*dist
        cam.location=(0,y,z)
        cam.rotation_euler=(degree_to_radian(-alpha-90),0,0)

    def scenario_2(self, cam, target_objects): 
        def count_values(arr,value):
            arr=np.equal(arr,value)
            arr=[x for x in arr if True==x]

            return len(arr)       
        def get_camera_angle(): #angle to middle point of objects
            a=np.random.uniform(size=2)
            angles=[11.541839481074303,16.380864048865554,20.694055318127504,22.625258981282265,24.0796678886685,25.151182765075262,26.729641520013466,29.66499068646274,32.03641319407704,37.30607393426648,66.8781015891939]
            
            i=int(a[0] * (len(angles)-1))
            if i==len(angles)-1:
                i-=1
            
            return a[1] * angles[i+1] + (1.0 - a[1]) * angles[i]
        def get_distance(): #distance nearest object to camera
            a=np.random.uniform(size=2)
            dist=[0.617447154743158,0.7079019273762083,0.7332982118619715,0.7544499287640324,0.7760178179015551,0.798877044890526,0.8346648848975794,0.859757597176487,0.8934435629251612,0.934346685094234,1.0502419872856639]

            i=int(a[0] * (len(dist)-1))
            if i==len(dist)-1:
                i-=1

            return a[1] * dist[i+1] + (1.0 - a[1]) * dist[i]
        def get_middle_point(objs):
            bpy.context.view_layer.update()
            sum=mathutils.Vector([0,0,0])

            for i in range(len(objs)):
                sum+=objs[i].matrix_world.translation

            return sum/len(objs)
        def get_y(objs, m, middle_point, dist, delta=0.01):
            y=-3

            bpy.context.view_layer.update()      
            cam.matrix_world.translation=(middle_point.x,y+middle_point.y,y*m+middle_point.z)      
            comp_dist=min([np.linalg.norm(obj.matrix_world.translation-cam.matrix_world.translation) for obj in target_objects])
            
            while np.abs(comp_dist)>np.abs(dist):
                y+=delta
                cam.matrix_world.translation=(middle_point.x,y+middle_point.y,y*m+middle_point.z)
                bpy.context.view_layer.update()
                comp_dist=min([np.linalg.norm(obj.matrix_world.translation-cam.matrix_world.translation) for obj in target_objects])
            
            return y
            """
            mid=middle_point
            
            for obj in objs:
                loc=obj.matrix_world.translation
                a=m*m+1
                b=-2.0*loc.y+2*mid.y-2*loc.z*m+2*m*mid.z
                c=-dist*dist+(loc.x-mid.x)**2+loc.y*loc.y-2*loc.y*mid.y+mid.y*mid.y+loc.z*loc.z-2*loc.z*mid.z

                if b*b-4*a*c>=0:
                    y_1=-b+np.sqrt(b*b-4*a*c)/(2*a)
                    y_2=-b-np.sqrt(b*b-4*a*c)/(2*a)

                    y=min(y,min(y_1,y_2))
            """
            return y
            
        def get_max_positive_x_rotation(cam, objs, begin_rotation_delta=math.radians(20.0), smallest_rotation_delta=math.radians(0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene

            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[1] for obj in objs]
            initial_visible_objects=count_values(np.greater(y_co_2ds,0), True)

            rotation=0
            i=0
            while rotation_delta>smallest_rotation_delta:
                cam.rotation_euler[0]+=rotation_delta
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation) for obj in objs]
                
                y_co_2ds=[x[1] for x in y_co_2ds]
                visible_ojects=count_values(np.greater(y_co_2ds,0), True)
                if visible_ojects<initial_visible_objects:
                    cam.rotation_euler[0]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def get_max_negative_x_rotation(cam, objs, begin_rotation_delta=math.radians(-20.0), smallest_rotation_delta=math.radians(-0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene

            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[1] for obj in objs]
            initial_visible_objects=count_values(np.less(y_co_2ds,1),True)

            rotation=0
            i=0
            while rotation_delta<smallest_rotation_delta:
                cam.rotation_euler[0]+=rotation_delta
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[1] for obj in objs]
                
                visible_objects=count_values(np.less(y_co_2ds,1),True)
                if visible_objects<initial_visible_objects:
                    cam.rotation_euler[0]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def get_max_positive_z_rotation(cam, objs, begin_rotation_delta=math.radians(20.0), smallest_rotation_delta=math.radians(0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene
            
            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
            initial_visible_objects=count_values(np.less(y_co_2ds,1),True)

            rotation=0
            i=0
            while rotation_delta>smallest_rotation_delta:
                cam.rotation_euler[2]+=rotation_delta
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
                
                visible_objects=count_values(np.less(y_co_2ds,1),True)
                if visible_objects<initial_visible_objects:
                    cam.rotation_euler[2]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def get_max_negative_z_rotation(cam, objs, begin_rotation_delta=math.radians(-20.0), smallest_rotation_delta=math.radians(-0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene

            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
            initial_visible_objects=count_values(np.greater(y_co_2ds,0),True)

            rotation=0
            i=0
            while rotation_delta<smallest_rotation_delta:
                cam.rotation_euler[2]+=rotation_delta
                
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
                visible_objects=count_values(np.greater(y_co_2ds,0),True)
                if visible_objects<initial_visible_objects:
                    cam.rotation_euler[2]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def look_at(cam, point):            
            bpy.context.view_layer.update()
            loc_camera = cam.matrix_world.to_translation()

            direction = point - loc_camera
            # point the cameras '-Z' and use its 'Y' as up
            rot_quat = direction.to_track_quat('-Z', 'Y')

            euler=rot_quat.to_euler()
            #euler.rotate_axis('X',np.pi)

            # assume we're using euler rotation
            cam.rotation_euler = euler

        alpha=get_camera_angle()
        rad=degree_to_radian(alpha)
        dist=get_distance()

        middle_point=get_middle_point(target_objects)
        m=-np.sin(rad)/np.cos(rad)
        if m!=0:
            m/=np.linalg.norm(m)

        y=get_y(target_objects, m, middle_point, dist)
        cam.matrix_world.translation=(middle_point.x,y+middle_point.y,y*m+middle_point.z)

        look_at(cam, middle_point)    
        
        rotation_positive_x=get_max_positive_x_rotation(cam, target_objects)
        rotation_negative_x=get_max_negative_x_rotation(cam, target_objects)
        
        rotation_positive_z=get_max_positive_z_rotation(cam, target_objects)
        rotation_negative_z=get_max_negative_z_rotation(cam, target_objects)

        rand=np.random.beta(1.2,1.2,size=2)

        rot_x=(rotation_positive_x-rotation_negative_x)*rand[0]+rotation_negative_x
        rot_z=(rotation_positive_z-rotation_negative_z)*rand[1]+rotation_negative_z

        #rot_x=np.random.uniform(rotation_negative_x,rotation_positive_x)
        #rot_z=np.random.uniform(rotation_negative_z,rotation_positive_z)

        cam.rotation_euler[0]+=rot_x
        cam.rotation_euler[2]+=rot_z

    def scenario_3(self, cam, target_objects):  #This scenario doesn't change the camera rotation or location
        bpy.context.view_layer.update()
        cam.matrix_world.translation=(0,0,1)
        cam.rotation_euler=(-np.pi/2,0,0)

        collision_ground=bpy.data.objects["CollisionGround"]
        collision_ground.matrix_world.translation=(0,-1.8,1)
        collision_ground.rotation_euler[0]=np.pi/2
        collision_ground.scale=(0.524621,0.394591,0.1435)
        bpy.context.view_layer.update()

    def scenario_4(self, cam, target_objects):  #This scenario sets the camera angle as in the synthetic samples
        bpy.context.view_layer.update()

        l=[os.path.join(BASE_PATH_TO_READ_FILES_IN,x) for x in os.listdir(BASE_PATH_TO_READ_FILES_IN) if "-meta.mat" in x]
        l.sort()

        if len(l)<=self.synthetic_sample:
            print("Too many images are created for this scenario!",file=sys.stderr)
            return

        mat=scipy.io.loadmat(l[self.synthetic_sample])

        if "rotation_translation_matrix" in mat:
            rot_trans_matrix=mat['rotation_translation_matrix']    
            rot_trans_matrix=np.array([rot_trans_matrix[0],rot_trans_matrix[1],rot_trans_matrix[2],[0,0,0,1]])
            mirror=np.asarray([[1,0,0,0],[0,-1,0,0],[0,0,-1,0],[0,0,0,1]])  #mirror z and y                    
            rot_trans_matrix=np.matmul(rot_trans_matrix,mirror)
            
            cam.matrix_world=rot_trans_matrix.transpose()
        else:
            rot_trans_matrix=np.array([[1,0,0,0],[0,-1,0,0],[0,0,-1,0],[0,0,0,1]])
            cam.matrix_world=rot_trans_matrix.transpose()

        collision_ground=bpy.data.objects["CollisionGround"]
        collision_ground.hide_render=True
        collision_ground.hide_viewport=True

        bpy.context.view_layer.update()

    def scenario_5(self, cam, target_objects):  #This scenario doesn't change the camera rotation or location
        bpy.context.view_layer.update()
        cam.matrix_world.translation=(0,0,0)
        cam.rotation_euler=(0,0,0)

        collision_ground=bpy.data.objects["CollisionGround"]
        collision_ground.matrix_world.translation=(0,0,-1.8)
        collision_ground.scale=(0.524621,0.394591,0.1435)
        bpy.context.view_layer.update()

    def scenario_6(self, cam, target_objects):  #This scenario sets the camera angle as in the synthetic samples
        bpy.context.view_layer.update()

        rot_trans_matrix=np.array([[1,0,0,0],[0,-1,0,0],[0,0,-1,0],[0,0,0,1]])
        cam.matrix_world=rot_trans_matrix.transpose()

        collision_ground=bpy.data.objects["CollisionGround"]
        collision_ground.hide_render=True
        collision_ground.hide_viewport=True

        bpy.context.view_layer.update()

    def scenario_7(self, cam, target_objects):  
        def count_values(arr,value):
            arr=np.equal(arr,value)
            arr=[x for x in arr if True==x]

            return len(arr)       
        def get_camera_angle(): #angle to middle point of objects
            return np.random.uniform(15,45)
        def get_distance(): #distance nearest object to camera
            return np.random.uniform(0.5,1.5)
        def get_middle_point(objs):
            bpy.context.view_layer.update()
            sum=mathutils.Vector([0,0,0])

            for i in range(len(objs)):
                sum+=objs[i].matrix_world.translation

            return sum/len(objs)
        def get_y(objs, m, middle_point, dist, delta=0.01):
            y=-3

            bpy.context.view_layer.update()      
            cam.matrix_world.translation=(middle_point.x,y+middle_point.y,y*m+middle_point.z)      
            comp_dist=min([np.linalg.norm(obj.matrix_world.translation-cam.matrix_world.translation) for obj in target_objects])
            
            while np.abs(comp_dist)>np.abs(dist):
                y+=delta
                cam.matrix_world.translation=(middle_point.x,y+middle_point.y,y*m+middle_point.z)
                bpy.context.view_layer.update()
                comp_dist=min([np.linalg.norm(obj.matrix_world.translation-cam.matrix_world.translation) for obj in target_objects])
            
            return y
            """
            mid=middle_point
            
            for obj in objs:
                loc=obj.matrix_world.translation
                a=m*m+1
                b=-2.0*loc.y+2*mid.y-2*loc.z*m+2*m*mid.z
                c=-dist*dist+(loc.x-mid.x)**2+loc.y*loc.y-2*loc.y*mid.y+mid.y*mid.y+loc.z*loc.z-2*loc.z*mid.z

                if b*b-4*a*c>=0:
                    y_1=-b+np.sqrt(b*b-4*a*c)/(2*a)

                    y_2=-b-np.sqrt(b*b-4*a*c)/(2*a)

                    y=min(y,min(y_1,y_2))
            """
            return y
            
        def get_max_positive_x_rotation(cam, objs, begin_rotation_delta=math.radians(20.0), smallest_rotation_delta=math.radians(0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene

            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[1] for obj in objs]
            initial_visible_objects=count_values(np.greater(y_co_2ds,0), True)

            rotation=0
            i=0
            while rotation_delta>smallest_rotation_delta:
                cam.rotation_euler[0]+=rotation_delta
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation) for obj in objs]
                
                y_co_2ds=[x[1] for x in y_co_2ds]
                visible_ojects=count_values(np.greater(y_co_2ds,0), True)
                if visible_ojects<initial_visible_objects:
                    cam.rotation_euler[0]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def get_max_negative_x_rotation(cam, objs, begin_rotation_delta=math.radians(-20.0), smallest_rotation_delta=math.radians(-0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene

            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[1] for obj in objs]
            initial_visible_objects=count_values(np.less(y_co_2ds,1),True)

            rotation=0
            i=0
            while rotation_delta<smallest_rotation_delta:
                cam.rotation_euler[0]+=rotation_delta
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[1] for obj in objs]
                
                visible_objects=count_values(np.less(y_co_2ds,1),True)
                if visible_objects<initial_visible_objects:
                    cam.rotation_euler[0]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def get_max_positive_z_rotation(cam, objs, begin_rotation_delta=math.radians(20.0), smallest_rotation_delta=math.radians(0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene
            
            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
            initial_visible_objects=count_values(np.less(y_co_2ds,1),True)

            rotation=0
            i=0
            while rotation_delta>smallest_rotation_delta:
                cam.rotation_euler[2]+=rotation_delta
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
                
                visible_objects=count_values(np.less(y_co_2ds,1),True)
                if visible_objects<initial_visible_objects:
                    cam.rotation_euler[2]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def get_max_negative_z_rotation(cam, objs, begin_rotation_delta=math.radians(-20.0), smallest_rotation_delta=math.radians(-0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene

            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
            initial_visible_objects=count_values(np.greater(y_co_2ds,0),True)

            rotation=0

            i=0
            while rotation_delta<smallest_rotation_delta:
                cam.rotation_euler[2]+=rotation_delta
                
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
                visible_objects=count_values(np.greater(y_co_2ds,0),True)
                if visible_objects<initial_visible_objects:
                    cam.rotation_euler[2]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def look_at(cam, point):            
            bpy.context.view_layer.update()
            loc_camera = cam.matrix_world.to_translation()

            direction = point - loc_camera
            # point the cameras '-Z' and use its 'Y' as up
            rot_quat = direction.to_track_quat('-Z', 'Y')

            euler=rot_quat.to_euler()
            #euler.rotate_axis('X',np.pi)

            # assume we're using euler rotation
            cam.rotation_euler = euler

        alpha=get_camera_angle()
        rad=degree_to_radian(alpha)
        dist=get_distance()

        middle_point=get_middle_point(target_objects)
        m=-np.sin(rad)/np.cos(rad)
        if m!=0:
            m/=np.linalg.norm(m)

        y=get_y(target_objects, m, middle_point, dist)
        cam.matrix_world.translation=(middle_point.x,y+middle_point.y,y*m+middle_point.z)

        look_at(cam, middle_point)    
        
        rotation_positive_x=get_max_positive_x_rotation(cam, target_objects)
        rotation_negative_x=get_max_negative_x_rotation(cam, target_objects)
        
        rotation_positive_z=get_max_positive_z_rotation(cam, target_objects)
        rotation_negative_z=get_max_negative_z_rotation(cam, target_objects)

        rand=np.random.beta(1.2,1.2,size=2)

        rot_x=(rotation_positive_x-rotation_negative_x)*rand[0]+rotation_negative_x
        rot_z=(rotation_positive_z-rotation_negative_z)*rand[1]+rotation_negative_z

        #rot_x=np.random.uniform(rotation_negative_x,rotation_positive_x)
        #rot_z=np.random.uniform(rotation_negative_z,rotation_positive_z)

        cam.rotation_euler[0]+=rot_x
        cam.rotation_euler[2]+=rot_z

    def scenario_8(self, cam, target_objects):  
        def count_values(arr,value):
            arr=np.equal(arr,value)
            arr=[x for x in arr if True==x]

            return len(arr)       
        def get_camera_angle(): #angle to middle point of objects
            a=np.random.uniform(size=2)
            angles=[11.541839481074303,16.380864048865554,20.694055318127504,22.625258981282265,24.0796678886685,25.151182765075262,26.729641520013466,29.66499068646274,32.03641319407704,37.30607393426648,66.8781015891939]
            
            i=int(a[0] * (len(angles)-1))
            if i==len(angles)-1:
                i-=1
            
            return a[1] * angles[i+1] + (1.0 - a[1]) * angles[i]
        def get_distance(): #distance nearest object to camera
            a=np.random.uniform(size=2)
            dist=[0.60,0.778997715680054,0.8011248198312799,0.8234251717531396,0.8461294714231269,0.8658597358883917,0.8961286713793072,0.9259525509736314,0.9680661198788819,1.0179310666308066,1.2]
            #instead of min = 0.6846145411143743
            #instead of max = 1.1275484875429556


            i=int(a[0] * (len(dist)-1))
            if i==len(dist)-1:
                i-=1

            return a[1] * dist[i+1] + (1.0 - a[1]) * dist[i]
        def get_middle_point(objs):
            bpy.context.view_layer.update()
            sum=mathutils.Vector([0,0,0])

            for i in range(len(objs)):
                sum+=objs[i].matrix_world.translation

            return sum/len(objs)
            
        def get_max_positive_x_rotation(cam, objs, begin_rotation_delta=math.radians(20.0), smallest_rotation_delta=math.radians(0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene

            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[1] for obj in objs]
            initial_visible_objects=count_values(np.greater(y_co_2ds,0), True)

            rotation=0
            i=0
            while rotation_delta>smallest_rotation_delta:
                cam.rotation_euler[0]+=rotation_delta
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation) for obj in objs]
                
                y_co_2ds=[x[1] for x in y_co_2ds]
                visible_ojects=count_values(np.greater(y_co_2ds,0), True)
                if visible_ojects<initial_visible_objects:
                    cam.rotation_euler[0]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def get_max_negative_x_rotation(cam, objs, begin_rotation_delta=math.radians(-20.0), smallest_rotation_delta=math.radians(-0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene

            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[1] for obj in objs]
            initial_visible_objects=count_values(np.less(y_co_2ds,1),True)

            rotation=0
            i=0
            while rotation_delta<smallest_rotation_delta:
                cam.rotation_euler[0]+=rotation_delta
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[1] for obj in objs]
                
                visible_objects=count_values(np.less(y_co_2ds,1),True)
                if visible_objects<initial_visible_objects:
                    cam.rotation_euler[0]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def get_max_positive_z_rotation(cam, objs, begin_rotation_delta=math.radians(20.0), smallest_rotation_delta=math.radians(0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene
            
            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
            initial_visible_objects=count_values(np.less(y_co_2ds,1),True)

            rotation=0
            i=0
            while rotation_delta>smallest_rotation_delta:
                cam.rotation_euler[2]+=rotation_delta
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
                
                visible_objects=count_values(np.less(y_co_2ds,1),True)
                if visible_objects<initial_visible_objects:
                    cam.rotation_euler[2]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def get_max_negative_z_rotation(cam, objs, begin_rotation_delta=math.radians(-20.0), smallest_rotation_delta=math.radians(-0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene

            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
            initial_visible_objects=count_values(np.greater(y_co_2ds,0),True)

            rotation=0

            i=0
            while rotation_delta<smallest_rotation_delta:
                cam.rotation_euler[2]+=rotation_delta
                
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
                visible_objects=count_values(np.greater(y_co_2ds,0),True)
                if visible_objects<initial_visible_objects:
                    cam.rotation_euler[2]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def look_at(cam, point):            
            bpy.context.view_layer.update()
            loc_camera = cam.matrix_world.to_translation()

            direction = point - loc_camera
            # point the cameras '-Z' and use its 'Y' as up
            rot_quat = direction.to_track_quat('-Z', 'Y')

            euler=rot_quat.to_euler()
            #euler.rotate_axis('X',np.pi)

            # assume we're using euler rotation
            cam.rotation_euler = euler

        alpha=get_camera_angle()
        rad=degree_to_radian(alpha)
        dist=get_distance()

        middle_point=get_middle_point(target_objects)
        cam.matrix_world.translation=(middle_point.x,middle_point.y-np.cos(rad)*dist,middle_point.z+np.sin(rad)*dist)

        look_at(cam, middle_point)    
        
        rotation_positive_x=get_max_positive_x_rotation(cam, target_objects)
        rotation_negative_x=get_max_negative_x_rotation(cam, target_objects)
        
        rotation_positive_z=get_max_positive_z_rotation(cam, target_objects)
        rotation_negative_z=get_max_negative_z_rotation(cam, target_objects)

        rand=np.random.beta(1.2,1.2,size=2)

        rot_x=(rotation_positive_x-rotation_negative_x)*rand[0]+rotation_negative_x
        rot_z=(rotation_positive_z-rotation_negative_z)*rand[1]+rotation_negative_z

        #rot_x=np.random.uniform(rotation_negative_x,rotation_positive_x)
        #rot_z=np.random.uniform(rotation_negative_z,rotation_positive_z)

        cam.rotation_euler[0]+=rot_x
        cam.rotation_euler[2]+=rot_z

    def scenario_9(self, cam, target_objects):  
        def count_values(arr,value):
            arr=np.equal(arr,value)
            arr=[x for x in arr if True==x]

            return len(arr)       
        def get_camera_angle(): #angle to middle point of objects
            a=np.random.uniform(size=2)
            angles=[11.541839481074303,16.380864048865554,20.694055318127504,22.625258981282265,24.0796678886685,25.151182765075262,26.729641520013466,29.66499068646274,32.03641319407704,37.30607393426648,66.8781015891939]
            
            i=int(a[0] * (len(angles)-1))
            if i==len(angles)-1:
                i-=1
            
            return a[1] * angles[i+1] + (1.0 - a[1]) * angles[i]
        def get_distance(): #distance nearest object to camera
            a=np.random.uniform(size=2)
            dist=[0.60,0.778997715680054,0.8011248198312799,0.8234251717531396,0.8461294714231269,0.8658597358883917,0.8961286713793072,0.9259525509736314,0.9680661198788819,1.0179310666308066,1.2]
            #instead of min = 0.6846145411143743
            #instead of max = 1.1275484875429556


            i=int(a[0] * (len(dist)-1))
            if i==len(dist)-1:
                i-=1

            return a[1] * dist[i+1] + (1.0 - a[1]) * dist[i]
        def get_middle_point(objs):
            bpy.context.view_layer.update()
            sum=mathutils.Vector([0,0,0])

            for i in range(len(objs)):
                sum+=objs[i].matrix_world.translation

            return sum/len(objs)
            
        def get_max_positive_x_rotation(cam, objs, begin_rotation_delta=math.radians(20.0), smallest_rotation_delta=math.radians(0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene

            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[1] for obj in objs]
            initial_visible_objects=count_values(np.greater(y_co_2ds,0), True)

            rotation=0
            i=0
            while rotation_delta>smallest_rotation_delta:
                cam.rotation_euler[0]+=rotation_delta
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation) for obj in objs]
                
                y_co_2ds=[x[1] for x in y_co_2ds]
                visible_ojects=count_values(np.greater(y_co_2ds,0), True)
                if visible_ojects<initial_visible_objects:
                    cam.rotation_euler[0]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def get_max_negative_x_rotation(cam, objs, begin_rotation_delta=math.radians(-20.0), smallest_rotation_delta=math.radians(-0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene

            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[1] for obj in objs]
            initial_visible_objects=count_values(np.less(y_co_2ds,1),True)

            rotation=0
            i=0
            while rotation_delta<smallest_rotation_delta:
                cam.rotation_euler[0]+=rotation_delta
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[1] for obj in objs]
                
                visible_objects=count_values(np.less(y_co_2ds,1),True)
                if visible_objects<initial_visible_objects:
                    cam.rotation_euler[0]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def get_max_positive_z_rotation(cam, objs, begin_rotation_delta=math.radians(20.0), smallest_rotation_delta=math.radians(0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene
            
            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
            initial_visible_objects=count_values(np.less(y_co_2ds,1),True)

            rotation=0
            i=0
            while rotation_delta>smallest_rotation_delta:
                cam.rotation_euler[2]+=rotation_delta
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
                
                visible_objects=count_values(np.less(y_co_2ds,1),True)
                if visible_objects<initial_visible_objects:
                    cam.rotation_euler[2]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def get_max_negative_z_rotation(cam, objs, begin_rotation_delta=math.radians(-20.0), smallest_rotation_delta=math.radians(-0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene

            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
            initial_visible_objects=count_values(np.greater(y_co_2ds,0),True)

            rotation=0

            i=0
            while rotation_delta<smallest_rotation_delta:
                cam.rotation_euler[2]+=rotation_delta
                
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
                visible_objects=count_values(np.greater(y_co_2ds,0),True)
                if visible_objects<initial_visible_objects:
                    cam.rotation_euler[2]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def look_at(cam, point):            
            bpy.context.view_layer.update()
            loc_camera = cam.matrix_world.to_translation()

            direction = point - loc_camera
            # point the cameras '-Z' and use its 'Y' as up
            rot_quat = direction.to_track_quat('-Z', 'Y')

            euler=rot_quat.to_euler()
            #euler.rotate_axis('X',np.pi)

            # assume we're using euler rotation
            cam.rotation_euler = euler

        alpha=get_camera_angle()
        rad=degree_to_radian(alpha)
        dist=get_distance()

        middle_point=get_middle_point(target_objects)
        cam.matrix_world.translation=(middle_point.x,middle_point.y-np.cos(rad)*dist,middle_point.z+np.sin(rad)*dist)

        look_at(cam, middle_point)    
        
        rotation_positive_x=get_max_positive_x_rotation(cam, target_objects)
        rotation_negative_x=get_max_negative_x_rotation(cam, target_objects)
        
        rotation_positive_z=get_max_positive_z_rotation(cam, target_objects)
        rotation_negative_z=get_max_negative_z_rotation(cam, target_objects)

        rand=np.random.beta(1.2,1.2,size=2)

        rot_x=(rotation_positive_x-rotation_negative_x)*rand[0]+rotation_negative_x
        rot_z=(rotation_positive_z-rotation_negative_z)*rand[1]+rotation_negative_z

        #rot_x=np.random.uniform(rotation_negative_x,rotation_positive_x)
        #rot_z=np.random.uniform(rotation_negative_z,rotation_positive_z)

        #cam.rotation_euler[0]+=rot_x
        #cam.rotation_euler[2]+=rot_z

    def scenario_10(self, cam, target_objects): 
        def count_values(arr,value):
            arr=np.equal(arr,value)
            arr=[x for x in arr if True==x]

            return len(arr)       
        def get_camera_angle(): #angle to middle point of objects
            return np.random.uniform(15,75)
        def get_distance(): #distance nearest object to camera
            return np.random.uniform(0.6,1.3)
        def get_middle_point(objs):
            bpy.context.view_layer.update()
            sum=mathutils.Vector([0,0,0])

            for i in range(len(objs)):
                sum+=objs[i].matrix_world.translation

            return sum/len(objs)
        def get_y(objs, m, middle_point, dist, delta=0.01):
            y=-3

            bpy.context.view_layer.update()      
            cam.matrix_world.translation=(middle_point.x,y+middle_point.y,y*m+middle_point.z)      
            comp_dist=min([np.linalg.norm(obj.matrix_world.translation-cam.matrix_world.translation) for obj in target_objects])
            
            while np.abs(comp_dist)>np.abs(dist):
                y+=delta
                cam.matrix_world.translation=(middle_point.x,y+middle_point.y,y*m+middle_point.z)
                bpy.context.view_layer.update()
                comp_dist=min([np.linalg.norm(obj.matrix_world.translation-cam.matrix_world.translation) for obj in target_objects])
            
            return y
            """
            mid=middle_point
            
            for obj in objs:
                loc=obj.matrix_world.translation
                a=m*m+1
                b=-2.0*loc.y+2*mid.y-2*loc.z*m+2*m*mid.z
                c=-dist*dist+(loc.x-mid.x)**2+loc.y*loc.y-2*loc.y*mid.y+mid.y*mid.y+loc.z*loc.z-2*loc.z*mid.z

                if b*b-4*a*c>=0:
                    y_1=-b+np.sqrt(b*b-4*a*c)/(2*a)
                    y_2=-b-np.sqrt(b*b-4*a*c)/(2*a)

                    y=min(y,min(y_1,y_2))
            """
            return y
            
        def get_max_positive_x_rotation(cam, objs, begin_rotation_delta=math.radians(20.0), smallest_rotation_delta=math.radians(0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene

            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[1] for obj in objs]
            initial_visible_objects=count_values(np.greater(y_co_2ds,0), True)

            rotation=0
            i=0
            while rotation_delta>smallest_rotation_delta:
                cam.rotation_euler[0]+=rotation_delta
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation) for obj in objs]
                
                y_co_2ds=[x[1] for x in y_co_2ds]
                visible_ojects=count_values(np.greater(y_co_2ds,0), True)
                if visible_ojects<initial_visible_objects:
                    cam.rotation_euler[0]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def get_max_negative_x_rotation(cam, objs, begin_rotation_delta=math.radians(-20.0), smallest_rotation_delta=math.radians(-0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene

            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[1] for obj in objs]
            initial_visible_objects=count_values(np.less(y_co_2ds,1),True)

            rotation=0
            i=0
            while rotation_delta<smallest_rotation_delta:
                cam.rotation_euler[0]+=rotation_delta
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[1] for obj in objs]
                
                visible_objects=count_values(np.less(y_co_2ds,1),True)
                if visible_objects<initial_visible_objects:
                    cam.rotation_euler[0]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def get_max_positive_z_rotation(cam, objs, begin_rotation_delta=math.radians(20.0), smallest_rotation_delta=math.radians(0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene
            
            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
            initial_visible_objects=count_values(np.less(y_co_2ds,1),True)

            rotation=0
            i=0
            while rotation_delta>smallest_rotation_delta:
                cam.rotation_euler[2]+=rotation_delta
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
                
                visible_objects=count_values(np.less(y_co_2ds,1),True)
                if visible_objects<initial_visible_objects:
                    cam.rotation_euler[2]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def get_max_negative_z_rotation(cam, objs, begin_rotation_delta=math.radians(-20.0), smallest_rotation_delta=math.radians(-0.05)): 
            original_rotation_euler=cam.rotation_euler.copy()
            rotation_delta=begin_rotation_delta

            scene=bpy.context.scene

            bpy.context.view_layer.update()
            y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
            initial_visible_objects=count_values(np.greater(y_co_2ds,0),True)

            rotation=0
            i=0
            while rotation_delta<smallest_rotation_delta:
                cam.rotation_euler[2]+=rotation_delta
                
                bpy.context.view_layer.update()
                y_co_2ds = [bpy_extras.object_utils.world_to_camera_view(scene, cam, obj.matrix_world.translation)[0] for obj in objs]
                visible_objects=count_values(np.greater(y_co_2ds,0),True)
                if visible_objects<initial_visible_objects:
                    cam.rotation_euler[2]-=rotation_delta
                    rotation_delta/=2.0
                else:
                    rotation+=rotation_delta
                
                i+=1
                if i>20:
                    break

            cam.rotation_euler=original_rotation_euler
            return rotation
        def look_at(cam, point):            
            bpy.context.view_layer.update()
            loc_camera = cam.matrix_world.to_translation()

            direction = point - loc_camera
            # point the cameras '-Z' and use its 'Y' as up
            rot_quat = direction.to_track_quat('-Z', 'Y')

            euler=rot_quat.to_euler()
            #euler.rotate_axis('X',np.pi)

            # assume we're using euler rotation
            cam.rotation_euler = euler

        alpha=get_camera_angle()
        rad=degree_to_radian(alpha)
        dist=get_distance()

        middle_point=get_middle_point(target_objects)
        m=-np.sin(rad)/np.cos(rad)
        if m!=0:
            m/=np.linalg.norm(m)

        y=get_y(target_objects, m, middle_point, dist)
        cam.matrix_world.translation=(middle_point.x,y+middle_point.y,y*m+middle_point.z)

        look_at(cam, middle_point)    
        
        rotation_positive_x=get_max_positive_x_rotation(cam, target_objects)
        rotation_negative_x=get_max_negative_x_rotation(cam, target_objects)
        
        rotation_positive_z=get_max_positive_z_rotation(cam, target_objects)
        rotation_negative_z=get_max_negative_z_rotation(cam, target_objects)

        rand=np.random.beta(1.2,1.2,size=2)

        rot_x=(rotation_positive_x-rotation_negative_x)*rand[0]+rotation_negative_x
        rot_z=(rotation_positive_z-rotation_negative_z)*rand[1]+rotation_negative_z

        #rot_x=np.random.uniform(rotation_negative_x,rotation_positive_x)
        #rot_z=np.random.uniform(rotation_negative_z,rotation_positive_z)

        cam.rotation_euler[0]+=rot_x
        cam.rotation_euler[2]+=rot_z
