import bpy
import os

i=0

def decrease_face_count(file_in,file_out):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.wm.open_mainfile(filepath=file_in)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.modifier_add(type='DECIMATE')
    n_faces=bpy.context.object.modifiers['Decimate'].face_count
    
    #if n_faces<=5000:
    #    return
    
    ratio=50000.0/float(n_faces)
    bpy.context.object.modifiers['Decimate'].ratio=ratio
    bpy.ops.object.modifier_apply(modifier="Decimate")
    bpy.ops.wm.save_mainfile(filepath=file_out, compress=True)
     
def traverse_all_files(base_dir):
    files=os.listdir(base_dir)
    
    global i
    for file in files:
        path=base_dir+file
        path_out="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/partsTarget/"+file
        
        if os.path.isdir(path):
            traverse_all_files(path+"/")
        elif str(file).endswith(".blend"):
            print(str(path)+"\t"+str(i))
            decrease_face_count(path,path_out)
            i+=1
                    
if __name__=="__main__":
    base_dir="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/partsTargetOri/"
    traverse_all_files(base_dir)