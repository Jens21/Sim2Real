import bpy
import os

if __name__=="__main__":
    base_dir="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/partsDistractor/"
    files=os.listdir(base_dir)
    
    for file in files:
        path=base_dir+file
                
        bpy.ops.wm.open_mainfile(filepath=path)  
        
        bpy.ops.rigidbody.objects_add()
        bpy.context.object.rigid_body.mesh_source = 'FINAL'
        
        os.remove(path)
        bpy.ops.wm.save_mainfile(filepath=path, compress=True)