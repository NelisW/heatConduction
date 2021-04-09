# 1D Heat Conduction Solver 
A transient 1D heat conduction solver using Finite Difference Method and implicit backward Euler time scheme.  

## Updates (08-24-2019)
Added a Jupyter notebook as a demo case for the solver. Very straight forward and the results are beautifully plotted. Enjoy!

## Features:  
    1. Fully modularized, easy to customize for your own problem.  
    1. Only use the common packages, Numpy, Pandas and Matplotlib.  
    2. Centered Differecing in space (second order accuracy), implicit backward Euler time scheme (First order accuracy).  
    3. Using Newton's method to solve discretized equation system at each time step.  
    4. Two types of boundary conditions, fixed temperature and fixed heat flux.  
    5. Current version only support constant material properties, will be upgraded.  
    6. Incoporate with postprocessing module and analytic solution comparison.   

## How to run:  
    0. Clone the repository.  
    1. In any Python IDE, open parameter.py, execute.  
    2. To compare with analytic solution, open analyticSolution.py, execute.  
    
## Reference:
1. [Numerical analysis](http://web.engr.uky.edu/~acfd/egr537-lctrs.pdf).
2. [Modeling of One-Dimensional Ablation with Porous Flow using Finite Control Volume Procedure](http://www.lib.ncsu.edu/resolver/1840.16/2847).

## Citation:
If you are using the code for your research or study, please consider cite me :) I am a miserable PhD ......
1. [Thermomechanical Coupling for Charring Ablators](https://doi.org/10.2514/1.T5194).
2. [Thermal Expansion for Charring Ablative Materials](https://doi.org/10.2514/1.T5718).


## Updates 20210409 (CJW)

1. Changed the files to allow temporal changes to boundary conditions

1. Added the option to do radiative heat loss on surface at x=0.

2. Changed the notebook to do more examples, also of temporal changes.

3. Many other minor updates.

