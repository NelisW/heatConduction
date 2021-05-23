# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 23:07:48 2019

@author: RickFu
https://github.com/rickfu415/heatConduction
https://github.com/NelisW/heatConduction

see also Amar2006:
https://repository.lib.ncsu.edu/bitstream/handle/1840.16/2847/etd.pdf
http://web.engr.uky.edu/~acfd/egr537-lctrs.pdf

"""
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd

# try:
#     import cupy as np                    
# except ImportError:
import numpy as np


def evolutionField(results):
    """ Generate 3D temperature fields
    
    For better understanding of the results
    
    Inputs:
        1. parameter, a pandas series
        2. results, a numpy array
    """
    
    X = results.index
    Y = results.columns
    X, Y = np.meshgrid(X, Y)
    
    fig = plt.figure(figsize=(8,6))
    ax = fig.gca(projection='3d')
    ax.set_xlabel('x, m')
    ax.set_ylabel('Time, s')
    ax.set_zlabel('Temperature, K')
    Z = results.T.values
    ax.plot_surface(X, Y, Z, 
                    cmap=cm.seismic,
                    linewidth=0, 
                    antialiased=False)
    plt.show()



def thermalCouplePlot(results, positions):
    """ Generate x-y plots as thermo-couple data
    
    Inputs:
        1. results, a pandas DataFrame
        2. Positions, a list of positions of the generated
           grids.

    """
    
    df = results.loc[positions,:]
    df = df.T
    df = df.add_prefix('x = ')
    df = df.add_suffix(' m')
    ax = df.plot(grid=True)
    ax.set_xlabel("Time, s")
    ax.set_ylabel("Temperature, K")



def temperatureDistribution(results, times):
    """ Generate temperature distribution at different times
    
    Inputs:
        1. results, a pandas DataFrame
        2. times, a list of timings on the calculated 
           time steps
    """
    
    df = results.loc[:,times]
    df = df.add_prefix('t = ')
    df = df.add_suffix(' s')
    ax = df.plot(grid=True)
    ax.set_xlabel("x, m")
    ax.set_ylabel("Temperature, K")

def preprocess(parameter, results):
    """ Pre-Process results
    
    To convert numpy array into pandas DataFrame for easier
    data processing.
    
    Input:
        1. Generated parameter serie
        2. results as a numpy array
    
    Return:
        A pandas DataFrame with index as times and 
        columns as grid positions
    """
    
    length = parameter['length']
    numberOfNode = int(parameter['numberOfNode'])
    numOfTimeStep = int(parameter['numberOfTimeStep'])
    deltaTime = parameter['deltaTime']
    time = deltaTime * numOfTimeStep
    grids = np.linspace(0, length, numberOfNode).round(5)
    times = np.linspace(0, time, numOfTimeStep+1).round(5)
    df = pd.DataFrame(results, 
                      index = grids, 
                      columns = times)
    return df


def plotsummary(results, positions,deciX=1,deciY=1,title='',savefile=None):
    """ Plot results 

    Inputs:
        1. results, a pandas DataFrame
        2. Positions, a list of depth positions
        3. use every deciX sample along depth
        4. use every deciY sample along time
        5. title for the plots
        6. save file name
        
    """
    import pyradi.ryplot as ryplot
    from matplotlib import cm
    
    df = results.loc[positions,:]
    
    Z = results.T.values

    Z = Z[:-1:deciY,:-1:deciX]
    Xv = np.asarray(results.index[0:-1:deciX])
    Yv = np.asarray(results.columns[0:-1:deciY])

    maxtime = np.max(Yv)
    if maxtime > 50*24*60*60:
        timeStr = 'Time Years'
        Yv = Yv / (365.25*24*60*60)
    elif maxtime > 20*24*60*60:
        timeStr = 'Time Weeks'
        Yv = Yv / (7*24*60*60)
    elif maxtime > 3*24*60*60:
        timeStr = 'Time Days'
        Yv = Yv / (24*60*60)
    elif maxtime > 3*60*60:
        timeStr = 'Time Hours'
        Yv = Yv / (60*60)
    elif maxtime > 3*60:
        timeStr = 'Time Minutes'
        Yv = Yv / (60)
    else :
        timeStr = 'Time Seconds'

    X, Y = np.meshgrid(Xv, Yv)
    samples = df.values[:,0:-1:deciY]

    p = ryplot.Plotter(1,1,1,figsize=(10,16),doWarning=False)
    p.mesh3D(1,X,Y,Z,title,'Depth m',timeStr,'Temperature K',xInvert=True,yInvert=True,cmap=cm.seismic)
    if savefile is not None:
        fname = savefile.replace('.png','-3D.png')
        p.saveFig(f'{fname}')
    
    miny = np.min(samples)
    maxy = np.max(samples)
    q = ryplot.Plotter(2,1,1,figsize=(10,6),doWarning=False)
    for ix,(index, row) in enumerate(df.iterrows()):
        q.plot(1,Yv,samples[ix,:],title,timeStr,'Temperature K',
               pltaxis=[0,np.max(Yv),miny,maxy],label=[f'depth={positions[ix]:0.2f} m'],xAxisFmt='%.2f',maxNX=11)
    if savefile is not None:
        fname = savefile.replace('.png','-T.png')
        q.saveFig(f'{fname}')




if __name__ == "__main__":
    global para, results
    test = preprocess(para, results)
    evolutionField(test)
    positions = [0, 0.002, 0.004, 0.006, 0.008, 0.01]
    thermalCouplePlot(test, positions)
    times = [0, 2, 4, 6, 8, 10]
    temperatureDistribution(test, times)
    
    
    
    
    
    
    
    
    
    
    
    
    