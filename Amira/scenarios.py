import bpy
import numpy as np
import sys
import bpy_extras
import math
import mathutils
import os
import scipy.io
from scipy.spatial.transform import Rotation as R

#amira Script

BASE_PATH_TO_READ_FILES_IN="/home/user/Downloads"

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
        
    def change_lights_properties(self, lights):
        #self.scenario_1(lights)
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
                    
        bpy.context.scene.world.light_settings.ao_factor = 0.19 * np.random.uniform() + 0.01  # random ambient occlusion
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
   
class ObjectComposition():
    def __init__(self,index):
        self.index=index
    
    def get_object_composition(self, all_target_objects, all_distractor_objects):   #(list_of_target_objects, list_of_distractor_objects)
        #return self.scenario_1(all_target_objects, all_distractor_objects)
        return self.scenario_3(all_target_objects, all_distractor_objects)
      
      
    def scenario_1(self, all_target_objects, all_distractor_objects):   #4 - 8 uniformly distributed target objects, no distractor objects
        targets=[]
        distractors=[]
    
        n_target_obj=np.random.randint(4,8)
                
        while len(targets)<n_target_obj:
            i=np.random.randint(0,len(all_target_objects)) 
            if not list(all_target_objects)[i] in targets:   
                targets.append(list(all_target_objects)[i])  
    
        return (targets, distractors)
    
    def scenario_2(self, all_target_objects, all_distractor_objects):   #4 - 8 uniformly distributed target objects, no distractor objects
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

        mat=scipy.io.loadmat(l[self.index])
        indices=mat['cls_indexes'][0]
        indices=[int(x) for x in indices]


        for index in indices:
            targets.append(list(all_target_objects)[index-1])

        return (targets, distractors)

#own scenario

class Objects():
    def __init__(self, synthetic_sample):
        self.synthetic_sample=synthetic_sample

    def randomize_object_transforms(self, target_objs, distractor_objs):
        self.scenario_3(target_objs, distractor_objs)

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

class Camera():

    def __init__(self, synthetic_sample):
        self.synthetic_sample=synthetic_sample

    def randomize_camera_transforms(self, cam, target_objects, distractor_objects):
        self.scenario_4(cam, target_objects)

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

    def scenario_3(self, cam, target_objects):  #This scenario doesn't change the camers rotation or location
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

