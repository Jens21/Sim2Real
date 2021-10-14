import os
from PIL import Image

def convert_images_to_jpeg(direc):

    for file in os.listdir(direc):
        im = Image.open(direc+file)
        os.remove(direc+file)
        rgb_im = im.convert('RGB')
        rgb_im.save(direc+str(file).replace(".png",".jpg"))

if __name__=="__main__":
    #convert_images_to_jpeg("C:/Users/User/Desktop/Studium KIT/Bachelor/Semester VIII/Bachelorarbeit/sim2real/amira/AllOutputs/Test/")
    convert_images_to_jpeg("C:/Users/User/Desktop/Studium KIT/Bachelor/Semester VIII/Bachelorarbeit/sim2real/amira/AllOutputs/Air/")
    convert_images_to_jpeg("C:/Users/User/Desktop/Studium KIT/Bachelor/Semester VIII/Bachelorarbeit/sim2real/amira/AllOutputs/0/")
    convert_images_to_jpeg("C:/Users/User/Desktop/Studium KIT/Bachelor/Semester VIII/Bachelorarbeit/sim2real/amira/AllOutputs/30/")
    convert_images_to_jpeg("C:/Users/User/Desktop/Studium KIT/Bachelor/Semester VIII/Bachelorarbeit/sim2real/amira/AllOutputs/60/")
    convert_images_to_jpeg("C:/Users/User/Desktop/Studium KIT/Bachelor/Semester VIII/Bachelorarbeit/sim2real/amira/AllOutputs/70/")
    convert_images_to_jpeg("C:/Users/User/Desktop/Studium KIT/Bachelor/Semester VIII/Bachelorarbeit/sim2real/amira/AllOutputs/80/")
    convert_images_to_jpeg("C:/Users/User/Desktop/Studium KIT/Bachelor/Semester VIII/Bachelorarbeit/sim2real/amira/AllOutputs/On Top/")