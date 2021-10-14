import numpy as np
from scipy.spatial.transform import Rotation as R
import scipy.io

mat = scipy.io.loadmat('000000-meta.mat')
mat['rotation_translation_matrix']=np.array([[1,0,0,0],[0,-1,0,0],[0,0,-1,0]])
row_to_be_added = np.array([0,0,0,1])

def print_target_objects():
	print("(Script) Target objects:")
	#targets=[list(all_target_objects)[3],list(all_target_objects)[8],list(all_target_objects)[12]]
	print("targets=[",end="")
	for i in range(len(mat['cls_indexes'][0])-1):
		print("list(all_target_objects)["+str(mat['cls_indexes'][0][i]-1)+"]",end=",")
	
	print("list(all_target_objects)["+str(mat['cls_indexes'][0][len(mat['cls_indexes'][0])-1]-1)+"]",end="")
	print("]\n\n")

def print_camera_coords():
	print("(Script) Camera coords:")
	
	R.from_matrix(np.vstack((mat['rotation_translation_matrix'], row_to_be_added))[0:3,0:3]).as_euler('xyz', degrees=True)
	mat['rotation_translation_matrix']

	print("obj.location=("+str(mat['rotation_translation_matrix'][0,3])+", "+str(mat['rotation_translation_matrix'][1,3])+", "+str(mat['rotation_translation_matrix'][2,3])+")")
	print("obj.rotation_euler=self.to_radian"+str((R.from_matrix(np.vstack((mat['rotation_translation_matrix'], row_to_be_added))[0:3,0:3]).as_euler('xyz', degrees=True)[0],R.from_matrix(np.vstack((mat['rotation_translation_matrix'], row_to_be_added))[0:3,0:3]).as_euler('xyz', degrees=True)[1],R.from_matrix(np.vstack((mat['rotation_translation_matrix'], row_to_be_added))[0:3,0:3]).as_euler('xyz', degrees=True)[2])))
	print("\n")
    
def print_obj_transforms():
    print("(Cofiguration) Object transform:")
    
    for i in range(len(mat['cls_indexes'][0])):
        rot_x=R.from_matrix(np.matmul(np.vstack((mat['rotation_translation_matrix'], row_to_be_added)),np.vstack((mat['poses'][:,:,i], row_to_be_added)))[0:3,0:3]).as_euler('xyz', degrees=True)[0]
        rot_y=R.from_matrix(np.matmul(np.vstack((mat['rotation_translation_matrix'], row_to_be_added)),np.vstack((mat['poses'][:,:,i], row_to_be_added)))[0:3,0:3]).as_euler('xyz', degrees=True)[1]
        rot_z=R.from_matrix(np.matmul(np.vstack((mat['rotation_translation_matrix'], row_to_be_added)),np.vstack((mat['poses'][:,:,i], row_to_be_added)))[0:3,0:3]).as_euler('xyz', degrees=True)[2]
		
        loc_x=np.matmul(np.vstack((mat['rotation_translation_matrix'], row_to_be_added)),np.vstack((mat['poses'][:,:,i], row_to_be_added)))[0:3,3:4][0]
        loc_y=np.matmul(np.vstack((mat['rotation_translation_matrix'], row_to_be_added)),np.vstack((mat['poses'][:,:,i], row_to_be_added)))[0:3,3:4][1]
        loc_z=np.matmul(np.vstack((mat['rotation_translation_matrix'], row_to_be_added)),np.vstack((mat['poses'][:,:,i], row_to_be_added)))[0:3,3:4][2]
        
        print("self.objs["+str(i)+"]['bpy'].location="+str((loc_x[0],loc_y[0],loc_z[0])))
        print("self.objs["+str(i)+"]['bpy'].rotation_euler=self.to_radian"+str((rot_x,rot_y,rot_z))+"\n")
    #R.from_matrix(np.matmul(np.vstack((mat['rotation_translation_matrix'], row_to_be_added)),np.vstack((mat['poses'][:,:,index], row_to_be_added)))[0:3,0:3]).as_euler('xyz', degrees=True)
    #np.matmul(np.vstack((mat['rotation_translation_matrix'], row_to_be_added)),np.vstack((mat['poses'][:,:,index], row_to_be_added)))[0:3,3:4]

    #self.objs[0]['bpy'].rotation_euler=self.to_radian(-96.62365751,  79.87079869, -17.01733387)
    #self.objs[0]['bpy'].location=(0.0619541,-0.52785544,0.35299587)
    
print_target_objects()
print_camera_coords()
print_obj_transforms()