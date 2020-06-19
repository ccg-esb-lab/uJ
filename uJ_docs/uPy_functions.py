import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import ScalarFormatter, FormatStrFormatter
import matplotlib.pyplot as plt
from PIL import Image


#Plotting functions
def showTIF(img_file, title='', outFile=''):
    img = plt.imread(img_file)
    imgplot = plt.imshow(img,cmap=plt.get_cmap('gray'))
    plt.axis('off')
    plt.title(title, fontsize=10)
    plt.show()
    
    
#Plotting functions
def show2TIFs(img_file1, img_file2, title1='', title2='', outFile=''):
    img1 = plt.imread(img_file1)
    #imgplot1 = plt.imshow(img1,cmap=plt.get_cmap('gray'))
    
    img2 = plt.imread(img_file2)
    #imgplot2 = plt.imshow(img2,cmap=plt.get_cmap('gray'))
    
    fig = plt.figure(figsize=(20,10))
    ax = fig.add_subplot(1, 2, 1)
    ax.axis('off')
    ax.imshow(img1,cmap=plt.get_cmap('gray'))
    ax.set_title(title1)
    #ax.autoscale(False)

    ax2 = fig.add_subplot(1, 2, 2)
    ax2.imshow(img2,cmap=plt.get_cmap('gray'))
    ax2.set_title(title2)
    ax2.axis('off')
    #ax2.autoscale(False)
    plt.show()