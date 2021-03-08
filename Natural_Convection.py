#Fundamentals of heat and mass transfer pg. 561
from scipy import constants
from CoolProp.CoolProp import PropsSI, HAPropsSI

def Nat_Conv_PanelInterior(A_cs, T_cs, T_film, S, orientation, panel_height, h_int_err, B_err, u_err, p_err, a_err, k_err_int):

   #T_cs = 273 #surface tmeperature
   #T_film = 300 #film temperature
         
    Interior_air_temp = float((T_cs + T_film)/2)
    
    B = B_err*PropsSI('isobaric_expansion_coefficient','P',101325,'T',Interior_air_temp,'air') #volumetric thermal expansion coefficient [1/k]
    u = u_err*PropsSI('viscosity','P',101325,'T',Interior_air_temp,'air') #Dynamic  viscosity [Pa*s]
    p = p_err*PropsSI('DMASS','P',101325,'T',Interior_air_temp,'air') #density [kg/m^3]
    v = u/p  #kinematic viscosity
    a = a_err*(((5.68172*(10.0**(-17.0)))* (Interior_air_temp**4.0))-((1.76304*(10.0**(-13.0)))*(Interior_air_temp**3.0))+((2.81311*(10.0**(-10.0)))*(Interior_air_temp**2.0))+((1.03147*(10.0**(-8.0)))*Interior_air_temp)-(1.47967*(10.0**(-6.0))))  #thermal diffusivity [m2/s]
    k= k_err_int*PropsSI('conductivity','P',101325,'T',Interior_air_temp,'air') #thermal conductivity [W/m k]
    g = constants.g
    #S = 0.2 #characteristic length (distance between panels [m])
    
    
    Ra_S = (g*B*(T_film - T_cs)*(S**3))/(v*a)
    Pr = v/a
    
    
    if orientation ==0: #for verticle panels   
       
         
        
        #if 10<panel_height/S<40 and 1<Pr<2*10**4 and 10**4<Ra_S < 10**7:
        if Ra_S < 10**7:   
            Nu_L = (0.42*(Ra_S**0.25))*(Pr**0.012)*((panel_height/S)**(-0.3))   
       
        
       # elif  10**7<Ra_S < 10**9:
        else:
            Nu_L = 0.046*(Ra_S**0.33)
            
# =============================================================================
#        # else:  
#        # elif 2<panel_height/S<10 and Pr<10 and Ra_S < 10**10:
#             Nu_L = (0.22*((panel_height/S)**(-0.25)))*  (((Pr/(0.2+Pr))*Ra_S)**(0.28))
# =============================================================================
            
# =============================================================================
#         else:
#             Nu_L =  0.18* ((Pr/(0.2+Pr))*Ra_S)**0.29
# =============================================================================
        
        
        
        
        
        
    else:               #horizontal panel
        Nu_L = 0.069*(Ra_S**(1/3))*(Pr**0.074)
        
    h_PanelInterior = (Nu_L*k/S)*h_int_err
    Q3_NCIn =  h_PanelInterior*A_cs*(T_cs - T_film) #Q3_NCIn = total heat transfer (W) Natural Convection Interior
           
    return Q3_NCIn, Ra_S, h_PanelInterior




def Nat_Conv_PanelExterior(A_cs, P_cs, T_film, T_air, RH, orientation, panel_height, panel_width, wind, h_ext_err, B_err, u_err, p_err, a_err, k_err_ext):
    
    T_air = float(T_air)
    
    B = B_err*PropsSI('isobaric_expansion_coefficient','P',101325,'T',T_air,'air')#volumetric thermal expansion coefficient [1/k]
    u = u_err*HAPropsSI('Visc','P',101325,'T',T_air,'R', RH) #Dynamic  viscosity [Pa*s]
    #u = PropsSI('viscosity','P',101325,'T',T_air,'air') #Dynamic  viscosity [Pa*s]
    p = p_err*PropsSI('DMASS','P',101325,'T',T_air,'air') #density [kg/m^3]
    v = u/p  #kinematic viscosity
    a = a_err*(((5.68172*(10.0**(-17.0)))* (T_air**4.0))-((1.76304*(10.0**(-13.0)))*(T_air**3.0))+((2.81311*(10.0**(-10.0)))*(T_air**2.0))+((1.03147*(10.0**(-8.0)))*T_air)-(1.47967*(10.0**(-6.0))))  #thermal diffusivity [m2/s]
    #k = PropsSI('conductivity','P',101325,'T',T_air,'air') #thermal conductivity [W/m k]
    k = k_err_ext*HAPropsSI('K','P',101325,'T',T_air,'R', RH) #thermal conductivity [W/m/k]
    g = constants.g
    
    



    if orientation ==0: #for verticle panels
        
        
        
        L = panel_height #characteristic length
        Gr_L = (g*B*(T_air - T_film)*(L**3))/(v**2)
        Pr = v/a
        Ra_L = Gr_L*Pr
        n = 0.7
        
        Re_L = (p*wind*panel_width)/u
        Nu_L_force=0.664*(Pr**(1/3))*(Re_L**(1/2))
        
        #UWT
        Nu_L_nat = (0.825+   ((0.387*(Ra_L**(1/6)))  /   ((1+ ((0.492/Pr)**(9/16))    )**(8/27))))**2
        Nu_L=((Nu_L_nat**n)+(Nu_L_force**n))**(1/n)
        
        if 0.99< abs(Nu_L/ Nu_L_force)<1.01:
            Nu_L = Nu_L_force
            
        if 0.99< abs(Nu_L/ Nu_L_nat)<1.01:
            Nu_L = Nu_L_nat            
        
# =============================================================================
#         #UHF
#         Nu_L = 0.55 *  Ra_L**(1/5)
# =============================================================================


    else: #horiztonal panel
        L = A_cs / P_cs #characteristic length
        Gr_L = (g*B*(T_air - T_film)*(L**3))/(v**2)
        Pr = v/a
        Ra_L = Gr_L*Pr
        Re_L = 0
        n = 3


        #UWT
        if Ra_L<10**7:
            Nu_L_nat = 0.54*Ra_L**0.25
        else:
            Nu_L_nat = 0.15*Ra_L**(1/3)
        
        Re_L = (p*wind*panel_width)/u
        Nu_L_force=0.664*(Pr**(1/3))*(Re_L**(1/2))
        Nu_L=((Nu_L_nat**n)+(Nu_L_force**n))**(1/n)
        
        if 0.99< abs(Nu_L/ Nu_L_force)<1.01:
            Nu_L = Nu_L_force
            
        if 0.99< abs(Nu_L/ Nu_L_nat)<1.01:
            Nu_L = Nu_L_nat 
      
# =============================================================================
#         #UHF
#         if Ra_L>5*10**8:  
#             0.13*Ra_L**(1/3)
#         if Ra_L<5*10**8:
#             0.16*Ra_L**(1/3)
# =============================================================================

        
    h_PanelExterior = (Nu_L*k/L)*h_ext_err
    Q1_NCEx =  h_PanelExterior*A_cs*(T_air - T_film) #Q1_NCEx = total heat transfer (W) Natural Convection Exterior
    
    return Q1_NCEx, Ra_L, Pr, h_PanelExterior, Re_L










