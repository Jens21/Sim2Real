import os

DIR1="/pfs/data5/home/kit/anthropomatik/yc5412/FFB6D"
DIR2="/pfs/data5/home/kit/anthropomatik/yc5412/Test/FFB6D"

def compare_files(file1,file2):
    try:
        f=open(file1)
        content1=f.read()
        f.close()

        f=open(file1)
        content2=f.read()
        f.close()

        return content1==content2
    
    except UnicodeDecodeError:
        print("Except: ",file1,file2)
    
    return True

def traverse_directory(dir1, dir2):
    l1=os.listdir(dir1)
    l2=os.listdir(dir2)

    for x in l1:
        path1=os.path.join(dir1,x)

        if  x in l2:
            path2=os.path.join(dir2,x)
            if os.path.isdir(path1):
                traverse_directory(path1,path2)
            else:
                if not compare_files(path1,path2):
                    print("Different content: ",path1)
        else:
            print("Not existent: ",path1)

    for x in l2:
        path2=os.path.join(dir2,x)

        if not x in l1:
            print("Not existent: ",path2)

            

if __name__=="__main__":
    traverse_directory(DIR1,DIR2)