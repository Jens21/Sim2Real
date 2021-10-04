import os

if __name__=="__main__":
    base_path="/pfs/data5/home/kit/anthropomatik/yc5412/sim2Real/amira/distractorParts/para/"
    
    files=os.listdir(base_path)
    for i,file in enumerate(files):
        folder=base_path+str(file)
        
        #print(str(i)+"\t"+str(file))
        
        for l in os.listdir(folder):
            if str(l).endswith(".x_t"):
                if "bearings" in l:
                    print("bearings\t"+str(file))
                    break
                elif "sprocket" in l:
                    print("sprocket\t"+str(file))
                    break
                elif "spring" in l:
                    print("spring\t"+str(file))
                    break
                elif "flange" in l:
                    print("flange\t"+str(file))
                    break
                elif "bracket" in l:
                    print("bracket\t"+str(file))
                    break
                elif "collet" in l:
                    print("collet\t"+str(file))
                    break
                elif "pipe" in l:
                    print("pipe\t"+str(file))
                    break
                elif "pipe_fitting" in l:
                    print("pipe_fitting\t"+str(file))
                    break
                elif "pipe_joint" in l:
                    print("pipe_joint\t"+str(file))
                    break
                elif "bushing" in l:
                    print("bushing\t"+str(file))
                    break
                elif "roller" in l:
                    print("roller\t"+str(file))
                    break
                elif "busing_liner" in l:
                    print("busing_liner\t"+str(file))
                    break
                elif "shaft" in l:
                    print("shaft\t"+str(file))
                    break
                elif "bolt" in l:
                    print("bolt\t"+str(file))
                    break
                elif "headless_screw" in l:
                    print("headless_screw\t"+str(file))
                    break
                elif "flat_screw" in l:
                    print("flat_screw\t"+str(file))
                    break
                elif "hex_screw" in l:
                    print("hex_screw\t"+str(file))
                    break
                elif "socket_screw" in l:
                    print("socket_screw\t"+str(file))
                    break
                elif "nut" in l:
                    print("nut\t"+str(file))
                    break
                elif "push_ring" in l:
                    print("push_ring\t"+str(file))
                    break
                elif "retaining_ring" in l:
                    print("retaining_ring\t"+str(file)) 
                    break               