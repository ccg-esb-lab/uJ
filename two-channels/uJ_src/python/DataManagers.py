
import sys
import os
import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
import matplotlib.patches as patches
from shapely.geometry import Point
from shapely.geometry import MultiPoint
from shapely.geometry import MultiPolygon
from shapely.geometry import Polygon
from shapely.geometry import box
from descartes.patch import PolygonPatch
import ipywidgets as widgets
import ipywidgets.widgets.interaction
#from ipywidgets import interactive, fixed
from ipywidgets import *
import random
import pandas as pd

import re

from shapely import geometry
import pickle
import time

from ipyparallel import Client

from shapely import affinity
from shapely.geometry import LineString
import warnings
warnings.simplefilter('ignore', np.RankWarning)



from readroi import *
from DataStructs import *


print("DataManagers...",end='')

def create_cells(num_frame, this_data_file, frame_roiIDs, frame_rois, frame_axis, frame_center,frame_exp_start):
    this_cells=[]
    df = pd.read_csv(this_data_file,sep='\t')
    
    
    for j,this_roi in enumerate(frame_rois):
        
        this_roiPoly=frame_rois[j]
        this_roiID=frame_roiIDs[j]
        this_axis=frame_axis[j]
        this_center=frame_center[j]
        
        
        data_row=df.loc[df['roi_label'] == this_roiID]
        
        if not data_row.empty:
            this_GFP=float(data_row['GFP'])
            this_DsRed=float(data_row['DsRed'])
            this_RelInt=float(data_row['relativeIntensity'])
            this_AbslInt=float(data_row['absoluteIntensity'])
        else:
            print("Roi not found! <%s>\n data file: %s ,%s "%(this_roiID,this_data_file,num_frame))
            return 0
        jn=str(j).zfill(3)
        cell_id='%s.%s'%(num_frame+frame_exp_start,jn)
            
        this_cell=new_cell(cell_id)
            
            
        #print("%s: %s"%(this_roiID, this_axis.length))
        add_info_cell(this_cell, this_roiID, this_roiPoly, this_axis, this_center,this_GFP, this_DsRed, this_RelInt,this_AbslInt)    
        
        this_cells.append(this_cell)
        
        if(False):
            fig=plt.figure(figsize=(10,10))
            ax = plt.axes()    
            ax.set_aspect('equal')
            plt.axis('off')
            ax.clear()
            patch = PolygonPatch(this_roi, facecolor=[0.75,0.75,0.75], edgecolor=[0,0,0], alpha=0.3, zorder=2)
            ax.add_patch(patch)
                
            linexy=np.array(this_axis)
            linex=linexy[:,0]
            liney=linexy[:,1]
            ax.plot(linex,liney,'g-')
            
            ax.plot(this_center.x, this_center.y,'ok')
            
            plt.show()
            
    
    return this_cells









def get_unserialized_cell(str_cell):
    str_cell=re.split(r'\t+', str_cell.rstrip('\t'))
    
    this_cell=new_cell(str_cell[0])
    this_cell['cellColor']=str_cell[1]
    this_cell['roiID']=str_cell[2]
    
    trackIDs=re.sub(r'\[|\]|\'','',str_cell[3])
    trackIDs=trackIDs.split()
    this_cell['trackID']=trackIDs

    
    #roiPoly=[]
    
    roiCoords=str_cell[4].split('], [')
    for i, p in enumerate(roiCoords):
        ps=p.split('), (')
        exterior_coords=[]
        for pj in ps:
            p1=re.findall("\d+\.\d+", pj.split(',')[0])[0]
            p2=re.findall("\d+\.\d+", pj.split(',')[1])[0]
            exterior_coords.append(Point(float(p1),float(p2)))
        #roiPoly.append(geometry.Polygon([[p.x, p.y] for p in exterior_coords]))
        roiPoly=(geometry.Polygon([[p.x, p.y] for p in exterior_coords]))
        
    this_cell['roiPoly']=roiPoly
    
    c1=float(re.findall("\d+\.\d+", str_cell[5].split(',')[0])[0])
    c2=float(re.findall("\d+\.\d+", str_cell[5].split(',')[1])[0])
    this_cell['center']= Point(c1, c2)
    
    #roiLine=[]
    roiLine=LineString()  #??????
    lineCoords=str_cell[6].split('], [')
    for i, p in enumerate(lineCoords):
        ps=p.split('), (')
        exterior_coords=[]
        for pj in ps:
            p1=re.findall("\d+\.\d+", pj.split(',')[0])[0]
            p2=re.findall("\d+\.\d+", pj.split(',')[1])[0]
            exterior_coords.append(Point(float(p1),float(p2)))
        #roiLine.append(geometry.LineString([[p.x, p.y] for p in exterior_coords]))
        roiLine=geometry.LineString([[p.x, p.y] for p in exterior_coords])
    this_cell['axis']=roiLine  #not ok
    
    this_cell['GFP']=float(str_cell[7])
    this_cell['DsRed']=float(str_cell[8])
    this_cell['RelInt']=float(str_cell[9])
    this_cell['AbsInt']=float(str_cell[10])
    
    
    tr_prev=re.sub(r'\[|\]|\'|,','',str_cell[11])
    tr_prev=tr_prev.split()
    this_cell['trackedBy_previous_frame']=tr_prev
    
    tr_next=re.sub(r'\[|\]|\'|,','',str_cell[12])
    tr_next=tr_next.split()
    this_cell['trackedBy_next_frame']=tr_next
    
    
    this_cell['motherID']=str_cell[13]
    
    return this_cell


def get_serialized_cell(this_cell):
    cellID=this_cell['cellID']
    cellColor=this_cell['cellColor']
    roiID=this_cell['roiID']
    trackID=this_cell['trackID']
    #roiFrames=this_cell['roiFrames']
    roiFrames=[]

    roiPoly=list(this_cell['roiPoly'].exterior.coords)
    
    center="(%s,%s)"%(this_cell['center'].x, this_cell['center'].y)   #If list?
    axis=list(this_cell['axis'].coords) #If list?
    GFP=this_cell['GFP']    
    DsRed=this_cell['DsRed']
    RelInt=this_cell['RelInt']
    AbsInt=this_cell['AbsInt']
    trackedBy_previous=this_cell['trackedBy_previous_frame']
    trackedBy_next=this_cell['trackedBy_next_frame']
    mother_ID=this_cell['motherID']
    
    #          0   1   2   3   4  5  6    7   8   9  10  11  12   13       0         1        2      3        4       5       6     7    8      9       10             11              12          13
    str_cell="%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s"%(cellID, cellColor, roiID, trackID, roiPoly, center, axis, GFP, DsRed, RelInt, AbsInt,trackedBy_previous, trackedBy_next,mother_ID)
    
    return str_cell


 
###############################################################################################trackingfunctions


def load_frame(fileName):
    rois_zip=read_roi_zip(fileName)
    rois=[]
    roiIDs=[]
    for key, value in rois_zip.items():
        this_x=value['x']
        this_y=value['y']

        coords=zip(this_x, this_y)
        this_roi = Polygon((coords))
        this_roiID= value['name']
        rois.append(this_roi)
        roiIDs.append(this_roiID)
    return [rois,roiIDs]

def load_rois(dirNameROIs):
    #fileNames=os.listdir(dirNameROIs)
    #filter(lambda k: '.zip' in k, fileNames)
    fileNames= list(f for f in os.listdir(dirNameROIs) if f.endswith('.zip'))
    fileNames.sort()
    
    return fileNames





def save_cells(this_cells, fileNameFrameCells):  
    
    print("Saving %s cells to %s"%(len(this_cells),fileNameFrameCells))
    serialized_cells=[]
    for this_cell in this_cells:
        serialized_cells.append(get_serialized_cell(this_cell))
    
        
    fileObject = open(fileNameFrameCells,'wb') 
    pickle.dump(serialized_cells,fileObject)   
    fileObject.close()
    


def save_tracked_cells(cells, fileName):
    serialized_cells=[]
    for this_cell in cells:
        serialized_cells.append(get_serialized_cell(this_cell))

    fileObject = open(fileName,'wb') 
    pickle.dump(serialized_cells,fileObject)   
    fileObject.close()
    

def load_this_cells(fileName):

    fileObject = open(fileName,'rb')  
    serialized_cells = pickle.load(fileObject)  

    loaded_cells=[]
    for this_serialized_cell in serialized_cells:
        loaded_cells.append(get_unserialized_cell(this_serialized_cell))
        
    return loaded_cells


   
    
def load_cells(dirNameFRAMECELLS, max_frames=-1):  
    ret_cells=[]
    fileNames= list(f for f in os.listdir(dirNameFRAMECELLS) if f.endswith('.pkl'))
    fileNames.sort()
    
    if max_frames<0:
        max_frames=len(fileNames)
    
    for i, this_file in enumerate(fileNames[0:max_frames]):
        print('%s: Loading %s'%(i,this_file),end='\r')
        ret_cells.append(load_this_cells("%s%s"%(dirNameFRAMECELLS,this_file)))
    print()    
    return ret_cells
    

def load_data_files(dirNameDATA):
    fileNames=os.listdir(dirNameDATA)
    filter(lambda k: 'zip' in k, fileNames)
    fileNames.sort()
    return fileNames






def load_data_lineages(fileName):
    #df_lineages = pd.read_csv(fileName,dtype=object)
    df_lineages = pd.read_csv(fileName)
    print('Loading %s lineages from %s'%(len(df_lineages.lineageID.unique()), fileName))
    return df_lineages
                

    
    
def save_data_lineages(cell_lineages, lineagesDataFile):
    
    with open(lineagesDataFile, "w") as file:
        print("Saving file %s"%(lineagesDataFile))
        header='lineageID,trackID,cellID,motherID,frame,roiID,length,division,dead,GFP,DsRed,RelInt,AbsInt\n'
        file.write(header)
        i=0
        for this_lineage in cell_lineages:
        #    try:
                print(i,round(i/len(cell_lineages)*100,3)," %",end='\r')
                
                this_trackID='%s'%(this_lineage['trackID'])
                this_lineageID='%s'%(this_lineage['lineageID'])
                
                #this_motherID=this_lineage['motherID'][0]  #????????????????
                this_motherID=this_lineage['motherID']
                #print(this_lineageID,this_trackID,i,round(i/len(cell_lineages)*100,3)," %",end='\r')
                #print(" ",end="\r")
                for frame in range(0,len(this_lineage['roiFrames'])):
                    #print(frame,end=", ")
                    this_cellID=this_lineage['cellIDs'][frame]
                    this_roiID=this_lineage['roiID'][frame]
                    this_frame=this_lineage['roiFrames'][frame]
                    this_length=this_lineage['axis'][frame].length

#                     this_division=0
#                     if frame<len(this_lineage['roiFrames'])-1:
#                         if 0.6*this_length>this_lineage['axis'][frame+1].length: #Division event
#                             this_division=1

                    this_division=this_lineage['divisions'][frame]
                    this_GFP=this_lineage['GFP'][frame]
                    this_DsRed=this_lineage['DsRed'][frame]
                    this_RelInt=this_lineage['RelInt'][frame]
                    this_AbsInt=this_lineage['AbsInt'][frame]
                    death=this_lineage['dead'][frame]
                    line='%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n'%(this_lineageID,this_trackID,this_cellID, this_motherID, this_frame,this_roiID, this_length, this_division,death, this_GFP, this_DsRed, this_RelInt,this_AbsInt)
                    file.write(line)
                i=i+1
         #   except TypeError:
          #      continue
    file.close()   
    
    
    ##############################


def export_frame(cells, frame, dirNameROI, fileNames, fileNameTracked):
    fig=plt.figure(figsize=(10,10))
    ax = plt.axes()
    ax.set_aspect('equal')
    plt.xlim(0,640)
    plt.ylim(0,512)
    plt.axis('off')
    #ax.clear()
    
    [rois,roiIDs]=load_frame('%s%s'%(dirNameROI,fileNames[frame]))
    
    for i, this_roi in enumerate(rois):
        patch = PolygonPatch(this_roi, facecolor=[0.75,0.75,0.75], edgecolor=[0,0,0], alpha=0.3, zorder=2)
        ax.add_patch(patch)
        
    for this_cell in cells[frame]:
        #print('Frame=%s: cellID=%s trackID=%s'%(frame, this_cell['cellID'],this_cell['trackID']))
        if len(this_cell['trackID'])>0:
            this_patch = PolygonPatch(this_cell['roiPoly'], facecolor=this_cell['cellColor'], edgecolor=[0.2,0.2,0.2], alpha=0.3, zorder=3)
            ax.add_patch(this_patch)
        #iframe=this_cell['roiFrames'].index(frame-1) if (frame-1) in this_cell['roiFrames'] else -1
        #if iframe>=0:
            #print('Drawing cell %s at frame %s'%(this_cell['cellID'],frame))
        #    this_patch = PolygonPatch(this_cell['roiPoly'][iframe], facecolor=this_cell['cellColor'], edgecolor=[0.2,0.2,0.2], alpha=0.7, zorder=3)
        #    ax.add_patch(this_patch)    
        
    ax.axis('off')
    print("Exporting frame %s to %s"%((frame+1), fileNameTracked))
    #plt.show()
    fig1 = plt.gcf()
    fig1.savefig(fileNameTracked)
    plt.close()

    
    





print("loaded!")

