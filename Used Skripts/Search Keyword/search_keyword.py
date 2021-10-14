import os

keyword="np.random.seed"
BASE_DIR="/home/user/amira_blender_rendering/src/amira_blender_rendering"

def scan_dir(base_dir):
    for file in os.listdir(base_dir):
        path=os.path.join(base_dir,file)

        if os.path.isdir(path):
            scan_dir(path)
        else:
            f=open(path)
            try:
                content=f.read()

                if keyword in content:
                    print(path)

            except UnicodeDecodeError:
                pass

            f.close()

if __name__=="__main__":
    scan_dir(BASE_DIR)