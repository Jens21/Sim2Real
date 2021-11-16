import pickle
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import scipy.stats

NUMBER_OF_LINES=200
NUMBER_OF_POINTS=3000
NUMBER_OF_BINS=150

def show_single_axis(arr, axis_name):
    def reduce_number_of_elements(arr, n):
        length=min(len(arr), n)

        result=[]
        for i in range(length):
            index=round(float(i*len(arr))/float(length))
            result.append(arr[int(index)])

        return result

    arr.sort()
    arr=reduce_number_of_elements(arr, NUMBER_OF_LINES)

    print(arr)

    plt.figure()
    plt.title(axis_name)
    plt.hlines(1, min(arr)-0.05, max(arr)+0.05)  # Draw a horizontal line
    plt.eventplot(arr, orientation='horizontal', colors='red', linewidths=0.5)
    plt.tight_layout()
    plt.show()

def show_single_axis_as_distribution(arr, axis_name):
    def create_bins(arr, n_bins):

        mi=np.min(arr)-1e-5
        ma=np.max(arr)+1e-5

        begin=mi+(ma-mi)/(2*n_bins)
        end=ma-(ma-mi)/(2*n_bins)

        x=np.linspace(begin,end,n_bins)

        y=np.zeros(n_bins)

        for value in arr:
            index=int((value-mi)/float(ma-mi)*float(n_bins))
            y[index]+=1

        y/=len(arr)

        return (x,y)

    (x,y)=create_bins(arr, NUMBER_OF_BINS)

    plt.xlabel(axis_name)
    plt.ylabel('Number of samples')
    plt.plot(x, y)
    plt.show()

def show_all_axis(arr):
    np.random.shuffle(arr)
    arr=arr[0:min(len(arr),NUMBER_OF_POINTS)]

    fig=plt.figure()
    axes = plt.axes(projection="3d")

    x=[a[0] for a in arr]
    y=[a[1] for a in arr]
    z=[a[2] for a in arr]
    axes.scatter3D(x,y,z,color="red",linewidths=0.5)

    axes.set_title("3d",fontsize=14,fontweight="bold")
    axes.set_xlabel("X")
    axes.set_ylabel("Y")
    axes.set_zlabel("Z")
    plt.tight_layout()
    plt.show()

if __name__=="__main__":
    with open ('positions_syn.txt', 'rb') as fp:
        positions = pickle.load(fp)

    x=[a[0] for a in positions]
    y=[a[1] for a in positions]
    z=[a[2] for a in positions]

    show_single_axis(x,"X")
    #show_single_axis_as_distribution(x,"X")

    show_single_axis(y,"Y")
    #show_single_axis_as_distribution(y,"Y")

    show_single_axis(z,"Z")
    #show_single_axis_as_distribution(z,"Z")

    #show_all_axis(positions)