import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os
import sys
import pathlib
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.patches as patches
import scipy.stats as st
from IPython.display import HTML, display
from IPython.display import set_matplotlib_formats





#from DataManagers import *

def get_this_path(this_df,cellID_inis,cellID_finals):
    paths_list=[]
    for cellID_ini,cellID_final in zip(cellID_inis,cellID_finals):
        
        this_id=cellID_final
        this_paths=[cellID_final]
        frame=int(cellID_final.split(".")[0])
        while(this_id!=cellID_ini):
            sub_df=this_df[(this_df['cellID']==this_id)&(this_df['motherID']!=this_id)]
            mothers=sub_df.motherID.unique()
            tracks=sub_df.trackID.unique()
            track=tracks[0]
            sub_df=this_df[(this_df['trackID']==track)&(this_df['frame']<frame)]
            this_ids=sub_df.cellID.tolist()
            
            this_paths=this_ids+this_paths
            this_id=mothers[0]
            frame=int(this_id.split(".")[0])
        
        paths_list.append(this_paths)
    return paths_list



def fromFileData(fileName):
    #d = np.loadtxt(fileName, delimiter="\t")
    
    f = open(fileName,'r')

    data = []
    numCells=0
    for line in f.readlines():
        if numCells>0:
            data.append(line.replace('\n','').split('\t'))
        numCells=numCells+1
    f.close()

    return data

#Returns a list with index of data_frame in array(t)
def filterFrames(data_frame, t):
    i=0
    ret=[]
    for this_data in data_frame:
        if this_data in t:
            ret.append(i)
        i=i+1
    return ret

def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return idx


def toFileData(fileName, row_data):
    f = open(fileName, 'w')
    f.write("id\timageGFP\timageDsRed\tpos\tframe\troi_label\tGFP\tDsRed\trelativeIntensity\tabsoluteIntensity")
    
    for row in row_data:
        str_row="\t".join(map(str,row))
        f.write("\n%s"%str_row)
    f.close()
    
    


def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(phi, rho)

def pol2cart(phi,rho):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)


def loadData(dataPath):

    data_pos=[]
    data_frame=[]
    data_GFP=[]
    data_DsRed=[]

    loaded_frames=0;
    for root, dirs, files in os.walk(dataPath):
        path = root.split(os.sep)
        for file in files:

            extension=""
            if len(os.path.splitext(file))>0:
                extension=pathlib.Path(file).suffix
            filePath = os.path.join(root,file)

            if extension == ".txt":
                #print("Loading data from: " + file)

                data=fromFileData(filePath)

                this_pos=[roi[4] for roi in data]
                this_t=[float(roi[5]) for roi in data]
                this_GFP=[float(roi[7]) for roi in data]
                this_DsRed=[float(roi[8]) for roi in data]

                data_pos.extend(this_pos)
                data_frame.extend(this_t)
                data_GFP.extend(this_GFP)
                data_DsRed.extend(this_DsRed)
                loaded_frames+=1

    data_frame=np.asarray(data_frame)
    data_GFP=np.asarray(data_GFP)
    data_DsRed=np.asarray(data_DsRed)
    
    return [data_pos, data_frame, data_GFP, data_DsRed, loaded_frames]

#Returns a list with index of data_frame in array(pos)
def filterPos(data_pos, pos):
    i=0
    ret=[]
    for this_data in data_pos:
        if this_data==pos:
            ret.append(i)
        i=i+1
    return ret


def get_long_lineages(this_cells,identifier, minFrames):
    complete_cells=[]
    identifier_list=[]
    for this_cell in this_cells:
        this_id=this_cell[identifier]
        identifier_list.append(this_id)
    identifier_list=list(set(identifier_list))
    #print(identifier_list)
    for identifierID  in identifier_list:
        for this_cell in this_cells:
            if identifierID==this_cell[identifier]:
                if len(this_cell['roiFrames'])>minFrames:
                    complete_cells.append(this_cell)
        
    return complete_cells

def get_analysis_lineages(this_cells,an_start,an_end,identifier):
    
    complete_cells=[]
    inif=an_start
    endf=an_end
    identifier_list=[]
    for this_cell in this_cells:
        this_id=this_cell[identifier]
        identifier_list.append(this_id)
    identifier_list=list(set(identifier_list))
    
    #print(inif,endf)
    to_pass=[]
    for identifierID  in identifier_list:
        for this_cell in this_cells:
            if identifierID==this_cell[identifier]:
                this_frames=this_cell['roiFrames']
        
                if(inif in this_frames and endf in this_frames) :
                    to_pass.append(identifierID)
    
    to_pass=list(set(to_pass))
    #print(to_pass)
    for this_cell in this_cells:
        #for identifierID  in to_pass:
        
            #if identifierID==this_cell[identifier]:
        if this_cell[identifier] in to_pass:
            #print(this_cell[identifier],end=",")
            complete_cells.append(this_cell)
    
    return complete_cells



print("> Analysis Functions loaded")