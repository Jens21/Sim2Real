import bpy
import os
from mathutils import Vector

i=0

def decimate_selected_obj():
    bpy.ops.object.modifier_add(type='DECIMATE')
    n_faces=bpy.context.object.modifiers['Decimate'].face_count
    
    if n_faces<=5000:
        return
    
    ratio=5000.0/float(n_faces)
    bpy.context.object.modifiers['Decimate'].ratio=ratio
    bpy.ops.object.modifier_apply(modifier="Decimate")

def get_max_bound_box_length_of_selected_obj():
    ob = bpy.context.object
    ob.matrix_world.translation # or .to_translation()    
    bbox_corners = [ob.matrix_world @ Vector(corner) for corner in ob.bound_box] 
    
    min_x=10000
    min_y=10000
    min_z=10000
    
    max_x=-10000
    max_y=-10000
    max_z=-10000
    
    for corner in bbox_corners:
        if min_x>corner[0]:
            min_x=corner[0]
        if max_x<corner[0]:
            max_x=corner[0]
            
        if min_y>corner[1]:
            min_y=corner[1]
        if max_y<corner[1]:
            max_y=corner[1]
            
        if min_z>corner[2]:
            min_z=corner[2]
        if max_z<corner[2]:
            max_z=corner[2]
    
    diff_x=abs(max_x-min_x)
    diff_y=abs(max_y-min_y)
    diff_z=abs(max_z-min_z)
    
    return max(diff_x,diff_y,diff_z)

def decrease_face_count(file_in,file_out):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.import_mesh.stl(filepath=file_in)
    bpy.ops.object.select_all(action='SELECT')
    
    max_box=get_max_bound_box_length_of_selected_obj()
    if max_box>0.25 or max_box<0.08: #maximale Größe ist größer als Thunfischdose aber kleiner als pitcher base
        return        
            
    decimate_selected_obj()
    bpy.ops.export_mesh.stl(filepath=file_out)
    
    global i
    i+=1
    print(str(file_in)+"\t"+str(i))
     
def traverse_all_files(base_dir):
    files=os.listdir(base_dir)
    
    for file in files:
        path=base_dir+file
        
        if os.path.isdir(path):
            traverse_all_files(path+"/")
        elif str(file).endswith(".stl"):            
            if os.stat(path).st_size<10000000:  #file size < 10MB
                decrease_face_count(path,"/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/abcAll/abc/"+file)                
                    
if __name__=="__main__":
    base_dir="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/abcAll/STL2/"
    traverse_all_files(base_dir)