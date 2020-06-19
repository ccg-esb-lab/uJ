

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
from shapely import affinity
from shapely.geometry import LineString


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

import warnings
warnings.simplefilter('ignore', np.RankWarning)


#sys.path.insert(0, './lib/')
#from readroi import read_roi_zip
#from readroi import *
from DataManagers import *
from DataStructs import *

print("TrackingFunctions... ",end='')
############### CELL FUNCTIONS ##################




############### I/O Functions ##################



############### PLOTTING FUNCTIONS ##################




############### ROI PROCESSING FUNCTIONS (PARALLEL) ##################


def par_process_rois():
    
    import numpy as np
    
    def get_max_x_angle(poly):
        rangle=0
        angles= list(range(0,185,5))
        (bminx, bminy, bmaxx, bmaxy)=poly.bounds
        xl=bmaxx-bminx
        yl=bmaxy-bminy
        center=Point((xl/2)+bminx,(yl/2)+bminy)

        max_xrange=xl
        for i,angle in enumerate(angles):
            #print(i,angle)
            poly_t=affinity.rotate(poly,angle,center)
            (bminx, bminy, bmaxx, bmaxy)=poly_t.bounds
            xl=bmaxx-bminx

            if(xl>max_xrange):
                max_xrange=xl
                rangle=angle

        return rangle,center


    def get_cell_axis(poly):
      #  t=time.time()
        line=LineString()
        pre_cloud=[]

        angle,center=get_max_x_angle(poly)

        poly=affinity.rotate(poly, angle,center )

        ext=poly.exterior.coords

        decs=0

        for i,seed_point in enumerate(ext):
            pre_cloud_i=[]

            seed_point=Point(seed_point)

            i=.5;
            intersection=poly.exterior.intersection(seed_point)
            sphere=seed_point.buffer(i)
            intersection=poly.exterior.intersection(sphere.exterior)
            while(len(list(intersection))>0):
                arc=Point()
                sphere=seed_point.buffer(i)
                intersection=poly.exterior.intersection(sphere.exterior)
                i+=3
                #i+=.5

                if(len(list(intersection))<=1):
                    continue

                arc=poly.intersection(sphere.exterior)

                if(arc.geom_type=="MultiLineString"):

                    for this_geom in arc.geoms:
                        arc_xy=list(this_geom.coords)

                        for pi in arc_xy:
                            pi=Point(pi)
                            pre_cloud_i.append((round(pi.x,decs),round(pi.y,decs)))

                elif(arc.geom_type=="LineString"):
                    for pi in list(arc.coords):
                        pi=Point(pi) 
                        pre_cloud_i.append((round(pi.x,decs),round(pi.y,decs)))


            pre_cloud.append(pre_cloud_i)


        cloud=MultiPoint(pre_cloud[0])

        for line in pre_cloud:

            line=MultiPoint(line)
            cloud=cloud.union(line)

        ###make poly fit to points cloud
        xs=[]
        ys=[]
        for pi in cloud:
            pi=Point(pi)

            xs.append(pi.x)
            ys.append(pi.y)

        pf=np.poly1d(np.polyfit(xs,ys,25))
        xr=np.linspace(np.min(xs),np.max(xs),100)

        line=[]
        for x in xr:
            pi=Point(x,pf(x))
            line.append(pi)

        line=LineString(line)
        linexy=np.array(line)
        linex=linexy[:,0]
        liney=linexy[:,1]

        line=poly.intersection(line)
        liner=affinity.rotate(line,-angle,center)
        if(liner.geom_type=="MultiLineString"):
            line=LineString()
            for this_geom in liner.geoms:
                if(this_geom.length>line.length):
                    line=this_geom
            liner=line



        linexy=np.array(liner)
        linex=linexy[:,0]
        liney=linexy[:,1]

        x=(np.max(xs)-np.min(xs))/2+np.min(xs)
        pi=Point(x,pf(x))


        center=affinity.rotate(pi,-angle,center)
       # t=time.time()-t
       # print(t)

        return liner,center
    
    frame_axis=[]
    frame_centers=[]
    for j,this_roi in enumerate(rois):
        
        this_axis,this_center=get_cell_axis(this_roi)
            
        frame_axis.append(this_axis)
        frame_centers.append(this_center)
    ret=[rois, roiIDs, frame_axis, frame_centers]
    return ret





#########################################################3
def get_polys_coverage(poly1,poly2):

    a,c=get_max_x_angle(poly1)
    poly1=affinity.rotate(poly1,a,c)
    
    a,c=get_max_x_angle(poly2)
    poly2=affinity.rotate(poly2,a,c)


    (bminx, bminy, bmaxx, bmaxy)=poly1.bounds
    poly1=affinity.translate(poly1,-bminx,-bminy)
    (bminx, bminy, bmaxx, bmaxy)=poly2.bounds
    poly2=affinity.translate(poly2,-bminx,-bminy)

    poly1=poly1.convex_hull
    poly2=poly2.convex_hull
    
    pI=poly1.intersection(poly2)
 

    coverage_1=pI.area/poly1.area
    coverage_2=pI.area/poly2.area
    
    coverage=max(coverage_1,coverage_2)
    
    #coverage=coverage_1+coverage_1
    
    return coverage

def get_max_x_angle(poly):
        rangle=0
        angles= list(range(0,185,5))
        (bminx, bminy, bmaxx, bmaxy)=poly.bounds
        xl=bmaxx-bminx
        yl=bmaxy-bminy
        center=Point((xl/2)+bminx,(yl/2)+bminy)

        max_xrange=xl
        for i,angle in enumerate(angles):
            #print(i,angle)
            poly_t=affinity.rotate(poly,angle,center)
            (bminx, bminy, bmaxx, bmaxy)=poly_t.bounds
            xl=bmaxx-bminx

            if(xl>max_xrange):
                max_xrange=xl
                rangle=angle

        return rangle,center





############### TRACKING FUNCTIONS ##################

def track_this_indexs(local_cells_index, local_cells_frames, local_cells, weight_vec):
    
    for i, this_index in enumerate(local_cells_index):
        to_frame=0
        from_frame=local_cells_frames[i]
#        to_frame=from_frame-1


      #  [toTrack_rois,toTrack_roiIDs]=load_frame('%s%s'%(dirNameROIs,fileROIs[from_frame]))
        if i%100==0:
            print("\n%s."%i,end='')
        else:
            print(".",end='')
        #print("\n*** Tracking ROI \'%s\' from frame %s"%(toTrack_roiIDs[this_index], local_cells_frames[i]+1))
       # this_tracked_cell=new_tracked_cell(str(len(tracked_cells)+1).zfill(3))
       # this_tracked_cell=add_roi_tracked_cell(this_tracked_cell,local_cells_frames[i],toTrack_roiIDs[this_index],toTrack_rois[this_index])
       # x=this_tracked_cell['cellID'] 
       # print('**',x)    
       # local_cells[local_cells_frames[i]][this_index]['cellColor']='#000000'
        
        #trackID=str(i+1).zfill(3)
        trackID=local_cells[local_cells_frames[i]][this_index]['cellID']
        local_cells[local_cells_frames[i]][this_index]['trackID'].append(trackID)    #change to something clever
        local_cells[local_cells_frames[i]][this_index]['motherID']=trackID
        
        #this_tracked_cell=track_cell_frames_charly_r(this_tracked_cell, this_index, from_frame, to_frame)
        #this_tracked_cell,local_cells=track_cells_weight_r(this_tracked_cell, this_index, from_frame, to_frame, local_cells)
        local_cells=track_cells_weight_r(this_index, from_frame, to_frame, local_cells,weight_vec)
        
       
    
    return local_cells




# def track_cell_weight(this_cell, to_track_cells, weight_vec):
#   #  weight_vec=[-1,-5,5,35,-175]  #No deberia estar aquí
    
    
#     neighbors=[]
#     max_neighbors=10
#     #max_distance=700 # (max in image)
    
    
#     roi2_daughter=-1
#     tracked_cell_index=-1
    
#     this_cell_center=this_cell['center']
    
    
#     # This cell calculations
#     this_cell_axis=this_cell['axis']
#     this_cell_box=this_cell_axis.bounds
#     this_cell_angle=np.arctan((this_cell_box[3]-this_cell_box[1])/(this_cell_box[2]-this_cell_box[0]))    
    
#     this_cell_axis=this_cell['axis']
#     this_cell_poly=this_cell['roiPoly']
#     this_cell_GFP=this_cell['GFP']
#     this_cell_DsRed=this_cell['DsRed']
#     this_cell_absint=this_cell['AbsInt']
    
#     #if(not this_cell_poly.is_valid):
#     #this_cell_poly=this_cell_poly.buffer(0)
#     this_cell_poly=this_cell_poly.convex_hull
    
    
#     neighbors=get_N_neighbors(this_cell, to_track_cells,max_neighbors)
    
#     # Neighbors calculations
    
#     t_weight=float("-inf")
#     chosen_w=[]
#     for this_ng in neighbors:
        
#         to_track_cell=to_track_cells[this_ng['index']]
#         to_track_poly=to_track_cell['roiPoly']
        
#         to_track_poly=to_track_poly.convex_hull
    

        
#         to_track_axis=to_track_cell['axis']
#         track_cell_box=to_track_axis.bounds
#         track_cell_angle=np.arctan((track_cell_box[3]-track_cell_box[1])/(track_cell_box[2]-track_cell_box[0]))
#         angle_diff=this_cell_angle-track_cell_angle
#         angle_diff=abs(angle_diff)
#         this_ng['angleDiff']=angle_diff
        
#         to_track_poly=to_track_cell['roiPoly']
#         #axisIntersection=to_track_poly.intersection(this_cell_axis)
#         #axisFraction=axisIntersection.length/this_cell_axis.length
        
#         polyInter=this_cell_poly.intersection(to_track_poly)
#         axisFraction=max(polyInter.area/this_cell_poly.area,polyInter.area/to_track_poly.area)
#         #axisFraction=polyInter.area#/this_cell_poly.area
        
#         this_ng['axisFraction']=axisFraction
        
#         this_ng['absInt']=to_track_cell['AbsInt']
#         absDIff=abs(this_ng['absInt']-this_cell_absint)
        
#         coverage=get_polys_coverage(this_cell_poly,to_track_poly)
        
#         this_ng['coverage']=coverage
        
# #         to_track_fl=to_track_cell['RelInt']
# #         flDiff=this_cell_fl-to_track_fl
# #         flDiff=abs(flDiff)
# #         this_ng['flDiff']=flDiff
        
# #         this_vec=[this_ng['distance'],angle_diff,coverage,axisFraction,flDiff]

#         to_track_fl=to_track_cell['GFP']
#         flDiff=this_cell_GFP-to_track_fl
#         GFPDiff=abs(flDiff)
#         this_ng['GFP']=GFPDiff
#         to_track_fl=to_track_cell['DsRed']
#         flDiff=this_cell_DsRed-to_track_fl
#         DsRedDiff=abs(flDiff)
#         this_ng['DsRed']=DsRedDiff
        
#         this_vec=[this_ng['distance'],angle_diff,coverage,axisFraction,GFPDiff,DsRedDiff,absDIff]

#         this_ng['weightV']=this_vec
        
        
#         this_weight=np.dot(this_vec,weight_vec)
#         this_ng['weight']=this_weight
        
#         #print(this_vec,this_weight)
        
# #         if(this_cell['cellID'] in lalalist):
# #             print(this_vec,this_weight,this_ng['index'])
        
#         if(this_weight>t_weight):
#             t_weight=this_weight
#             tracked_cell_index=this_ng['index']
#             chosen_ng=this_ng['weightV']
#             chosen_ng2=this_ng['weight']
        
#     #print()
#     #print(this_cell['center'],to_track_cells[tracked_cell_index]['center'])    
#    # return [tracked_cell_index, roi2_daughter]
#     return [tracked_cell_index, '%s -> %s'%(chosen_ng,chosen_ng2)]

def track_cell_weight(this_cell, to_track_cells, weight_vec):
  #  weight_vec=[-1,-5,5,35,-175]  #No deberia estar aquí
   
    
    neighbors=[]
    max_neighbors=10
    #max_distance=700 # (max in image)
    
    
    roi2_daughter=-1
    tracked_cell_index=-1
    
    this_cell_center=this_cell['center']
    
    
    # This cell calculations
    this_cell_axis=this_cell['axis']
    this_cell_box=this_cell_axis.bounds
    this_cell_angle=np.arctan((this_cell_box[3]-this_cell_box[1])/(this_cell_box[2]-this_cell_box[0]))    
    
    this_cell_axis=this_cell['axis']
    this_cell_poly=this_cell['roiPoly']
    this_cell_GFP=this_cell['GFP']
    this_cell_DsRed=this_cell['DsRed']
  #  this_cell_absint=this_cell['Norm_GFP']
    
    #if(not this_cell_poly.is_valid):
    #this_cell_poly=this_cell_poly.buffer(0)
    this_cell_poly=this_cell_poly.convex_hull
    
    
    neighbors=get_N_neighbors(this_cell, to_track_cells,max_neighbors)
    
    # Neighbors calculations
    
    t_weight=float("-inf")
    chosen_w=[]
    for this_ng in neighbors:
        
        to_track_cell=to_track_cells[this_ng['index']]
        to_track_poly=to_track_cell['roiPoly']
        
        to_track_poly=to_track_poly.convex_hull
    

        
        to_track_axis=to_track_cell['axis']
        track_cell_box=to_track_axis.bounds
        track_cell_angle=np.arctan((track_cell_box[3]-track_cell_box[1])/(track_cell_box[2]-track_cell_box[0]))
        angle_diff=this_cell_angle-track_cell_angle
        angle_diff=abs(angle_diff)
        this_ng['angleDiff']=angle_diff
        
        to_track_poly=to_track_cell['roiPoly']
        #axisIntersection=to_track_poly.intersection(this_cell_axis)
        #axisFraction=axisIntersection.length/this_cell_axis.length
        
        polyInter=this_cell_poly.intersection(to_track_poly)
        axisFraction=max(polyInter.area/this_cell_poly.area,polyInter.area/to_track_poly.area)
        #axisFraction=min(polyInter.area/this_cell_poly.area,polyInter.area/to_track_poly.area)
        #axisFraction=polyInter.area#/this_cell_poly.area
        #print(polyInter)
        this_ng['axisFraction']=axisFraction
        
      #  this_ng['Norm_GFP']=to_track_cell['Norm_GFP']
    #    absDIff=abs(this_ng['Norm_GFP']-this_cell_absint)
        
        coverage=get_polys_coverage(this_cell_poly,to_track_poly)
        
        this_ng['coverage']=coverage
        
#         to_track_fl=to_track_cell['RelInt']
#         flDiff=this_cell_fl-to_track_fl
#         flDiff=abs(flDiff)
#         this_ng['flDiff']=flDiff
        
#         this_vec=[this_ng['distance'],angle_diff,coverage,axisFraction,flDiff]

        to_track_fl=to_track_cell['GFP']
        flDiff=this_cell_GFP-to_track_fl
        GFPDiff=abs(flDiff)
        this_ng['GFP']=GFPDiff
        to_track_fl=to_track_cell['DsRed']
        flDiff=this_cell_DsRed-to_track_fl
        DsRedDiff=abs(flDiff)
        this_ng['DsRed']=DsRedDiff
        
        #this_vec=[this_ng['distance'],angle_diff,coverage,axisFraction,GFPDiff,DsRedDiff,absDIff]
        this_vec=[this_ng['distance'],angle_diff,coverage,axisFraction,GFPDiff,DsRedDiff]

        this_ng['weightV']=this_vec
        
        
        this_weight=np.dot(this_vec,weight_vec)
        this_ng['weight']=this_weight
        
       
        
#         this_vec2=[round(x,3) for x in this_vec]
#         print(this_cell['cellID'],this_vec2,this_weight,this_ng['index'])
        
        if(this_weight>t_weight):
            t_weight=this_weight
            tracked_cell_index=this_ng['index']
            chosen_ng=this_ng['weightV']
            chosen_ng2=this_ng['weight']
        
    #print()
    #print(tracked_cell_index)
    #print(this_cell['center'],to_track_cells[tracked_cell_index]['center'])    
   # return [tracked_cell_index, roi2_daughter]
    return [tracked_cell_index, '%s -> %s'%(chosen_ng,chosen_ng2)]






def track_cells_weight_r( tracked_cell_index, from_frame, to_frame, local_cells, weight_vec):
    
    
    for this_frame in range(from_frame,to_frame,-1):
        #print("%s-%s"%(this_frame,tracked_cell_index),end=' ,')
        #cells=cells[this_frame]
        #this_cell=cells[this_frame][roi1_index]
        this_cell=local_cells[this_frame][tracked_cell_index]
        to_track_cells=local_cells[this_frame-1]

        this_cell_trackID=local_cells[this_frame][tracked_cell_index]['trackID']
        this_cell_ID=local_cells[this_frame][tracked_cell_index]['cellID']
        this_cell_color=local_cells[this_frame][tracked_cell_index]['cellColor']
        
        
        
        [tracked_cell_index, tracked_info]=track_cell_weight(this_cell, to_track_cells,weight_vec)
        
    #    print("%s-%s"%(this_frame-1,tracked_cell_index),end=' ,')
  #      print("*",roi2_daughter)
        if(tracked_cell_index==-1):
            print("** Cell %s not tracked",this_cell['cellID'])
            return local_cells
        
        this_tracked_trackID=local_cells[this_frame-1][tracked_cell_index]['trackID']
        
        
       
        
        
        if(len(this_tracked_trackID)>=1):
            #print('.',end='')
            local_cells[this_frame-1][tracked_cell_index]['motherID']=this_cell_trackID
            local_cells[this_frame-1][tracked_cell_index]['trackedBy_next_frame'].append(this_cell_ID)
            local_cells[this_frame-1][tracked_cell_index]['trackedBy_next_frame']=list(set(local_cells[this_frame-1][tracked_cell_index]['trackedBy_next_frame']))
       #
    
#             if(len(local_cells[this_frame-1][tracked_cell_index]['trackedBy_next_frame'])>2):
#                 print('\n',local_cells[this_frame-1][tracked_cell_index]['cellID'],"\t",local_cells[this_frame-1][tracked_cell_index]['trackedBy_next_frame'],'- ',tracked_info,this_cell_ID)
#                 plot_this_cells(local_cells[this_frame-1][tracked_cell_index]['cellID'],local_cells[this_frame-1][tracked_cell_index]['trackedBy_next_frame'],cells)
        
    
    
            return local_cells
        
        else:
            local_cells[this_frame-1][tracked_cell_index]['trackID'].extend(this_cell_trackID)
            local_cells[this_frame-1][tracked_cell_index]['trackID']=list(set(local_cells[this_frame-1][tracked_cell_index]['trackID']))
            local_cells[this_frame-1][tracked_cell_index]['cellColor']=this_cell_color
            
    
    
       # print("this cell id: %s\nthis cell track id %s\n tci %s"%(this_cell_ID,this_cell_trackID,tracked_cell_index))
#         print("--->",local_cells[this_frame-1][tracked_cell_index]['trackedBy_next_frame'])
    
        local_cells[this_frame-1][tracked_cell_index]['motherID']=this_cell_trackID
        local_cells[this_frame-1][tracked_cell_index]['trackedBy_next_frame'].append(this_cell_ID)
        local_cells[this_frame-1][tracked_cell_index]['trackedBy_next_frame']=list(set(local_cells[this_frame-1][tracked_cell_index]['trackedBy_next_frame']))
       # print("--->*",local_cells[this_frame-1][tracked_cell_index]['trackedBy_next_frame'])
        
        
    return local_cells


######################################################

def clear_this_cell_track(this_cell,local_cells):
    this_cell_id=this_cell['cellID']
    this_cell_id_list=this_cell_id.split('.')
    

    this_cell_frame=int(this_cell_id_list[0])
    this_cell_index=int(this_cell_id_list[1])
    print("Clearing track of...",this_cell_frame,this_cell_index)
    
    for frame in reversed(range(this_cell_frame)):
        for tracked_index,this_tracked_cell in enumerate(local_cells[frame]):
            this_tracked_cell_trackedList=this_tracked_cell['trackedBy_next_frame']
            if(this_cell['cellID'] in this_tracked_cell_trackedList):
                print(this_tracked_cell['cellID'],end=' ')
               # print(" ",local_cells[frame][tracked_index]['trackID'],this_cell['trackID'])
                local_cells[frame][tracked_index]['trackedBy_next_frame'].remove(this_cell['cellID'])
                
                for this_track_id in this_cell['trackID']:
                    if(local_cells[frame][tracked_index]['trackID']):
                       # print(" ",local_cells[frame][tracked_index]['trackID'],this_track_id)
                        local_cells[frame][tracked_index]['trackID'].remove(this_track_id)
                
                
                this_cell=this_tracked_cell
    
    
    return local_cells



def clear_tracks(local_cells):
    for i in range(len(local_cells)):
        for j in range(len(local_cells[i])):
            local_cells[i][j]['trackID']=[]
            local_cells[i][j]['trackedBy_next_frame']=[]
            local_cells[i][j]['trackedBy_previous_frame']=[]
            local_cells[i][j]['motherID']=[]
    
    return local_cells


def get_N_neighbors(this_cell, to_track_cells,N):
    neighbors=[]
    distances=[]
    threshold_distance=0.
    this_cell_center=this_cell['center']
    
    #Compute threshold distance to the N closest cells
    for to_track_cell in to_track_cells:
        to_track_center=to_track_cell['center']
        this_d=this_cell_center.distance(to_track_center)
        distances.append(this_d)
    
    distances.sort()
    #print("*",len(distances))
    if(len(distances)<=N):
        threshold_distance=distances[len(distances)-1]
    else:
        threshold_distance=distances[N-1]
    
    #Find the N closets cells
    for to_track_index,to_track_cell in enumerate(to_track_cells):
        to_track_center=to_track_cell['center']
        this_d=this_cell_center.distance(to_track_center)
        
        to_track_id=to_track_cell['cellID'] 
        
        if(this_d<=threshold_distance and len(neighbors)<N):
            this_ng=new_neighbor(to_track_index,to_track_id,this_d)
            neighbors.append(this_ng)
    
    
    return neighbors
    
    




    
#########################Lineages######################################

def make_cellLineages_all(tracked_cells,frame_experiment_start,to_frame=0):
    cell_lineages=[]
    tracked_ids_list=[]
    max_frames=len(tracked_cells)-1  #?????

    from_frame=max_frames
    to_frame=0
    last_lineageID=0
    for this_frame in range(from_frame,to_frame,-1):
        
        toMake_cells=[]
        
        for select_index, this_cell in enumerate(tracked_cells[this_frame]):
            
            if len(this_cell['trackID'])==0:
                print("***",this_cell['trackID'] ,"+", this_cell['trackID'][0],"+", this_cell['cellID'])
            if this_cell['trackID'][0]==this_cell['cellID']:
               # print("**",this_cell['trackID'] ,"+", this_cell['trackID'][0],"+", this_cell['cellID'])
                toMake_cells.append(this_cell)
            else:
                0
               # print(this_cell['trackID'] ,"+", this_cell['trackID'][0],"+", this_cell['cellID'])
       # toMake_cells=tracked_cells[this_frame]
       # cell_lineages.append(make_cellLineages(cell_lineages, tracked_cells, toMake_cells, this_frame)) 
        
#         if(this_frame==113):
#             print('*',len(tracked_ids_list))
#             return cell_lineages
            
            
            
        print('Making lineages of %s cells out of %s from frame %s '%(len(toMake_cells),len(tracked_cells[this_frame]),this_frame))
        cell_lineages,tracked_ids_list,last_lineageID=make_cellLineages(cell_lineages, tracked_cells, toMake_cells, this_frame,tracked_ids_list,frame_experiment_start,last_lineageID)
    #break    
    
    
#     for i,this_lineage in enumerate(cell_lineages):
#         #print(i,this_lineage['motherID'])
#         this_lineage_trackID=this_lineage['trackID']
#         this_lineage_trackID_list=this_lineage_trackID.split('-')
#         crit_cell=this_lineage_trackID_list[0]
#         fr=int(crit_cell.split('.')[0])
#         ind=int(crit_cell.split('.')[1])
#         cell_lineages[i]['motherID']=tracked_cells[fr][ind]['trackID']
    
    print(len(tracked_ids_list))
    print('\nLineage complete!')
    
    return cell_lineages






def make_cellLineages(cell_lineages, tracked_cells, toMake_cells, last_frame, tracked_ids_list,frame_experiment_start,last_lineageID):   
    
    for this_cell in toMake_cells:
        this_track_id=this_cell['trackID']
        this_cellId=this_cell['cellID']
        if(this_track_id):
            #print('\n',this_track_id, end='\t')
                   
            this_roiID=this_cell['roiID']
            this_roiPoly=this_cell['roiPoly']
            this_GFP=this_cell['GFP']
            this_DsRed=this_cell['DsRed']
            this_RelInt=this_cell['RelInt']
            this_axis=this_cell['axis']
            this_center=this_cell['center']
            this_mother=this_cell['motherID']                        
            this_AbsInt=this_cell['AbsInt']                        
            #this_lineage=new_cellLineage(this_track_id)
            death=0  
            this_lineage=new_cellLineage("lameID")
                                    
            this_lineage=add_trackInfo_cellLineage(this_lineage,this_cellId, this_roiID, last_frame+frame_experiment_start, this_roiPoly, this_axis, this_center, this_GFP, this_DsRed, this_RelInt,this_AbsInt, death,this_mother )
            
            
            last_mother=this_cellId
            aux_lineageID=0
            #lineageID=len(cell_lineages)
            lineageID=last_lineageID
            frame_flag=False
            for frame in reversed(range(last_frame)):
               # print(frame,end='.')
                if(frame_flag):
                    break
                #print('.',end='')
                print(this_track_id,"\t",frame,end='\r')
                this_tracked_cells=tracked_cells[frame]
                
                for this_tracked_cell in this_tracked_cells:
                    
                    if len(this_tracked_cell['trackedBy_next_frame'])>0:
                        this_tracked_cellID_list=this_tracked_cell['trackedBy_next_frame']
                    else:
                        this_tracked_cellID_list=[]
                        
                    if((len(this_tracked_cell['trackedBy_next_frame'])>1) and (this_cellId in tracked_ids_list)):
                        #print('>1',len(this_tracked_cell['trackedBy_next_frame']),this_tracked_cell['cellID'],this_tracked_cell['trackedBy_next_frame'],this_tracked_cell['motherID'],this_track_id,frame,this_cellId)
                        #break
                        print(this_track_id,"\t",'*',end='')
                        for aux_lineage in cell_lineages:
                            aux_lienage_cellIds=aux_lineage['cellIDs']
                            if(this_cellId in aux_lienage_cellIds):
                                aux_lineageID=aux_lineage['lineageID']
                        frame_flag=True
                        break
                    
                    elif(this_cellId in this_tracked_cellID_list):
                    #if(this_cellId in this_tracked_cellID_list):
                        
                        
                        tracked_ids_list.append(this_cellId)
                        tracked_ids_list=list(set(tracked_ids_list))
                    
                        
                        
                        #print(this_cellId,end=' ,')
                        this_cellId=this_tracked_cell['cellID']
                        this_roiID=this_tracked_cell['roiID']
                        
                        this_roiPoly=this_tracked_cell['roiPoly']
                        this_axis=this_tracked_cell['axis']
                        this_center=this_tracked_cell['center']
                        this_GFP=this_tracked_cell['GFP']
                        this_DsRed=this_tracked_cell['DsRed']
                        this_RelInt=this_tracked_cell['RelInt']
                        this_AbsInt=this_tracked_cell['AbsInt']
                        this_mother=this_tracked_cell['motherID']                        
                        
                        death=0  
                        #his_lineage=add_trackInfo_cellLineage(this_lineage,this_cellId, this_roiID, frame, this_roiPoly, this_axis, this_center, this_GFP, this_DsRed, this_RelInt,this_AbsInt ,this_mother )
                        this_lineage=add_trackInfo_cellLineage(this_lineage,this_cellId, this_roiID, frame+frame_experiment_start, this_roiPoly, this_axis, this_center, this_GFP, this_DsRed, this_RelInt,this_AbsInt, death,this_mother )
                        last_mother=this_mother
                        last_mother=this_cellId
                        
                        
                   
                    
                
            if(aux_lineageID):
                print(lineageID,'-',aux_lineageID,end='\r')
                this_lineage['lineageID']=aux_lineageID
            else:
                last_lineageID=last_lineageID+1
                this_lineage['lineageID']=last_lineageID
            this_lineage['motherID']=last_mother

            
            #     ### Fix reverse tracking.....    
            this_lineage['cellIDs']=(this_lineage['cellIDs'][::-1])
            this_lineage['roiID']=(this_lineage['roiID'][::-1])
            this_lineage['roiFrames']=(this_lineage['roiFrames'][::-1])
            this_lineage['roiPolys']=(this_lineage['roiPolys'][::-1])
            this_lineage['axis']=(this_lineage['axis'][::-1])
            this_lineage['center']=(this_lineage['center'][::-1])
            this_lineage['GFP']=(this_lineage['GFP'][::-1])
            this_lineage['DsRed']=(this_lineage['DsRed'][::-1])
            this_lineage['RelInt']=(this_lineage['RelInt'][::-1])
            this_lineage['AbsInt']=(this_lineage['AbsInt'][::-1])
            this_lineage['dead']=(this_lineage['dead'][::-1])
            
            for t_cell_id in this_lineage['cellIDs']:
                t_cell_id_list=t_cell_id.split('.')
                to_div_frame=int(t_cell_id_list[0])
                to_div_index=int(t_cell_id_list[1])
                
                to_div_frame=to_div_frame-frame_experiment_start
                
                to_div_cell_tracked_trackedByNext=tracked_cells[to_div_frame][to_div_index]['trackedBy_next_frame']
                if(len(to_div_cell_tracked_trackedByNext)>1):
                    #print('.',end='')
                    this_lineage['divisions'].append(1)                    
                else:
                    this_lineage['divisions'].append(0)
                        
            
            
            this_lineage['trackID']=str("%s-%s"%(this_lineage['cellIDs'][0],this_lineage['cellIDs'][-1]))
            
            

            cell_lineages.append(this_lineage)
    

    
    return cell_lineages,tracked_ids_list,last_lineageID

############### MISC FUNCTIONS ##################


def TicTocGenerator():
    # Generator that returns time differences
    ti = 0           # initial time
    tf = time.time() # final time
    while True:
        ti = tf
        tf = time.time()
        yield tf-ti # returns the time difference

TicToc = TicTocGenerator() # create an instance of the TicTocGen generator

# This will be the main function through which we define both tic() and toc()
def toc(tempBool=True):
    # Prints the time difference yielded by generator instance TicToc
    tempTimeInterval = next(TicToc)
    if tempBool:
        print( "Elapsed time: %f seconds." %tempTimeInterval )

def tic():
    # Records a time in TicToc, marks the beginning of a time interval
    toc(False)


    
    
    
print("loaded!")


