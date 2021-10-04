import os
import shutil

files=[]

def grap_files(input_dir):
    n_files=0
    n_max_files=100
    
    global files
    for file in os.listdir(input_dir):
        if str(file).startswith("rgb"):
            files.append(file)
        
            n_files+=1
            
            if n_files==n_max_files:
                break

def restore_files(input_dir, output_dir):
    if not os.path.isdir(output_dir):
        grap_files(input_dir)

        os.makedirs(output_dir)
            
        global files
        for file in files:
            shutil.copy(input_dir+file,output_dir+file)
        
        files=[]

if __name__=="__main__":
    restore_files("distractor within parts in air/Output/","distractor within parts in air/RGB/")
    restore_files("distractor within parts on floor 0/Output/","distractor within parts on floor 0/RGB/")
    restore_files("distractor within parts on floor 30/Output/","distractor within parts on floor 30/RGB/")
    restore_files("distractor within parts on floor 60/Output/","distractor within parts on floor 60/RGB/")
    restore_files("distractor within parts on floor 70/Output/","distractor within parts on floor 70/RGB/")
    restore_files("distractor within parts on floor 80/Output/","distractor within parts on floor 80/RGB/")
    restore_files("distractor within parts on top of another/Output/","distractor within parts on top of another/RGB/")