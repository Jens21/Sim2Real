import bpy
import numpy as np

class Lights():
    def __init__(self):
        pass
        
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
   
    def scenario_2(self,lights):    #scenario parts (target, distractor) on floor
       self.scenario_1(lights)
"""
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
"""
   
class ObjectComposition():
    def __init__(self):
        pass
    
    def get_object_composition(self, all_target_objects, all_distractor_objects):   #(list_of_target_objects, list_of_distractor_objects)
        #return self.scenario_1(all_target_objects, all_distractor_objects)
        return self.scenario_2(all_target_objects, all_distractor_objects)
      
      
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