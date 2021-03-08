import math 
import numpy as np


def MRT_Panel(P1_Q_PanelOut, A_cs ):

    boltz = (5.670374*10**(-8))
       
    
    
    T_panel1 = (P1_Q_PanelOut/(A_cs*boltz))**(1/4)
      
    

    
    return  T_panel1-273.15