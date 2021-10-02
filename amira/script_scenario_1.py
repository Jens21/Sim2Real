from datetime import datetime
starting_time=datetime.now()

import bpy
import concurrent.futures
import threading
import subprocess
import shutil
import os
import time
import numpy as np
import subprocess
#from tqdm import tqdm 
import sys  #TODO, remove me
from datetime import datetime   #TODO, remove me
import time     #TODO, remove me
import multiprocessing
import argparse
import bmesh


import sys                                                                                      #can be removed
sys.path.append("/home/kit/anthropomatik/yc5412/.conda/envs/ffb6d-venv2/lib/python3.6/site-packages/")     #TODO
#sys.path.append("/home/jens/miniconda2/lib/python2.7/site-packages/")     #TODO
from tqdm import tqdm    


lock=threading.Lock()

parser = argparse.ArgumentParser()

parser.add_argument('--THREAD_LIMIT', type=int,default=int(multiprocessing.cpu_count()), help='number of threads to use')
parser.add_argument('--RAND_SEED', type=int,default=12345, help='random seed to start from')

parser.add_argument('--DEBUG_ABRGEN', type=bool,default=False, help='If debugging of abrgen should be turned on')
parser.add_argument('--COMPOSITIONS', type=int,default=80, help='number of different compositions')
parser.add_argument('--IMAGE_COUNT', type=int,default=1, help='number of different images per composition')
#number of images = COMPOSITIONS x SCENES x VIEWS

parser.add_argument('--FORWARD_FRAMES', type=int,default=1, help='number of to forward frames')
parser.add_argument('--SCENE_TYPE', type=str,default="OwnScenarios", help='scene typ')
parser.add_argument('--MODE', type=str,default="DISTRACTOR_WITHIN_PARTS_IN_AIR", help='Number of samples to render with')

parser.add_argument('--SAMPLES', type=int,default=4, help='Number of samples to render with')

parser.add_argument('--USE_SPECIAL_DISTRIBUTION', type=bool,default=True, help='Determines of the number of target objects should follow a specific distribution')
parser.add_argument('--MIN_TARGET_OBJECTS_PER_COMPOSITION', type=int,default=3, help='Number of min target objects')
parser.add_argument('--MAX_TARGET_OBJECTS_PER_COMPOSITION', type=int,default=9, help='Number of max target objects')
parser.add_argument('--MIN_DISTRACTOR_OBJECTS_PER_COMPOSITION', type=int,default=0, help='Number min distractor objects')
parser.add_argument('--MAX_DISTRACTOR_OBJECTS_PER_COMPOSITION', type=int,default=0, help='Number max distractor objects')

#/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira
parser.add_argument('--PATH_SCENE_TEMPLATE', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/amiraEditing/scene_template.blend", help='')
parser.add_argument('--PATH_CONFIG_TEMPLATE', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/amiraEditing/config_template.cfg", help='')
parser.add_argument('--PATH_ABRGEN_FILE', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/amira_blender_rendering/scripts/abrgen", help='')
parser.add_argument('--DIR_ABRGEN_SRC', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/amira_blender_rendering/src/", help='')
parser.add_argument('--DIR_OUTPUT', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/amiraEditing/Output/", help='')
parser.add_argument('--DIR_TEMPORARY', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/amiraEditing/Temporary/", help='')
parser.add_argument('--DIR_TARGET_OBJECTS', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/partsTarget/", help='')
parser.add_argument('--DIR_DISTRACTOR_OBJECTS', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/partsDistractor/", help='')
parser.add_argument('--DIR_FLOOR_TEXTURES', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/textures/", help='')
parser.add_argument('--DIR_DISTRACTOR_TEXTURES', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/textures/", help='')

parser.add_argument('--START_AT_IMAGE_NUMBER', type=int,default=0, help='Number of image declaration to start')

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"
args=parser.parse_args(argv)

all_target_objects=dict()
all_distractor_objects=dict()

pbar_started=tqdm(total=args.COMPOSITIONS, desc="Started")
pbar_ended=tqdm(total=args.COMPOSITIONS, desc="Finished")

paths_floor_textures=os.listdir(args.DIR_FLOOR_TEXTURES)

class Worker():
    def __init__(self, composition_index):        
        self.composition_index=composition_index
      
    def run(self):
        actual_time=datetime.now()
        seconds=(actual_time-starting_time).seconds
        minutes=seconds/60
        if minutes>=25:
            return
        
        pbar_started.update()
        pbar_ended.refresh()
                
        self.create_random_composition(self.composition_index)
        print("create_random_composition: "+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me
        self.run_abrgen()
        print("run_abrgen: "+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me
        self.postprocess()
        print("postprocess: "+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me
        self.remove_tempory_files()
        print("remove_tempory_files: "+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me
        
        pbar_started.refresh()
        pbar_ended.refresh()
        print("end: "+str(datetime.now().strftime("%M:%S:%f")),file=sys.stderr)   #TODO, remove me
       
    def place_light_at_random_location_distractor_within_parts_in_air(self,obj_to_move):
        y = np.random.uniform()
        z = np.random.uniform()
        x = np.random.uniform()

        x=x*2-1
        y=y*2-1
        z=z*2-1

        obj_to_move.location.z =0.5*z+1.5
        obj_to_move.location.y =1*y+0
        obj_to_move.location.x =1*x+0

    def place_light_at_random_location_distractor_within_parts_on_floor_0(self,obj_to_move):
        y = np.random.uniform()
        z = np.random.uniform()
        x = np.random.uniform()

        x=x*2-1
        y=y*2-1
        z=z*2-1

        obj_to_move.location.z =0.5*z+1.5
        obj_to_move.location.y =1*y+0
        obj_to_move.location.x =1*x+0
        
    def place_light_at_random_location_distractor_within_parts_on_floor_30(self,obj_to_move):
        y = np.random.uniform()
        z = np.random.uniform()
        x = np.random.uniform()

        x=x*2-1
        y=y*2-1
        z=z*2-1

        obj_to_move.location.z =0.5*z+1.5
        obj_to_move.location.y =1*y+0
        obj_to_move.location.x =1*x+0
        
    def place_light_at_random_location_distractor_within_parts_on_floor_60(self,obj_to_move):
        y = np.random.uniform()
        z = np.random.uniform()
        x = np.random.uniform()

        x=x*2-1
        y=y*2-1
        z=z*2-1

        obj_to_move.location.z =0.5*z+1.5
        obj_to_move.location.y =1.5*y+0
        obj_to_move.location.x =1.5*x+0
       
    def place_light_at_random_location_distractor_within_parts_on_floor_70(self,obj_to_move):
        y = np.random.uniform()
        z = np.random.uniform()
        x = np.random.uniform()

        x=x*2-1
        y=y*2-1
        z=z*2-1

        obj_to_move.location.z =0.5*z+1.5
        obj_to_move.location.y =1.5*y+0
        obj_to_move.location.x =1.5*x+0
        
    def place_light_at_random_location_distractor_within_parts_on_floor_80(self,obj_to_move):
        y = np.random.uniform()
        z = np.random.uniform()
        x = np.random.uniform()

        x=x*2-1
        y=y*2-1
        z=z*2-1

        obj_to_move.location.z =0.5*z+1.5
        obj_to_move.location.y =1.5*y+0
        obj_to_move.location.x =1.5*x+0
        
    def place_light_at_random_location_distractor_within_parts_on_top_of_another(self,obj_to_move):
        y = np.random.uniform()
        z = np.random.uniform()
        x = np.random.uniform()

        x=x*2-1
        y=y*2-1
        z=z*2-1

        obj_to_move.location.z =0.5*z+1.5
        obj_to_move.location.y =1.5*y+0
        obj_to_move.location.x =1.5*x+0
       
    def place_light_at_random_location_distractor_within_parts(self,obj_to_move):
        y = np.random.uniform()
        z = np.random.uniform()
        x = np.random.uniform()

        x=x*2-1
        y=y*2-1
        z=z*2-1

        obj_to_move.location.z =0.5*z+1.5
        obj_to_move.location.y =1.5*y+0
        obj_to_move.location.x =1.5*x+0
      
    def remove_tempory_files(self):
        #import sys
        print("Delete file: "+str(args.DIR_TEMPORARY+"scenes/scene"+str(self.composition_index)+".blend"))
        os.remove(args.DIR_TEMPORARY+"scenes/scene"+str(self.composition_index)+".blend")    #TODO
        os.remove(args.DIR_TEMPORARY+"configs/config"+str(self.composition_index)+".cfg")
        shutil.rmtree(args.DIR_TEMPORARY+"Output"+str(self.composition_index)+"-Camera")       #TODO   
        
    def run_abrgen(self):
        #/home/jens/amira_blender_rendering/scripts/abrgen --config config.cfg --abr-path $HOME/amira_blender_rendering/src --render-mode multiview
        subprocess.run([args.PATH_ABRGEN_FILE, "--config", args.DIR_TEMPORARY+"configs/config"+str(self.composition_index)+".cfg", "--abr-path", args.DIR_ABRGEN_SRC],stdout=subprocess.DEVNULL)
        #stdout=subprocess.DEVNULL,  stderr=subprocess.DEVNULL passing supress the output
                   
    def postprocess(self):   
        def move_files(dir_from, dir_to, prefix):
            arr = os.listdir(dir_from)
            
            for f in arr:
                shutil.move(dir_from+f,dir_to+prefix+f) 
                
                
        dir_tmp_out=args.DIR_TEMPORARY+"Output"+str(self.composition_index)+"-Camera/"
        
        move_files(dir_tmp_out+"Annotations/OpenGL/", args.DIR_OUTPUT, "annot_c"+str(self.composition_index)+"_")
        move_files(dir_tmp_out+"Images/rgb/", args.DIR_OUTPUT, "rgb_c"+str(self.composition_index)+"_")
        move_files(dir_tmp_out+"Images/backdrop/", args.DIR_OUTPUT, "backdrop_c"+str(self.composition_index)+"_")
        move_files(dir_tmp_out+"Images/depth/", args.DIR_OUTPUT, "depth_c"+str(self.composition_index)+"_")
        move_files(dir_tmp_out+"Images/mask/", args.DIR_OUTPUT, "mask_c"+str(self.composition_index)+"_")
        #move_files(dir_tmp_out+"Images/mask_per_part/", args.DIR_OUTPUT, "maskPerPart_c"+str(self.composition_index)+"_")
        move_files(dir_tmp_out+"Images/range/", args.DIR_OUTPUT, "range_c"+str(self.composition_index)+"_")
        
    def change_light_color_randomly(self, obj,brightness):
        r = np.random.uniform()*brightness
        g = np.random.uniform(r/2,min(1.0,r*2))*brightness
        b = np.random.uniform(max(r,g)/2,min(r,g)*2)*brightness
        #r = np.random.uniform()
        #g = np.random.uniform()
        #b = np.random.uniform()
        
        obj.data.color=(r,g,b)
        
    def change_lights_randomly(self):
        brightness=np.random.uniform(0.5,1)
        
        for i, obj in enumerate(bpy.data.objects):
            if(obj.name.startswith('Light')):
                self.change_light_color_randomly(obj, brightness)
            
                if args.MODE=="DISTRACTOR_WITHIN_PARTS_IN_AIR":
                    self.place_light_at_random_location_distractor_within_parts_in_air(obj)
                elif args.MODE=="DISTRACTOR_WITHIN_PARTS_ON_FLOOR_0":
                    self.place_light_at_random_location_distractor_within_parts_on_floor_0(obj);
                elif args.MODE=="DISTRACTOR_WITHIN_PARTS_ON_FLOOR_30":
                    self.place_light_at_random_location_distractor_within_parts_on_floor_30(obj);
                elif args.MODE=="DISTRACTOR_WITHIN_PARTS_ON_FLOOR_60":
                    self.place_light_at_random_location_distractor_within_parts_on_floor_60(obj);
                elif args.MODE=="DISTRACTOR_WITHIN_PARTS_ON_FLOOR_70":
                    self.place_light_at_random_location_distractor_within_parts_on_floor_70(obj);
                elif args.MODE=="DISTRACTOR_WITHIN_PARTS_ON_FLOOR_80":
                    self.place_light_at_random_location_distractor_within_parts_on_floor_80(obj);
                elif args.MODE=="Distractor_Within_Parts_On_Top_Of_Another":
                    self.place_light_at_random_location_distractor_within_parts_on_top_of_another(obj);
                elif args.MODE=="DISTRACTOR_WITHIN_PARTS":
                    self.place_light_at_random_location_distractor_within_parts(obj);
                else:
                    raise ValueError("")
                
    def create_target_objects(self):
        targets=[]
        if args.MAX_TARGET_OBJECTS_PER_COMPOSITION>0:
            n_target_obj=np.random.randint(args.MIN_TARGET_OBJECTS_PER_COMPOSITION, args.MAX_TARGET_OBJECTS_PER_COMPOSITION+1)
            
            if args.USE_SPECIAL_DISTRIBUTION:
                uni=np.random.uniform()

                """
                if uni<float(50995)/float(50995+12554+2392+0+947):
                    n_target_obj=5
                elif uni<float(50995+12554)/float(50995+12554+2392+0+947):
                    n_target_obj=6
                elif uni<float(50995+12554+2392)/float(50995+12554+2392+0+947):
                    n_target_obj=7
                elif uni<float(50995+12554+2392+0)/float(50995+12554+2392+0+947):
                    n_target_obj=8
                else:
                    n_target_obj=9
                """
                """
                if uni<float(0)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_target_obj=0
                elif uni<float(0+0)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_target_obj=1
                elif uni<float(0+0+0)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_target_obj=2
                elif uni<float(0+0+0+9841)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_target_obj=3
                elif uni<float(0+0+0+9841+57207)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_target_obj=4
                elif uni<float(0+0+0+9841+57207+50995)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_target_obj=5
                elif uni<float(0+0+0+9841+57207+50995+12554)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_target_obj=6
                elif uni<float(0+0+0+9841+57207+50995+12554+2392)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_target_obj=7
                elif uni<float(0+0+0+9841+57207+50995+12554+2392+0)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_target_obj=8
                else:
                    n_target_obj=9
                """
                
                """
                #8: 19899, 5: 20047, 7: 19952, 6: 20102 distribution according to data_syn
                if uni<float(20047)/float(20047+20102+19952+19899):
                    n_target_obj=5
                elif uni<float(20047+20102)/float(20047+20102+19952+19899):
                    n_target_obj=6
                elif uni<float(20047+20102+19952)/float(20047+20102+19952+19899):
                    n_target_obj=7
                else:
                    n_target_obj=8
                """
                
                n_target_obj=np.random.randint(6,15)
                #n_target_obj=np.random.randint(4,8)
                
            while len(targets)<n_target_obj:
                i=np.random.randint(0,len(all_target_objects)) 
                if not list(all_target_objects)[i] in targets:   
                    targets.append(list(all_target_objects)[i])  
       
        return targets
        
    def create_distractor_objects(self):
        distractors=[]
        if args.MAX_DISTRACTOR_OBJECTS_PER_COMPOSITION>0:
            n_distrac_obj=np.random.randint(args.MIN_DISTRACTOR_OBJECTS_PER_COMPOSITION, args.MAX_DISTRACTOR_OBJECTS_PER_COMPOSITION+1)
            
            if args.USE_SPECIAL_DISTRIBUTION:
                uni=np.random.uniform()
                    
                if uni<float(0)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_distrac_obj=0
                elif uni<float(0+0)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_distrac_obj=1
                elif uni<float(0+0+0)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_distrac_obj=2
                elif uni<float(0+0+0+9841)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_distrac_obj=3
                elif uni<float(0+0+0+9841+57207)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_distrac_obj=4
                elif uni<float(0+0+0+9841+57207+50995)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_distrac_obj=5
                elif uni<float(0+0+0+9841+57207+50995+12554)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_distrac_obj=6
                elif uni<float(0+0+0+9841+57207+50995+12554+2392)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_distrac_obj=7
                elif uni<float(0+0+0+9841+57207+50995+12554+2392+0)/float(0+0+0+9841+57207+50995+12554+2392+0+947):
                    n_distrac_obj=8
                else:
                    n_distrac_obj=9
                
                
            while len(distractors)<n_distrac_obj:
                i=np.random.randint(0, len(all_distractor_objects)) 
                if not list(all_distractor_objects)[i] in distractors:    
                    distractors.append(list(all_distractor_objects)[i])
        
        distractors=[]
        return distractors
            
        
    def create_random_config_file(self):     
        f=open(args.PATH_CONFIG_TEMPLATE,"r")
        config_template_content=f.read()
        f.close()
        
        config_template_content=config_template_content.replace("#image_count", str(args.IMAGE_COUNT))
        config_template_content=config_template_content.replace("#blend_file", args.DIR_TEMPORARY+"scenes/scene"+str(self.composition_index)+".blend")    
        config_template_content=config_template_content.replace("#samples", str(args.SAMPLES))       
        config_template_content=config_template_content.replace("#forward_frames", str(args.FORWARD_FRAMES))
        config_template_content=config_template_content.replace("#scene_type", str(args.SCENE_TYPE))
        config_template_content=config_template_content.replace("#base_path", args.DIR_TEMPORARY+"Output"+str(self.composition_index))
        config_template_content=config_template_content.replace("#distractor_textures_dir", str(args.DIR_DISTRACTOR_TEXTURES))
        
        target_objects=self.create_target_objects()
        print("Used "+str(len(target_objects))+" target objects: "+str(target_objects[:]))   #TODO, remove me
        distractor_objects=self.create_distractor_objects()
        print("Used "+str(len(distractor_objects))+" distractor objects: "+str(distractor_objects[:]))   #TODO, remove me
        
        if len(target_objects)>0: 
            config_template_content=config_template_content.replace("#target_objects","target_objects = #target_objects")
        for i, target in enumerate(target_objects):
            config_template_content=config_template_content.replace("#parts","#parts\n"+target+"="+args.DIR_TARGET_OBJECTS+all_target_objects[target])
            config_template_content=config_template_content.replace("#target_objects","parts."+target+":1,#target_objects")
        config_template_content=config_template_content.replace(",#target_objects","")
        config_template_content=config_template_content.replace("#target_objects","")
        
        if len(distractor_objects)>0:
            config_template_content=config_template_content.replace("#distractor_objects","distractor_objects = #distractor_objects")
        for i, distractor in enumerate(distractor_objects):
            config_template_content=config_template_content.replace("#parts","#parts\n"+distractor+"="+args.DIR_DISTRACTOR_OBJECTS+all_distractor_objects[distractor])
            config_template_content=config_template_content.replace("#distractor_objects","parts."+distractor+":1,#distractor_objects")
        config_template_content=config_template_content.replace(",#distractor_objects","")
        config_template_content=config_template_content.replace("#distractor_objects","")
                    
        if args.DEBUG_ABRGEN:
            config_template_content=config_template_content.replace("#debug_enabled", "True")
            config_template_content=config_template_content.replace("#debug_save_to_blend", "True")
        else:
            config_template_content=config_template_content.replace("#debug_enabled", "False")
            config_template_content=config_template_content.replace("#debug_save_to_blend", "False")            
        
        f_w=open(args.DIR_TEMPORARY+"configs/config"+str(self.composition_index)+".cfg",'w')
        f_w.write(config_template_content)
        f_w.close()
        
    def change_floor_texture_randomly(self):
        if args.MODE!="DISTRACTOR_WITHIN_PARTS_IN_AIR":
            index=np.random.randint(len(paths_floor_textures))
            
            obj=bpy.data.objects["CollisionGround"]
            
            mat = bpy.data.materials.new(name="Random texture")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
            texImage.image = bpy.data.images.load(os.path.abspath(args.DIR_FLOOR_TEXTURES+paths_floor_textures[index]))
            mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
            mat.node_tree.nodes["Principled BSDF"].inputs['Specular'].default_value = 0.0

            # Assign it to object
            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)

    def to_radian(self,x,y,z):
        def to_rad(d):
            return d/180.0*np.pi
            
        return (to_rad(x),to_rad(y),to_rad(z))
    
    def change_camera_location_randomly(self,obj):
        if args.MODE!="DISTRACTOR_WITHIN_PARTS_IN_AIR":
            r=0
            alpha=0
                
            y_offset=0
            z_offset=0
                
            if args.MODE=="DISTRACTOR_WITHIN_PARTS_ON_FLOOR_0":
                r=1
                alpha=30*np.random.uniform()+0
            elif args.MODE=="DISTRACTOR_WITHIN_PARTS_ON_FLOOR_30":
                r=1.4
                y_offset=-0.02
                z_offset=-0.01
                alpha=30*np.random.uniform()+30
            elif args.MODE=="DISTRACTOR_WITHIN_PARTS_ON_FLOOR_60": 
                r=1.41
                y_offset=-0.06
                z_offset=-0.1
                alpha=10*np.random.uniform()+60
            elif args.MODE=="DISTRACTOR_WITHIN_PARTS_ON_FLOOR_70":
                r=1.73
                y_offset=-0.04
                z_offset=-0.15
                alpha=10*np.random.uniform()+70
            elif args.MODE=="DISTRACTOR_WITHIN_PARTS_ON_FLOOR_80": 
                r=1.86
                z_offset=0.16
                alpha=10*np.random.uniform()+80
            elif args.MODE=="Distractor_Within_Parts_On_Top_Of_Another": 
                obj.rotation_euler.x=90*np.pi/180
                obj.location.x=0.2*np.random.uniform()-0.1
                obj.location.y=0.2*np.random.uniform()-0.1-1
                obj.location.z=0.13*np.random.uniform()-0.1+0.16
                return            
            elif args.MODE=="DISTRACTOR_WITHIN_PARTS": 
                r=np.random.uniform(0.6, 1.5)    #Min:  0.6846145411143743       Max:  1.1275484875429556 
                alpha=50*np.random.uniform()+20
            else:
                raise ValueError("")
                            
            #obj.rotation_euler.x=-180*np.pi/180+alpha*np.pi/180
            #obj.location.y=-r*np.sin(alpha*np.pi/180.0)+y_offset
            #obj.location.z=r*np.cos(alpha*np.pi/180.0)+z_offset
                     
    def change_cameras_randomly(self):
        for i, obj in enumerate(bpy.data.objects):
            if(obj.name.startswith('Camera')):
                self.change_camera_location_randomly(obj)
     
    def create_random_composition(self, composition_index):
        lock.acquire()
        self.change_lights_randomly()
        self.change_cameras_randomly()
        bpy.context.scene.world.light_settings.ao_factor = 0.19*np.random.uniform()+0.01  # random ambient occlusion
        self.change_floor_texture_randomly()
        bpy.ops.wm.save_mainfile(filepath=str(args.DIR_TEMPORARY+"scenes/scene"+str(self.composition_index)+".blend"))
        
        self.create_random_config_file()
        lock.release()
        
#all_target_objects intersection all_distractor_objects = empty set
def add_all_target_objects():  
    
    all_target_objects["master_chef_can"]="002_master_chef_can.blend"
    all_target_objects["cracker_box"]="003_cracker_box.blend"
    all_target_objects["sugar_box"]="004_sugar_box.blend"
    all_target_objects["tomato_soup_can"]="005_tomato_soup_can.blend"
    all_target_objects["mustard_bottle"]="006_mustard_bottle.blend"
    all_target_objects["tuna_fish_can"]="007_tuna_fish_can.blend"
    all_target_objects["pudding_box"]="008_pudding_box.blend"
    all_target_objects["gelatin_box"]="009_gelatin_box.blend"
    all_target_objects["potted_meat_can"]="010_potted_meat_can.blend"
    all_target_objects["banana"]="011_banana.blend"
    all_target_objects["pitcher_base"]="019_pitcher_base.blend"
    all_target_objects["bleach_cleanser"]="021_bleach_cleanser.blend"
    all_target_objects["bowl"]="024_bowl.blend"
    all_target_objects["mug"]="025_mug.blend"
    all_target_objects["power_drill"]="035_power_drill.blend"
    all_target_objects["wood_block"]="036_wood_block.blend"
    all_target_objects["scissors"]="037_scissors.blend"
    all_target_objects["large_marker"]="040_large_marker.blend"
    all_target_objects["large_clamp"]="051_large_clamp.blend"
    all_target_objects["extra_large_clamp"]="052_extra_large_clamp.blend"
    all_target_objects["foam_brick"]="061_foam_brick.blend"
    """
    all_target_objects["cube"]="cube.blend"
    all_target_objects["torus"]="torus.blend"
    all_target_objects["monkey"]="monkey.blend"
    all_target_objects["sphere"]="sphere.blend"
    all_target_objects["cone"]="cone.blend"
    all_target_objects["cylinder"]="cylinder.blend"
    """
    
#all_target_objects intersection all_distractor_objects = empty set
def add_all_distractor_objects():
    base_path=args.DIR_DISTRACTOR_OBJECTS
    files=os.listdir(base_path)
    
    for i,file in enumerate(files):
        all_distractor_objects[str(file).replace(".blend","")]=str(file)

if __name__=='__main__':
    print("THREAD_LIMIT="+str(args.THREAD_LIMIT))

    np.random.seed(args.RAND_SEED+args.START_AT_IMAGE_NUMBER) #important to know

    os.makedirs(args.DIR_OUTPUT, exist_ok=True)
    os.makedirs(args.DIR_TEMPORARY, exist_ok=True)
    os.makedirs(args.DIR_TEMPORARY+"scenes", exist_ok=True)
    os.makedirs(args.DIR_TEMPORARY+"configs", exist_ok=True)
        
    add_all_target_objects()
    add_all_distractor_objects()
                
    bpy.ops.wm.open_mainfile(filepath=str(args.PATH_SCENE_TEMPLATE))     #This has to be done here
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.THREAD_LIMIT) as executor:
        for comp_index in range(args.COMPOSITIONS):
            executor.submit(Worker(comp_index+args.START_AT_IMAGE_NUMBER).run)
    #Worker(0).run()
    
    pbar_started.close()
    pbar_ended.close()
    
    #shutil.rmtree(args.DIR_TEMPORARY) 
