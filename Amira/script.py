from datetime import datetime
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
from datetime import datetime   #TODO, remove me
import time     #TODO, remove me
import multiprocessing
import argparse
import bmesh

import sys                                                                                      
sys.path.append("/home/kit/anthropomatik/yc5412/.conda/envs/ffb6d-venv2/lib/python3.6/site-packages/")     #TODO
#sys.path.append("/home/user/.local/lib/python3.8/site-packages/")     #TODO
sys.path.append(os.getcwd()+"/")
from tqdm import tqdm    
import scenarios


starting_time=datetime.now()

lock=threading.Lock()

parser = argparse.ArgumentParser()

parser.add_argument('--THREAD_LIMIT', type=int,default=int(multiprocessing.cpu_count()), help='number of threads to use')

parser.add_argument('--DEBUG_ABRGEN', type=bool,default=False, help='If debugging of abrgen should be turned on')
parser.add_argument('--COMPOSITIONS', type=int,default=80, help='number of different compositions')
parser.add_argument('--IMAGE_COUNT', type=int,default=1, help='number of different images per composition')
#number of images = COMPOSITIONS x SCENES x VIEWS

parser.add_argument('--FORWARD_FRAMES', type=int,default=1, help='number of to forward frames')
parser.add_argument('--SCENE_TYPE', type=str,default="OwnScenarios", help='scene typ')
parser.add_argument('--MODE', type=str,default="DISTRACTOR_WITHIN_PARTS_IN_AIR", help='Number of samples to render with')

parser.add_argument('--SAMPLES', type=int,default=4, help='Number of samples to render with')

#/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira
parser.add_argument('--PATH_SCENE_TEMPLATE', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/amiraEditing/scene_template.blend", help='')
parser.add_argument('--PATH_CONFIG_TEMPLATE', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/amiraEditing/config_template.cfg", help='')
parser.add_argument('--PATH_ABRGEN_FILE', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/amira_blender_rendering/scripts/abrgen", help='')
parser.add_argument('--DIR_ABRGEN_SRC', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/amira_blender_rendering/src/", help='')
parser.add_argument('--DIR_OUTPUT', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/amiraEditing/Output/", help='')
parser.add_argument('--DIR_TEMPORARY', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/amiraEditing/Temporary/", help='')
parser.add_argument('--DIR_TARGET_OBJECTS', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/partsTarget/", help='')
parser.add_argument('--DIR_DISTRACTOR_OBJECTS', type=str,default="", help='')
parser.add_argument('--DIR_FLOOR_TEXTURES', type=str,default="", help='')
parser.add_argument('--DIR_DISTRACTOR_TEXTURES', type=str,default="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/textures/", help='')

parser.add_argument('--START_AT_IMAGE_NUMBER', type=int,default=0, help='Number of image declaration to start')

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"
args=parser.parse_args(argv)

all_target_objects=dict()
all_distractor_objects=dict()

#pbar_started=tqdm(total=args.COMPOSITIONS, desc="Started")
pbar_ended=tqdm(total=args.COMPOSITIONS, desc="Finished")

paths_floor_textures=os.listdir(args.DIR_FLOOR_TEXTURES)

class Worker():
    def __init__(self, composition_index):        
        self.composition_index=composition_index
      
    def run(self):
        #to make sure, the process takes at max. 25 min
        actual_time=datetime.now()
        seconds=(actual_time-starting_time).seconds
        minutes=seconds/60
        #if minutes>=25:
        #    return
        
        #updates the display progress bar
        #pbar_started.update()
        #pbar_ended.refresh()
        
        #creates a scene, runs the blender rending framework, postprocesses the created files and removes the temporary files afterwards
        try:
            self.create_random_composition(self.composition_index)
            self.run_abrgen()
            self.postprocess()
            self.remove_tempory_files()
        except:
            print("Generator Exit",file=sys.stderr)
        
        #updates the display progress bar
        #pbar_started.refresh()
        pbar_ended.update()
     
    def create_random_composition(self,composition_index):
        def change_lights_randomly():            
            lights=[]
            
            for i, obj in enumerate(bpy.data.objects):
                if(obj.name.startswith('Light')):
                    lights.append(obj)
                  
            scenarios.Lights(composition_index).change_lights_properties(lights)
          
        def change_floor_texture_randomly():
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

        def create_random_config_file(self,composition_index):     
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
            config_template_content=config_template_content.replace("#synthetic_sample", str(composition_index))
            
            obj_composition=scenarios.ObjectComposition(composition_index).get_object_composition(all_target_objects, all_distractor_objects)
            
            if obj_composition==None:
                raise GeneratorExit("The object composition isn't valid")

            target_objects=obj_composition[0]
            distractor_objects=obj_composition[1]
            
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
     
        lock.acquire()
        change_lights_randomly()
        change_floor_texture_randomly()
        bpy.ops.wm.save_mainfile(filepath=str(args.DIR_TEMPORARY+"scenes/scene"+str(self.composition_index)+".blend"))
        
        create_random_config_file(self, composition_index)
        lock.release()
        
    def run_abrgen(self):
        #/home/jens/amira_blender_rendering/scripts/abrgen --config config.cfg --abr-path $HOME/amira_blender_rendering/src
        subprocess.run([args.PATH_ABRGEN_FILE, "--config", args.DIR_TEMPORARY+"configs/config"+str(self.composition_index)+".cfg", "--abr-path", args.DIR_ABRGEN_SRC],stdout=subprocess.DEVNULL)
    
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
    
    def remove_tempory_files(self):
        os.remove(args.DIR_TEMPORARY+"scenes/scene"+str(self.composition_index)+".blend")
        os.remove(args.DIR_TEMPORARY+"configs/config"+str(self.composition_index)+".cfg")
        shutil.rmtree(args.DIR_TEMPORARY+"Output"+str(self.composition_index)+"-Camera")
    
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
    
#all_target_objects intersection all_distractor_objects = empty set
def add_all_distractor_objects():
    base_path=args.DIR_DISTRACTOR_OBJECTS
    
    if os.path.isdir(base_path):
        files=os.listdir(base_path)
        
        for i,file in enumerate(files):
            all_distractor_objects[str(file).replace(".blend","")]=str(file)

if __name__=='__main__':
    print("THREAD_LIMIT="+str(args.THREAD_LIMIT))

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
    #for comp_index in range(args.COMPOSITIONS):
    #	Worker(comp_index+args.START_AT_IMAGE_NUMBER).run()
    
    #pbar_started.close()
    pbar_ended.close()
    
    #shutil.rmtree(args.DIR_TEMPORARY) 
