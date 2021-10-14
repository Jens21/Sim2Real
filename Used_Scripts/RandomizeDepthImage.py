import cv2
import numpy as np

def randomize_depth_image(img_depth, img_label, img_texture):
    img_texture=cv2.cvtColor(cv2.resize(img_texture, (640,480)),cv2.COLOR_BGR2GRAY)
    
    rand=np.random.uniform(0.5,1.5,img_depth.shape)
    img_depth=np.multiply(img_depth,rand).astype('uint16')
        
    max_tex=np.max(img_texture)
    min_tex=np.min(img_texture)
    
    max_depth=np.max(img_depth)
    max_value=2*max_depth#65490
    
    img_texture=np.where(img_label==0, (img_texture-min_tex)/(max_tex-min_tex)*(max_value-max_depth)+max_depth, 0).astype('uint16')
        
    result=img_depth+img_texture
    
    return result
    
if __name__=="__main__":
    img_depth=cv2.imread("/pfs/data5/home/kit/anthropomatik/yc5412/Test/001714-depth.png",cv2.IMREAD_UNCHANGED)
    img_label=cv2.imread("/pfs/data5/home/kit/anthropomatik/yc5412/Test/001714-label.png",cv2.IMREAD_UNCHANGED)
    img_texture=cv2.imread("/pfs/data5/home/kit/anthropomatik/yc5412/Test/001_0001.jpg")
    
    img_depth=randomize_depth_image(img_depth, img_label, img_texture)
    
    cv2.imwrite("/pfs/data5/home/kit/anthropomatik/yc5412/Test/001714-depthOut.png",img_depth)