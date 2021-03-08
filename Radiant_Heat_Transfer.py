#sources
#http://gw2jh3xr2c.search.serialssolutions.com/?sid=sersol&SS_jc=TC_027716784&title=2016%20ASHRAE%20Handbook%20-%20Heating%20Ventilating%20and%20Air-Conditioning%20Systems%20and%20Equipment%20%28SI%20Edition%29
import math 
import numpy as np


def Wall_emissivity( T_cs, T_film, trans, absorb, wave_len2, E_cs):
    
    C1 = 3.741695*(10**8) #radiation contants for Planck's distribution
    C2 = 1.438866*(10**4)
    
    E1_through_film = list(range(0, len(trans)))  #emissive power of cold surface per wavelength
    E1_through_film_black = list(range(0, len(trans)))
    for x in E1_through_film:
        E1_through_film [x] = ((C1/((wave_len2[x]**5) * ((math.exp(C2/(wave_len2[x]*T_cs))) -1)))*E_cs)*trans[x] #Emissive power/wavelength for blackbody
        E1_through_film_black [x] = (C1/((wave_len2[x]**5) * ((math.exp(C2/(wave_len2[x]*T_cs))) -1)))*trans[x]
    
    E1_through_film_tot_wall=np.trapz(E1_through_film, wave_len2)
    E1_through_film_black_tot_wall=np.trapz( E1_through_film_black, wave_len2)
    
    
    E_film1 = list(range(0, len(trans)))  #emissive power of film per wavelength 
    E_film_black1 = list(range(0, len(trans)))
    #Creating spectral emissive power from cold panel
    for x in E_film1:
        E_film1 [x] = (C1/((wave_len2[x]**5) * ((math.exp(C2/(wave_len2[x]*T_film))) -1)))*absorb[x] 
        E_film_black1 [x] = (C1/((wave_len2[x]**5) * ((math.exp(C2/(wave_len2[x]*T_film))) -1)))
    
    E_film2 = list(range(0, len(trans)))  #emissive power of film per wavelength 
    E_film_black2 = list(range(0, len(trans)))
    for x in E_film2:
# =============================================================================
#         E_film2 [x] = (C1/((wave_len2[x]**5) * ((math.exp(C2/(wave_len2[x]*T_film))) -1)))*absorb[x]*0.05*(1-absorb[x])
#         E_film_black2 [x] = (C1/((wave_len2[x]**5) * ((math.exp(C2/(wave_len2[x]*T_film))) -1)))*0.05*(1-absorb[x])
# =============================================================================
        E_film2 [x] = (C1/((wave_len2[x]**5) * ((math.exp(C2/(wave_len2[x]*T_film))) -1)))*absorb[x]*0.05*(trans[x])
        E_film_black2 [x] = (C1/((wave_len2[x]**5) * ((math.exp(C2/(wave_len2[x]*T_film))) -1)))*0.05*(trans[x])
    
    E_film_tot_wall1=np.trapz(E_film1, wave_len2)
    E_film_black_tot_wall1=np.trapz(E_film_black1, wave_len2)
    
    E_film_tot_wall2=np.trapz(E_film2, wave_len2)
    E_film_black_tot_wall2=np.trapz(E_film_black2, wave_len2)
    
    #Panel_emmisivity = (E_film_tot_wall1 + E1_through_film_tot_wall)/(E1_through_film_black_tot_wall + E_film_black_tot_wall1)
    Panel_emmisivity = (E_film_tot_wall1 + E1_through_film_tot_wall+E_film_tot_wall2)/(E1_through_film_black_tot_wall + E_film_black_tot_wall1+E_film_black_tot_wall2)

    return Panel_emmisivity, E_film_tot_wall1, E1_through_film_tot_wall, E_film_black_tot_wall1, E1_through_film_black_tot_wall







def Radiant_Transfer_absorption(A_cs, T_cs, T_wall, trans, absorb, wave_len2, E_cs, reflect):
    
        
    #==============================================================================
    ##constants
    #==============================================================================
        
    C1 = 3.741695*(10**8) #radiation contants for Planck's distribution
    C2 = 1.438866*(10**4)
    F_12 = 1 #view factor from cs to wall
    
   
    #===============================================================================  
    #===============================================================================    
    ##E1 (Emission cold panel)
    #===============================================================================
    #===============================================================================  

    E1 = list(range(0, len(trans)))  #emissive power of cold surface per wavelength 
    #Creating spectral emissive power from cold panel
    for x in E1:
        E1 [x] = (C1/((wave_len2[x]**5) * ((math.exp(C2/(wave_len2[x]*T_cs))) -1)))*E_cs #Emissive power/wavelength for blackbody
    E1_tot=np.trapz(E1, wave_len2) #integrates across wavelengths to find total Emission from Cold Panel
    
    
    #==============================================================================
    ##Calculating transmission of E1  through film, ---> G2 (Irradiation on surfaces)
    #==============================================================================
       
    G2 = list(range(0, len(trans)))
    for x in G2:
        G2 [x] = E1 [x]*(trans[x])
    G2_tot=np.trapz(G2, wave_len2) #integrates across wavelengths to find total Irradiance on wall
    
    
    #==============================================================================
    ##Calculating reflected portion of  G2 --->  pG2
    #==============================================================================   
    
# =============================================================================
#     p_wall = 1-E_wall #reflectivity of wall
#     pG2 = list(range(0, len(trans)))
#     for x in pG2:
#         pG2 [x] = G2 [x] * p_wall  
#     pG2_tot=np.trapz(pG2, wave_len2) #integrates across wavelengths to find total energy reflected by cold panel
# =============================================================================
    
    
    ##Calculating second round of absorption
    p_cs = 1-E_cs #reflectivity of cold panel
# =============================================================================
#     pG11 = list(range(0, len(trans)))
#     for x in pG11:
#         pG11 [x] =pG2 [x] *trans[x]*p_cs
#     pG11_tot=np.trapz(pG11, wave_len2) #integrates across wavelengths to find total energy reflected by cold panel
# =============================================================================
    
    
    
    #===============================================================================  
    #===============================================================================     
    ##E2 (Emission wall)
    #===============================================================================  
    #=============================================================================== 
    
    E2 = list(range(0, len(trans)))  #emissive power of wall per wavelength 
    #Creating spectral emissive power from wall
    for x in E2:
        E2 [x] = (C1/((wave_len2[x]**5) * ((math.exp(C2/(wave_len2[x]*T_wall))) -1)))#*E_wall #Emissive power/wavelength for blackbody
    E2_tot=np.trapz(E2, wave_len2) #integrates across wavelengths to find total Emission from wall
    
    #==============================================================================
    ##Calculating transmission of E2  through film, ---> G1 (Irradiation on surfaces)
    #==============================================================================
   
    
    G1 = list(range(0, len(trans)))
    for x in G1:
        G1 [x] = E2 [x]*(trans[x])    
    G1_tot=np.trapz(G1, wave_len2) #integrates across wavelengths to find total Irradiance on cold surface
    
    #==============================================================================
    ##Calculating reflected portion of G1  ---> pG1
    #==============================================================================
  
    pG1 = list(range(0, len(trans)))
    for x in pG1:
        pG1 [x] = G1 [x] * p_cs  
    pG1_tot=np.trapz(pG1, wave_len2) #integrates across wavelengths to find total energy reflected by cold panel
    
    pPanel = list(range(0, len(trans)))   #energy reflected off panel from outside
    for x in pPanel:
        pPanel [x] = (E2 [x] * reflect[x]) + (pG1 [x] * trans[x])
    pPanel_tot=np.trapz(pPanel, wave_len2) #integrates across wavelengths to find total energy reflected by cold panel  

    ##Calculating second round of absorption
# =============================================================================
#     pG22 = list(range(0, len(trans)))
#     for x in pG22:
#         pG22 [x] =pG1 [x] *trans[x]*p_wall
#     pG22_tot=np.trapz(pG22, wave_len2) #integrates across wavelengths to find total energy reflected by cold panel
# =============================================================================


    
    #==============================================================================
    ##Energy Absorbed by film
    #==============================================================================
    
    rad_abs = list(range(0, len(trans))) #energy absorbed by panel per wavelength
    for x in rad_abs:
        #rad_abs [x] = (E1[x] + E2[x] + pG1[x] + pG2[x]) * absorb[x]
        rad_abs [x] = (E1[x] + E2[x] + pG1[x]) * absorb[x]
        
    rad_abs_tot=np.trapz(rad_abs, wave_len2) #total energy flux absorbed (not accounting for surface area)
    Q2 = A_cs * rad_abs_tot
    film_transmissivity = G2_tot / E1_tot
    heat_transfer_on_cold_surface  = A_cs*((E_cs*(G1_tot+(E1_tot*0.05)))-E1_tot)
    Q_netroom1 = A_cs*(E2_tot-pPanel_tot-G2_tot)#net heat transfer between panel and surrounding walls
    Q_netroom_out = A_cs*(G2_tot+pPanel_tot)
    
    return Q2, rad_abs_tot, pG1_tot, G1_tot, G2_tot, E2_tot, E1_tot, film_transmissivity, heat_transfer_on_cold_surface, Q_netroom1, Q_netroom_out






def Radiant_Transfer_emission(A_cs, T_film, trans, absorb, wave_len2, E_cs):

        
    #==============================================================================
    ##constants
    #==============================================================================
        
    C1 = 3.741695*(10**8) #radiation contants for Planck's distribution
    C2 = 1.438866*(10**4)
    
    #==============================================================================
    ##Start of Heat Transfer
    #==============================================================================
    ##Calculating Emissions
    #==============================================================================


    E_film = list(range(0, len(trans)))  #emissive power of cold surface per wavelength 
    E_film_black = list(range(0, len(trans))) #emissive power of cold surface per wavelength if blackbody
    #Creating spectral emissive power from film
    for x in E_film:
        E_film [x] = (C1/((wave_len2[x]**5) * ((math.exp(C2/(wave_len2[x]*T_film))) -1)))*absorb[x]  #Real emissive power per wavelength
        E_film_black [x] = (C1/((wave_len2[x]**5) * ((math.exp(C2/(wave_len2[x]*T_film))) -1)))
    
    ##pG1 irradiance on film from cold surface       
    p_cs = 1-E_cs #reflectivity of cold panel
    pG1 = list(range(0, len(trans)))
    for x in pG1:
        #pG1 [x] = E_film [x] * p_cs 
        pG1 [x] = E_film [x] * p_cs * absorb[x]  
    pG1_tot=np.trapz(pG1, wave_len2) #integrates across wavelengths to find total energy reflected by cold panel
    #==============================================================================
    
    film_ref_out = list(range(0, len(trans)))
    for x in film_ref_out:
        film_ref_out [x] = E_film [x] * p_cs * trans[x]  
    film_ref_out_tot=np.trapz(film_ref_out, wave_len2) #integrates across wavelengths to find total energy reflected by cold panel
    
    
# =============================================================================
#     ##pG2    
#     p_wall = 1-E_wall #reflectivity of wall panel
#     pG2 = list(range(0, len(trans)))
#     for x in pG2:
#         pG2 [x] = E_film [x] * p_wall
#         #pG2 [x] = E_film [x] * p_wall  * absorb[x]  
#     pG2_tot=np.trapz(pG2, wave_len2) #integrates across wavelengths to find total energy reflected by cold panel
# =============================================================================
    
        
        
    E_film_tot=np.trapz(E_film, wave_len2) #integrates across wavelengths to find total Emission from Cold Panel
    E_film_black_tot=np.trapz(E_film_black, wave_len2)
    film_emissivity = E_film_tot /  E_film_black_tot
   
    #Q4 = A_cs * ((2 * E_film_tot) - pG1_tot - pG2_tot)
    Q4 = -1*A_cs * ((2 * E_film_tot) - pG1_tot )
    
    pG1_for_cooling = list(range(0, len(trans)))
    pG1_for_cooling [x] = E_film [x] * p_cs * trans[x]
    Part2_Em_power_for_cooling = E_film_tot + np.trapz(pG1_for_cooling, wave_len2)
    Q_netroom2 = A_cs*(-E_film_tot-film_ref_out_tot)
    Q_netroom_out = A_cs*(E_film_tot+film_ref_out_tot)
    
    heat_transfer_on_cold_surface = A_cs*(E_film_tot*E_cs)
    
    return Q4, E_film_tot, film_emissivity, Part2_Em_power_for_cooling, heat_transfer_on_cold_surface, Q_netroom2, Q_netroom_out
    
    
    
    
    
    
    
    
    
    
    
    
    