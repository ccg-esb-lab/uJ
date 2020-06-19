
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os
import sys
import pathlib
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.patches as patches
from shapely.geometry import Point
from shapely.geometry import MultiPoint
from shapely.geometry import MultiPolygon
from shapely.geometry import Polygon
from shapely.geometry import box
from descartes.patch import PolygonPatch
from shapely import affinity
from shapely.geometry import LineString
import scipy.stats as st
import pandas as pd
import random
from scipy.stats import linregress

import re

from shapely import geometry
import pickle
import time

from DataManagers import *
from DataStructs import *




print("PlottingFunctions... ",end='')
def plot_track_path(cells,the_frame,path,fsz):
    #plt.clf()
    fig=plt.figure(1,frameon=True)
    DPI = fig.get_dpi()
    figxlim=fsz[0]
    figylim=fsz[1]
    figWidth=figxlim/float(DPI)
    figHight=figylim/float(DPI)
    fig.set_size_inches(figWidth,figHight)
    
    ax = plt.axes()
    ax.clear()
    
    ax.axis("off")
    ax.set_aspect('equal',adjustable='box')
    plt.xlim(0,figxlim)
    plt.ylim(0,figylim)

    matchID=""
    for this_cell in cells[the_frame-1]:
        if(this_cell['cellID'] in path):
            this_poly=this_cell['roiPoly']
            matchID=this_cell['cellID']
            patch = PolygonPatch(this_poly, facecolor=[0,0,0], edgecolor=[0,0,0], alpha=0.7, zorder=2)
            ax.add_patch(patch)
#         else:
#             this_poly=this_cell['roiPoly']

#             patch = PolygonPatch(this_poly, facecolor=[0.75,0.75,0.75], edgecolor=[0,0,0], alpha=0.7, zorder=2)
#             ax.add_patch(patch)
   

    
    plt.gca().invert_yaxis()
    plt.tight_layout(pad=0,h_pad=0,w_pad=0)
    return plt,matchID


def plot_mother_lineages(cells,the_frame,mother_list,fsz):
    fig=plt.figure(1,frameon=True)
    DPI = fig.get_dpi()
    figxlim=fsz[0]
    figylim=fsz[1]
    figWidth=figxlim/float(DPI)
    figHight=figylim/float(DPI)
    fig.set_size_inches(figWidth,figHight)
    ax = plt.axes()
    ax.clear()
    ax.axis("off")
    ax.set_aspect('equal',adjustable='box')
    plt.xlim(0,figxlim)
    plt.ylim(0,figylim)
    
    for this_cell in cells[the_frame-1]:
        if(this_cell['cellID'] in mother_list):
            this_poly=this_cell['roiPoly']
            
            patch = PolygonPatch(this_poly, facecolor=[0,0,0], edgecolor=[0,0,0], alpha=0.7, zorder=2)
            ax.add_patch(patch)
        else:
            this_poly=this_cell['roiPoly']

            patch = PolygonPatch(this_poly, facecolor=[0.75,0.75,0.75], edgecolor=[0,0,0], alpha=0.7, zorder=2)
            ax.add_patch(patch)
   

    plt.gca().invert_yaxis()
    plt.tight_layout(pad=0,h_pad=0,w_pad=0)
    
    return plt
#####################################
def draw_cell(local_cells,tracked_frame,fsz):
    fig=plt.figure(1,frameon=True)
    DPI = fig.get_dpi()
    figxlim=fsz[0]
    figylim=fsz[1]
    figWidth=figxlim/float(DPI)
    figHight=figylim/float(DPI)
    fig.set_size_inches(figWidth,figHight)
    
    ax = plt.axes()
    ax.clear()
    
    ax.axis("off")
    ax.set_aspect('equal',adjustable='box')
    plt.xlim(0,figxlim)
    plt.ylim(0,figylim)
    #plt.axis('off')
    #ax.clear()
    print('Building plot for frame frame %s '%(tracked_frame),end="\r")
    for this_cell in local_cells[tracked_frame-1]:
        
        this_poly=this_cell['roiPoly']
        if(this_cell['trackID']):
            patch = PolygonPatch(this_poly, facecolor=this_cell['cellColor'], edgecolor=[0.2,0.2,0.2], alpha=0.7, zorder=3)    
        else:
            patch = PolygonPatch(this_poly, facecolor=[0.75,0.75,0.75], edgecolor=[0,0,0], alpha=0.3, zorder=2)
        
        ax.add_patch(patch)
        this_axis=this_cell['axis']
        linexy=np.array(this_axis)
        linex=linexy[:,0]
        liney=linexy[:,1]
        ax.plot(linex,liney,'c-',alpha=0.5)
        
    #ax.axis('off')
    #plt.xlim(0,1000)
    #plt.ylim(0,512)
    #rfig=fig
    plt.gca().invert_yaxis()
    plt.tight_layout(pad=0,h_pad=0,w_pad=0)
    
    return fig




####################################3

def show_all(this_tracked_plots,tracked_frame,fs):
#    print("Ploting frame: ",tracked_frame,"File: ",fileROIs[tracked_frame-1]) ##printing flickers
    fig=this_tracked_plots[tracked_frame-fs]
    display(fig)


def make_colormap(seq):
    """Return a LinearSegmentedColormap
    seq: a sequence of floats and RGB-tuples. The floats should be increasing
    and in the interval (0,1).
    """
    seq = [(None,) * 3, 0.0] + list(seq) + [1.0, (None,) * 3]
    cdict = {'red': [], 'green': [], 'blue': []}
    for i, item in enumerate(seq):
        if isinstance(item, float):
            r1, g1, b1 = seq[i - 1]
            r2, g2, b2 = seq[i + 1]
            cdict['red'].append([item, r1, r2])
            cdict['green'].append([item, g1, g2])
            cdict['blue'].append([item, b1, b2])
    return mcolors.LinearSegmentedColormap('CustomMap', cdict)

def make_cmap(colors, position=None, bit=False):
    bit_rgb = np.linspace(0,1,256)
    if position == None:
        position = np.linspace(0,1,len(colors))
    else:
        if len(position) != len(colors):
            sys.exit("position length must be the same as colors")
        elif position[0] != 0 or position[-1] != 1:
            sys.exit("position must start with 0 and end with 1")

    if bit:
        for i in range(len(colors)):
            colors[i] = (bit_rgb[colors[i][0]], bit_rgb[colors[i][1]], bit_rgb[colors[i][2]])
    
    cdict = {'red':[], 'green':[], 'blue':[]}

    for pos, color in zip(position, colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))
        cmap = cm.colors.LinearSegmentedColormap('my_colormap',cdict,256)
    return cmap



def plot_cells_poincare(this_cells, this_data_label, fileName):
    fig=plt.figure(figsize=(8,8))
    ax = plt.axes()
    for this_cell in this_cells:
        try:
            x=this_cell[this_data_label]
            y=x[0:-1]
            x.pop(0)
            c=this_cell['cellColor']
            ax.plot(x, y, color=c, alpha=.25, linewidth=1)
            
            
        except (TypeError,IndexError):
            continue
    
    ax.set_xlabel('t')
    ax.set_ylabel('t+1')
    plt.title(this_data_label)
    plt.savefig(fileName)
    plt.show()



#Function that plots frames vs GFP/DsRed/relativeIntensity/?
def plot_cell_data(this_cell, this_data_label):
    fig=plt.figure(figsize=(10,4))
    ax = plt.axes()
    #x=this_cell['times']
    x=this_cell['roiFrames']
    y=this_cell[this_data_label]
    c=this_cell['cellColor']
    ax.plot(x, y, color=c, alpha=1, linewidth=2)
            
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel(this_data_label)
    plt.show()
    

def plot_relativeIntensity(this_cell):
    fig=plt.figure(figsize=(10,4))
    ax = plt.axes()
    #time=this_cell['times']
    time=this_cell['roiFrames']
    relativeIntensity=this_cell['relInt']
    c=this_cell['cellColor']
    ax.plot(time, relativeIntensity, color=c, alpha=1, linewidth=2)
    ax.plot([0,np.max(time)],[0,0],'k:', linewidth=1, alpha=0.5)
            
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel('Relative Intensity (a.u.)')
    
    ax.set_ylim([-1,1])
    ax.set_xlim([0, np.max(time)])
    plt.show()
    
def plot_relativeIntensity_Horizon(lcells, num_levels, fileName):
    
    fig, axarr = plt.subplots(len(lcells),1, sharex=True,figsize=(12,len(lcells)))
    #f.subplots_adjust(vspace=0)
    
    for iax, this_cell in enumerate(lcells):
        
        if len(lcells)>1:
            ax=axarr[iax]
        else:
            ax = axarr

        #time=this_cell['times']
        time=this_cell['roiFrames']
        relativeIntensity=np.add(-0.,this_cell['RelInt'])
        
        if len(time)>1:

            #ax.plot(time, np.add(0.5,.5*relativeIntensity), 'k-', alpha=.5, linewidth=1)
            ax.fill_between([time[0], time[-1]], 0., 1., color='y', alpha=0.2)

            zero_crossings = np.where(np.diff(np.sign(relativeIntensity)))[0]
            
            zero_crossings=np.hstack((0,zero_crossings, len(relativeIntensity)-1))
            i0=0
            for ix in zero_crossings:
                try:
                    if relativeIntensity[ix]<0:
                        if ix<len(time)-1 and ix>1:
                            tN=np.interp(0.,[relativeIntensity[ix],relativeIntensity[ix+1]],[time[ix],time[ix+1]])
                            yN=0
                        else:
                            tN=time[-1]
                            yN=relativeIntensity[-1]

                        if i0>1:
                            t0=np.interp(0.,[relativeIntensity[i0],relativeIntensity[i0-1]],[time[i0],time[i0-1]])
                            y0=0.
                        else:
                            t0=time[0]
                            y0=relativeIntensity[0]
                        if ix>0:
                            xtimes=np.hstack((t0,time[i0:ix+1],tN))
                            xrelativeIntensity=np.hstack((y0, relativeIntensity[i0:ix+1], yN))

                            for this_level in range(0,num_levels):
                                ax.fill_between(xtimes, num_levels*this_level+1, np.add(1+this_level,num_levels*xrelativeIntensity), color='r', alpha=1/num_levels)
                    else:   
                        if ix<len(time)-1 :
                            tN=np.interp(0.,[relativeIntensity[ix+1],relativeIntensity[ix]],[time[ix+1],time[ix]])
                            yN=0
                        else:
                            tN=time[-1]
                            yN=relativeIntensity[-1]

                        if i0>1:
                            t0=np.interp(0.,[relativeIntensity[i0-1],relativeIntensity[i0]],[time[i0-1],time[i0]])
                            y0=0
                        else:
                            t0=time[0]
                            y0=relativeIntensity[0]

                        if ix>0:
                            xtimes=np.hstack((t0,time[i0:ix+1],tN))

                            xrelativeIntensity=np.hstack((y0, relativeIntensity[i0:ix+1], yN))

                            for this_level in range(0,num_levels):
                                ax.fill_between(xtimes, -num_levels*this_level, np.add(-this_level,num_levels*xrelativeIntensity), color='g', alpha=1/num_levels)
                except IndexError:
                    continue
                i0=ix+1
                


        #ax.plot([0,np.max(time)],[0.5,0.5],'k:', linewidth=1, alpha=0.5)
        #ax.plot([0,np.max(time)],[1,1],'k-', linewidth=1, alpha=0.5)
        #ax.plot([0,np.max(time)],[-0,-0],'k-', linewidth=1, alpha=0.5)

        ax.text(-2,.5,'Cell %s'%this_cell['trackID'],FontSize=14, verticalalignment='center',horizontalalignment='right')
        ax.set_yticks([])

        ax.set_ylim([0,1])
        ax.set_xlim([0, 1+np.max(time)])
        
        if iax==len(lcells)-1:
            ax.set_xlabel('Time (frames)',FontSize=14)
            ax.set_xticks(np.arange(0,np.max(time),10))
        else:
            ax.set_xlabel('',FontSize=16)
            ax.set_xticks([])
    plt.savefig(fileName)
    #plt.close()
    
def plot_cells_data(this_cells, this_data_label, fileName):
    fig=plt.figure(figsize=(12,4))
    ax = plt.axes()
    maxT=1
    
    xs=[]
    ys=[]
    for this_cell in this_cells:
        try:
            x=this_cell['roiFrames']
            
            if np.max(x)>maxT:
                maxT=np.max(x)
            y=this_cell[this_data_label]
            c=[.6,.6,.6]#this_cell['cellColor']
            ax.plot(x, y, color=c, alpha=.1, linewidth=1)
            
            xs.append(x)
            ys.append(y)
            
        except TypeError:
            continue
    
    #Now plot mean
    flat_xs = np.asarray([item for sublist in xs for item in sublist])
    flat_ys = np.asarray([item for sublist in ys for item in sublist])
    mean_ys=[]
    mean_xs=[]
    for xi in set(flat_xs):
        i = [i for i,x in enumerate(flat_xs) if x == xi]
        mean_ys.append(np.mean(flat_ys[i]))
        mean_xs.append(xi)
    ax.plot(mean_xs,mean_ys,'k-', linewidth=2.0) 
    ax.plot([0, maxT],[0,0],'k:', linewidth=1.)    
        
    ax.set_xlabel('Time (frames)')
    ax.set_ylabel(this_data_label)
    ax.set_xlim([0, maxT])
    plt.savefig(fileName)
    plt.show()


######################################3

# def get_polys(cell_lineages, frame):
#     polys=[]
#     trackIDs=[]
#     for icell, this_cell in enumerate(cell_lineages):
#         try:
#             roiFrames=(this_cell['roiFrames'])
#             roiIndex=roiFrames.index(frame)
#             polys.append(this_cell['roiPolys'][roiIndex])
#             trackIDs.append(this_cell['trackID'])
#         except (ValueError,TypeError):
#             continue
#     return [trackIDs, polys]

# def get_datapoint(df_lineages, trackID, frame):
#     this_lineage=df_lineages.loc[df_lineages['trackID'] == trackID]
#     this_data=this_lineage.loc[this_lineage['frame'] == frame]
#     if len(this_data)>0:
#         this_val=this_data['division'].values[0]
#     else:
#         this_val=-1  #Default?
#     return this_val

# def get_data_roi(poly_lineages, df_lineages, frame):
#     [polys_trackIDs, polys]=get_polys(poly_lineages, frame)

#     trackIDs=[]
#     trackPolys=[]
#     trackData=[]
#     for this_trackID in polys_trackIDs:

#         iroi=polys_trackIDs.index(this_trackID)
#         this_poly=polys[iroi]
    
#         this_data=get_datapoint(df_lineages, this_trackID, frame-1)
        
#         trackIDs.append(this_trackID)
#         trackPolys.append(this_poly)
#         trackData.append(this_data)
        
#     return [trackIDs, trackPolys, trackData]
#######################################


def get_polys(cell_lineages, frame):
    polys=[]
    trackIDs=[]
    lcolors=[]
    for icell, this_cell in enumerate(cell_lineages):
        try:
            roiFrames=(this_cell['roiFrames'])
            roiIndex=roiFrames.index(frame)
            polys.append(this_cell['roiPolys'][roiIndex])
            lcolors.append(this_cell['cellColor'])
            trackIDs.append(this_cell['trackID'])
        except (ValueError,TypeError):
            continue
    return [trackIDs, polys,lcolors]
    
    
def get_datapoint(df_lineages, trackID, frame,channel,this_color):
    this_lineage=df_lineages.loc[df_lineages['trackID'] == trackID]
    this_data=this_lineage.loc[this_lineage['frame'] == frame]
    if (len(this_data)>0 and not channel=="Mask" and not channel=="Tracking"):
        this_val=this_data[channel].values[0]
    else:
       # print(this_data[channel])
        this_val=-1  #Default?
    if(channel=="Tracking"):
        this_val=this_color
        #print(this_val)
    return this_val

def get_data_roi(poly_lineages, df_lineages, frame,channel):
    [polys_trackIDs, polys,lcolors]=get_polys(poly_lineages, frame)

    trackIDs=[]
    trackPolys=[]
    trackData=[]
    for this_trackID in polys_trackIDs:

        iroi=polys_trackIDs.index(this_trackID)
        this_poly=polys[iroi]
        this_color=lcolors[iroi]
        this_data=get_datapoint(df_lineages, this_trackID, frame,channel,this_color)
        
        trackIDs.append(this_trackID)
        trackPolys.append(this_poly)
        trackData.append(this_data)
        
    return [trackIDs, trackPolys, trackData]

def draw_channel(frame, layer, trackIDs, trackPolys, trackData, fileNameIMAGEOVERLAY,fsz):
    numColors = 201
    
    
    fig=plt.figure(1,frameon=True)
    DPI = fig.get_dpi()
    figxlim=fsz[0]
    figylim=fsz[1]
    figWidth=figxlim/float(DPI)
    figHight=figylim/float(DPI)
    fig.set_size_inches(figWidth,figHight)
    
    ax = plt.axes()
    ax.clear()
    
    ax.axis("off")
    ax.set_aspect('equal',adjustable='box')
    plt.xlim(0,figxlim)
    plt.ylim(0,figylim)
    
    
    
    ax.plot([0, figxlim],[0,figylim],'w.')  ##mmmmh
    for i, this_trackID in enumerate(trackIDs):
        
        this_poly=trackPolys[i]
        this_data=trackData[i]
        
        #Define overlay properties
        if layer['channel']=='division':  #CHANNEL: divisions
            if this_data==1:
                cellEdgeColor=[0,0,0]
                cellColor=[1,1,0]
                alphaCell=1.
            else:
                cellEdgeColor=[0.5,0.5,0.5]
                cellColor=[0.9,0.9,0.9]
                alphaCell=.5
                
        elif layer['channel']=='GFP':
            cmap= plt.cm.Greens(range(0, numColors))
            if this_data==-1:
                alphaCell=0
                cellColor=[0.5,0.5,0.5]
                cellEdgeColor=[0,0,0]
            else:
                xp=np.linspace(0,201,201)
                fp=np.linspace(layer['minvalue'],layer['maxvalue'],201)
                icolor=int(np.interp(this_data, fp, xp))
                if icolor>numColors-1:
                    icolor=numColors-1
                alphaCell=1
                cellColor=cmap[icolor,:]
                cellEdgeColor=[0,0,0]
        
        elif layer['channel']=='DsRed':
            cmap= plt.cm.Reds(range(0, numColors))
            if this_data==-1:
                alphaCell=0
                cellColor=[0.5,0.5,0.5]
                cellEdgeColor=[0,0,0]
            else:
                xp=np.linspace(0,201,201)
                fp=np.linspace(layer['minvalue'],layer['maxvalue'],201)
                icolor=int(np.interp(this_data, fp, xp))
                if icolor>numColors-1:
                    icolor=numColors-1
                alphaCell=1
                cellColor=cmap[icolor,:]
                cellEdgeColor=[0,0,0]
                
        elif layer['channel']=='RYG':
            #cmap= plt.cm.RdYlGn(range(0, numColors))
            cmap = cm.get_cmap("RdYlGn", 201)
            if this_data==-1:
                alphaCell=0
                cellColor=[0.9,0.9,0.9]
                cellEdgeColor=[0.5,0.5,0.5]
            else:
                cellColor=cmap(1-this_data/np.pi)
                alphaCell=1
                cellEdgeColor=[0.5,0.5,0.5]
        elif layer['channel']=='RelInt':
            colors2=[(100,34,101),(92,204,192),(27,68,28)]
            cmap=make_cmap(colors2, bit=True)
            if this_data==-1:
                alphaCell=0
                cellColor=[0.9,0.9,0.9]
                cellEdgeColor=[0.5,0.5,0.5]
            else:
                cellColor=cmap(1-this_data/np.pi)
                alphaCell=1
                cellEdgeColor=[0.5,0.5,0.5]
                
        elif layer['channel']=='Tracking':
            cellColor=this_data
            cellEdgeColor=[0.5,0.5,0.5]
            alphaCell=.5
            
        else: #Mask
            cellColor=[0,0,0]
            cellEdgeColor=[0,0,0]
            alphaCell=1
            
        #Now draw polygon with overlay 
        if layer['contour']:
            patch = PolygonPatch(this_poly, facecolor=cellColor, edgecolor=cellEdgeColor, alpha=alphaCell, linewidth=.5, zorder=2)
        else:
            patch = PolygonPatch(this_poly, facecolor=cellColor, edgecolor=cellColor, alpha=alphaCell, zorder=2)
        ax.add_patch(patch)
        
    plt.gca().invert_yaxis()
    plt.tight_layout(pad=0,h_pad=0,w_pad=0)
    fig.savefig(fileNameIMAGEOVERLAY)
    #plt.close(fig1)
    plt.clf()
    plt.close(fig)



    
def plot_Raw_flourescence(data1,data2,title,name1,name2,lg,lr):
    fig,ax= plt.subplots( figsize=(10,5))
    
    xm=np.mean(data1)
    ym=np.mean(data2)
    
    ax.scatter(data1,data2,s=5,alpha=.1)
    ax.scatter(xm,ym,c='r')
    #ax.set_aspect('equal')
    ax.grid(True)
    ax.set_xlim(left=0)
    if(lg):
        ax.set_xlim(right=lg)
    ax.set_ylim(bottom=0)
    
    if(lr):
        ax.set_ylim(top=lr)
    
    ax.set_title(title, va='bottom')
    ax.set_xlabel(name1)
    ax.set_ylabel(name2)

    lregGFP=linregress(data1,data2)
    x_vals = np.array(ax.get_xlim())
    y_vals = lregGFP.intercept + lregGFP.slope * x_vals
    ax.plot(x_vals, y_vals, '--g')

    return plt

def plot_polar_fluorescence(datap1,datap2,phimax,phimin,phimean,rhomean,rhomax,title):
    fig= plt.figure( figsize=(10,5))
    ax=fig.add_subplot(111,projection='polar') 
    ax.plot([0,phimin],[0,rhomax])
    ax.plot([0,phimax],[0,rhomax])
    ax.scatter(datap1, datap2,s=5,alpha=.1)
    ax.scatter(phimean,rhomean,c='r',zorder=3)
    ax.set_rmax(rhomax)
    lphimean=np.mean(datap1)
    lrhomean=np.mean(datap2)
    ax.scatter(lphimean,lrhomean,s=30,c='k',zorder=3)
   # ax.grid(True)

    ax.set_title("Polar plot of fluorescence %s"%(title), va='bottom')
    return plt

def plot_phi_hist(lphis,prange,pop):

    fig,ax= plt.subplots( figsize=(5,5))
    #phiden=st.gaussian_kde(lphis)
    #ax.plot(prange,phiden(prange),c='g')
    n,bins,patches=plt.hist(lphis,bins=prange)#,density='true')
    #plt.yscale("log")
   # print(n.std())
   # print(lphis.std())
    #plt.ylim(ymax=lymax)
    ax.set_title("Histogram %s "%(pop), va='bottom')
    ax.set_xlabel("Relative intensity (phis)")
    ax.set_ylabel("Count")
    return plt


    
    

print("loaded!")




