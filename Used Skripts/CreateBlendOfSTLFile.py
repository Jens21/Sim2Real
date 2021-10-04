import bpy
import os

if __name__=="__main__":
    base_dir="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/partsDistractor/"
    files=os.listdir(base_dir)
    
    i=0
    for file in files:
        path_in=base_dir+str(file)
        
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        bpy.ops.import_mesh.stl(filepath=path_in)
        
        path_out=base_dir+str(file).replace(".stl",".blend")
        bpy.ops.wm.save_as_mainfile(filepath=path_out, compress=True)
        
        i+=1
        print(i)