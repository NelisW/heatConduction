# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 22:41:22 2019

@author: RickFu 
https://github.com/rickfu415/heatConduction
https://github.com/NelisW/heatConduction

see also Amar2006:
https://repository.lib.ncsu.edu/bitstream/handle/1840.16/2847/etd.pdf

"""
import postprocessing as pp
import heatConduction as hc
import pandas as pd


def main():
    """ Generate parameter
    
    1. Generate system-level parameters
    2. Generate material properties, grid, time, bcs
    
    Return: a Pandas series
    """
    
    column = 'values'
    df = pd.Series(name = column,dtype='object')
    
    # Material
    df.at['material'] = 'steel'
    df.at['material function'] = 'constant'
    df.at['density'] = 7850
    df.at['conductivity'] = 60.5
    df.at['heatCapacity'] = 434
    
    # Grid
    df.at['length'] = 0.05
    df.at['numberOfNode'] = 501
    
    # Solution
    df.at['numberOfTimeStep'] = 50#400
    df.at['deltaTime'] = 0.2
    df.at['maxIteration'] = 20
    df.at['convergence'] = 1E-10
    df.at['relaxation'] = 1 # value in [0-1] Very sensitive!!!
    
    # Initial conditions
    df.at['Initial value'] = 298.
    
    # Boundary conditions
    df.at['x=0 type'] = 'heatFlux'#'heatFlux' W/m2  or 'fixedTemperature' K
    df.at['x=0 value'] = 750000 
    df.at['x=L type'] = 'heatFlux'#'heatFlux' W/m2  or 'fixedTemperature' K
    df.at['x=L value'] = 0.

    return df



if __name__ == "__main__":
    parameter = main()
    results, cache = hc.solve(parameter)
    T = pp.preprocess(parameter, results)
    pp.evolutionField(T)
    positions = [0, 0.002, 0.004, 0.006, 0.008, 0.01]
    pp.thermalCouplePlot(T, positions)
    times = [0, 2, 4, 6, 8, 10]
    pp.temperatureDistribution(T, times)
    
    
    
    
    