from PIL import Image

FILE="C:/Users/User/Desktop/Studium KIT/Bachelor/Semester VIII/Bachelorarbeit/sim2real/amira/distractor within parts in air/Output/mask_c0_s1_v0_2_0.png"
color=(0,0,0)

if __name__=="__main__":
    from PIL import Image

    im = Image.open(FILE) # Can be many different formats.
    pix = im.load()
    
    count=0
    for x in range(im.size[0]):
        for y in range(im.size[1]):
            if pix[x,y]!=color:
                count+=1
            
    print(count)