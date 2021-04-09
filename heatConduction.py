# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 12:15:28 2019

@author: RickFu 
https://github.com/rickfu415/heatConduction
https://github.com/NelisW/heatConduction

see also Amar2006:
https://repository.lib.ncsu.edu/bitstream/handle/1840.16/2847/etd.pdf

"""
import numpy as np
import pandas as pd
# import cupy as np
import parameter
import utility
import time

##########################################################################
def initialize(para):
    """ Initialize key data

    done only once at the start of solve
    
    T: current step temperature
    T0: last step temperature
    TProfile: temperature results in time and space
    F: B as right hand side of Ax = B
    Jacobian: A as left had side of Ax = B
    
    Return: a dictionary
    """
    
    numberOfNode = int(para['numberOfNode'])
    numOfTimeStep = int(para['numberOfTimeStep'])
    Tic = para['Initial value']
    T = np.full((numberOfNode, 1), Tic)
    T0 = np.full((numberOfNode, 1), Tic)
    TProfile = np.zeros((numberOfNode, numOfTimeStep + 1))
    F = np.zeros((numberOfNode, 1))
    Jacobian = np.zeros((numberOfNode, numberOfNode))
    TProfile[:,0] = T.reshape(1,-1)
    cache = {'T':T,'T0':T0,'TProfile':TProfile,
             'F':F,'Jacobian':Jacobian,
             'Log':pd.DataFrame()}
    return cache


#######################################################################
def assemble(para, cache):
    """ Assemble linear system Jacobian * dx = F

    Done in each iteration in newton solver
    
    Process:
        0. Obtain relevant information
        1. Loop over grid:
            1.1 Deal with boundary condition node at x=0
            1.2 Deal with boundary condition node at x=L
            1.3 Deal with interior nodes
            1.4 Obtain values on imaginary nodes (Ug1 and Ug2)
                for the two boundary conditions
            1.4 Assemble Jacobian (a diagonal matrix)
        2. Calculate temperature gradient dT2
        3. Assemble F
    
    Return: dictionary containing cache data
    """
    
    dt = para['deltaTime']
    numberOfNode = int(para['numberOfNode'])
    timeStep = cache['ts']
    currentTime = (cache['ts'] - 1) * dt
    
    dx = para['length'] / (numberOfNode -1)
    
    # boundary conditions
    if para['Do radiative']:
        radLoss = para['Emissivity'] * 5.67e-8 * cache['T'][0] ** 4
    else:
        radLoss = 0

    valueX0 = para['x=0 value'][timeStep-1] - radLoss
    valueXL = para['x=L value'][timeStep-1]

    # Containers
    T = cache['T']
    T0 = cache['T0']
    F = cache['F']
    Jacobian = cache['Jacobian']
    
    # Calculate analytic jacobian element
    temp1 = 1 + 2 * para['diffusivity']  * dt / (dx**2)
    temp2 = - para['diffusivity']  * dt / (dx**2)
    
    # Loop over grid
    for i in range(0, numberOfNode):
        # boundary condition node at x=0
        if i == 0:
            if para['x=0 type'] == 'heatFlux':
                Ug1 = utility.fixedGradient(valueX0, para['conductivity'], dx, T[1])
                Jacobian[0][1] = temp2 * 2
            elif para['x=0 type'] == 'fixedTemperature':
                Ug1 = utility.fixedValue(valueX0, T[1])
                Jacobian[0][1] = 0
        # boundary condition node at x=L
        elif i == numberOfNode-1:
            if para['x=L type'] == 'heatFlux':
                Ug2 = utility.fixedGradient(valueXL, para['conductivity'], dx, T[-2])
                Jacobian[-1][-2] = temp2 * 2
            elif para['x=L type'] == 'fixedTemperature':
                Ug2 = utility.fixedValue(valueXL, T[-2])
                Jacobian[-1][-2] = 0
        # Interior nodes
        else:
            Jacobian[i][i+1] = temp2
            Jacobian[i][i-1] = temp2
        Jacobian[i][i] = temp1
    
    # Calculate F (right hand side vector)
    d2T = utility.secondOrder(T, dx, Ug1, Ug2)
    F = T - T0 - para['diffusivity']  * dt * d2T # Vectorization
    
    # Store in cache
    cache['F'] = -F
    cache['Jacobian'] = Jacobian

    return cache

def solveLinearSystem(para, cache):
    """ Solve Ax=B
    
    Process:
        1. Get A = Jacobian matrix (Jacobian)
        2. Get B = Right hand side equation (F)
        3. Calculate dT
        4. Update T
        5. Store in cache
        
    Return: a dictionary
    """
    relax = para['relaxation']
    A = cache['Jacobian']
    B = cache['F']
    dT = np.linalg.solve(A, B)
    T = cache['T']
    T = dT * relax + T
    cache['T']=T
    cache['dT'] = dT
    return cache


def storeUpdateResult(cache):
    """ Store results
    Update T0
    Store temperaure results into a dataframe and 
    save it in the cache.
    """
    
    timeStep = cache['ts']
    TProfile = cache['TProfile']
    T = cache['T']
    cache['T0'] = T.copy()
    TProfile[:,timeStep] = T.reshape(1,-1)
    return cache


def newtonIteration(para, cache):
    """ Newton's Iteration for Equation System
    
    Process:
        1. Get max iteratino, convergence limit
        2. Call assemble function to get Jacobian and F(RHS)
        3. Solve for dT, update solution
        4. Evaluate F, get value of 2-norm
        5. If solution converged, break, output to screen and
           return cache.
    
    """
    
    maxIteration = int(para['maxIteration'])
    convergence = para['convergence']
    dt = para['deltaTime']
    log = cache['Log']
    ts = cache['ts']
    for n in range(maxIteration):
        cache = assemble(para, cache)
        F = cache['F']
        norm = np.linalg.norm(F)
        if norm < convergence:
            log.loc[ts,'PhysicalTime'] = dt*ts
            log.loc[ts,'Iteration'] = n+1
            log.loc[ts,'Residual'] = norm
            break
        cache = solveLinearSystem(para, cache)

    if para['showProg']:
        print(' [','{:3.0f}'.format(ts), ']',
            ' [','{:6.2f}'.format(ts*dt),']',
            ' [','{:2.0f}'.format(n+1), ']',
            ' [','{:8.2E}'.format(norm),']')

    return cache


def solve(para):
    """ Main function to solve heat conduction
    
    Input: a Pandas series containing all parameters
    
    Process:
        1. Initialize cache
        2. Time marching 
        3. Newton's iteration for discretized PDE for singe time 
           step
        4. Update T, save result to T profile
    
    Return: temperature profile as final result
    """
    
    if para['showProg']:
        print(" Heat Conduction Solver")
    start = time.time()
    cache = initialize(para)
    numOfTimeStep = int(para['numberOfTimeStep'])
    if para['showProg']:
        print(' [Step] [Physical Time] [Iteration] [Residue]')
    for timeStep in range(1, numOfTimeStep+1):
        cache['ts'] = timeStep
        cache = newtonIteration(para, cache)
        cache = storeUpdateResult(cache)
    TProfile = cache['TProfile']
    runtime = time.time() - start
    if para['showProg']:
        print('[Cost] CPU time spent','%.3f'%runtime,'s')
    return TProfile, cache



if __name__ == "__main__":
    para = parameter.main()
    results, cache = solve(para)
    

