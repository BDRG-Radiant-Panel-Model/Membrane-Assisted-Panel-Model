from Radiant_Heat_Transfer import Radiant_Transfer_absorption, Radiant_Transfer_emission, MRT_Panel
from Natural_Convection import Nat_Conv_PanelInterior, Nat_Conv_PanelExterior
import math 
import pandas as pd
from decimal import Decimal
import xlsxwriter 
import numpy as np


#model performance
deltaT = 0.05   #lower number will produce more precise results, but will increase run time
orientation = 0 #0 for vertical panel, 1 for horizontal

#Panel Paramaters
panel_height = 2.1  #[m]
panel_width = 1.2   #[m]
#S = 0.15 #characteristic length (distance between cold panel and film [m])
S = 1.5 #characteristic length (distance between cold panel and film [m])
#thick_film_2 = 0.001 #thickness of the film for panel design [m]
thick_film_2 = 0.00005 #thickness of the film for panel design [m]
E_cs = 0.95

U_value_ins = 0.63 #W/m^2k


#Environmental Paramaters
T_cs = [17.5, 8.1, 15.9, 10.6, 13.39, 13.7, 12, 14.67, 13.3] # [all temps in degrees C] Cold surface temperature 
T_wall = [25.398, 19.037, 24.315, 20.729, 22.617, 22.826, 21.676, 23.483, 22.556] #Denon Regression - temperature of prticipating wall (MRT)
T_air = [26.8, 31.1, 31.5, 30, 30.1, 29.3, 29.1, 29.46, 30.97] #air temperature surrounding the panel 
RH = [0.8467, 0.6405, 0.7269, 0.6618, 0.7116, 0.7407, 0.7184, 0.7625, 0.7299]
Real_Mem_Temp = [24, 23.5, 26, 23, 24.3, 24.2, 23.5, 24.84, 25.56]

wind = 0.3



# =============================================================================
# #to sumulate using your own model inputs, comment out previus model input and uncomment below
# T_cs = [50]  
# T_wall = [0]  
# T_air = [0] 
# RH = [0.888]
# Real_Mem_Temp = [24.0]
# 
# wind = 0.8
# =============================================================================




# =============================================================================
# #Calibration - vertical panel - orig
# err_inc = 1.0
# h_int_err = err_inc*0.6047
# h_ext_err = err_inc*1.497
# em_cs_err = err_inc
# Trans_error = err_inc*0.899
# T_cs_err = err_inc
# T_ss_err = err_inc*1.018
# T_air_err = err_inc
# B_err = err_inc
# u_err = err_inc
# p_err = err_inc
# a_err = err_inc
# k_err_int = err_inc*0.9925
# k_err_ext = err_inc*1.160
# wind_err = err_inc
# n_err = 3
# =============================================================================


#Calibration - vertical panel - new
err_inc = 1.0
h_int_err = err_inc*0.981474747
h_ext_err = err_inc*1.082080808
em_cs_err = err_inc
Trans_error = err_inc*0.864969697
T_cs_err = err_inc
T_ss_err = err_inc*1.013050505
T_air_err = err_inc
B_err = err_inc
u_err = err_inc
p_err = err_inc
a_err = err_inc
k_err_int = err_inc
k_err_ext = err_inc*1.039676768
wind_err = err_inc
n_err = 0.705393939





# =============================================================================
# #Horizontal panel
# err_inc = 1.0
# h_int_err = err_inc
# h_ext_err = err_inc
# em_cs_err = err_inc
# Trans_error = err_inc
# T_cs_err = err_inc
# T_ss_err = err_inc
# T_air_err = err_inc
# B_err = err_inc
# u_err = err_inc
# p_err = err_inc
# a_err = err_inc
# k_err_int = err_inc
# k_err_ext = err_inc
# wind_err = err_inc
# n_err = 3
# =============================================================================


#Variables for radiant heat transfer


thick_film_1 = 0.00005 # * Dont change unless data changes * thickness of film used for ftir data [m]

E_cs = E_cs * em_cs_err #emissivity of cold surface 

#Variables for convective heat transfer
wind = wind * wind_err

#==============================================================================


data1 = pd.read_excel (r"C:\Users\denon\Documents\GitHub\Membrane-Assisted-Panel-Model\Basic_Model\Transmission_Membrane_coldtube.xlsx") #reading in FTIR values from excel sheet
trans1 = pd.DataFrame(data1, columns=['trans']) #seperating transmissivity data
trans = list(range(0, len(trans1)))#creating list for transmissivity values  
for x in trans:   #calculating new transmissivity for each wavelength
    if trans1.iloc[x][0]!= 0:
        abs_cof_temp =  math.log(trans1.iloc[x][0])/thick_film_1 #calculating absorption coefficient (Beer's Law)
        trans[x] = Trans_error * math.exp(abs_cof_temp*thick_film_2)  #Beer's law again (broken up for debugging)      
    else:
        trans[x]=0
data2 = pd.read_excel (r"C:\Users\denon\Documents\GitHub\Membrane-Assisted-Panel-Model\Basic_Model\Reflection_Membrane_coldtube.xlsx") #reading in FTIR values from excel sheet
reflect1 = pd.DataFrame(data2, columns=['ref']) #seperating reflectivity data
reflect = list(range(0, len(reflect1)))#creating list for reflection values
for x in reflect:
    reflect[x] = reflect1.iloc[x][0] #making a list because I didn't want to use data frames for some reason
absorb = list(range(0, len(trans1)))
for x in absorb:
    absorb[x] = 1 - trans[x] -  reflect[x]

wave_len1 = pd.DataFrame(data1, columns=['wavelength']) #wavelengths considered
wave_len2 = list(range(0, len(trans1)))
for x in wave_len2:
    wave_len2[x] = wave_len1.iloc[x][0]
    
#==============================================================================
A_cs = panel_height*panel_width #area of cold panel [m]
P_cs = (panel_height*2)+(panel_width*2) #perimeter of cold panel [m]


T_cs_counter = 0 #because the cold surface, mrt, and air values are already set, these lists are iterated using a counter
T_cs = [(x*T_cs_err) + 273.15 for x in T_cs] #changes all temperatures from calcius to kelvin
T_wall = [(x*T_ss_err) + 273.15 for x in T_wall]
T_air = [(x*T_air_err) + 273.15 for x in T_air]
All_film_temps = list(range(0, len(T_cs))) #creates a list for the solved film temp for each combination of inital variables
All_ColdSurface_Qs = list(range(0, len(T_cs)))

All_QnetroomRadcooling = list(range(0, len(T_cs)))
All_QnetroomRadother = list(range(0, len(T_cs)))
NaturalConvectionPanelinterior = list(range(0, len(T_cs)))

All_Conv_ext_h= list(range(0, len(T_cs)))
All_Conv_int_h= list(range(0, len(T_cs)))
All_K_ext= list(range(0, len(T_cs)))
Panel_temps =  list(range(0, len(T_cs)))
Rear_Conduction =  list(range(0, len(T_cs)))
All_Trans =  list(range(0, len(T_cs)))



for y in T_cs:


    if T_wall[T_cs_counter] >= T_air[T_cs_counter] and T_wall[T_cs_counter] >= T_cs[T_cs_counter]: #deciding what range of potential film temperatures need to be iterated through
        temp_high = T_wall[T_cs_counter]
   
    elif T_air[T_cs_counter] >= T_wall[T_cs_counter] and T_air[T_cs_counter] >= T_cs[T_cs_counter]:
        temp_high = T_air[T_cs_counter]
        
    else :
        temp_high = T_cs[T_cs_counter]
    
    
    if T_wall[T_cs_counter] <= T_air[T_cs_counter] and T_wall[T_cs_counter] <= T_cs[T_cs_counter]: #deciding what range of potential film temperatures need to be iterated through
        temp_low = T_wall[T_cs_counter]
   
    elif T_air[T_cs_counter] <= T_wall[T_cs_counter] and T_air[T_cs_counter] <= T_cs[T_cs_counter]:
        temp_low = T_air[T_cs_counter]
        
    else:
        temp_low = T_cs[T_cs_counter]
        
    
    resolution = int((temp_high-temp_low)/deltaT) #higher number means more precise temperature but takes longer
    
    T_film = list(range(resolution)) #each of these lists are for storing data for one combination of variales, it gets reset after each combination has been iterated
    energy_balance = list(range(resolution))
    e_wall = list(range(resolution))
    wall_e_film = list(range(resolution))
    wall_e_cs = list(range(resolution))
    wall_e_film_black = list(range(resolution))
    wall_e_cs_black = list(range(resolution))
    Q1 = list(range(resolution))
    Q2 = list(range(resolution))
    Q3 = list(range(resolution))
    Q4 = list(range(resolution))
    film_emissivity = list(range(resolution))
    Conv_ext_Ra = list(range(resolution))
    Conv_ext_Re = list(range(resolution))
    Conv_int_Ra = list(range(resolution))
    
    Pr_val = list(range(resolution))
    cooling_part1= list(range(resolution))
    cooling_part2= list(range(resolution))
    h_int= list(range(resolution))
    h_ext= list(range(resolution))
    K_ext_Re= list(range(resolution))
    
    Q_radEmi_cs = list(range(resolution))
    Q_radAbs_cs = list(range(resolution))
    Q_netroom1 = list(range(resolution))
    Q_netroom2 = list(range(resolution))
    Q_netroom_out1 = list(range(resolution))
    Q_netroom_out2 = list(range(resolution))
    
    
    
    min_energy_balance = 10000 #just setting it to a large number, the combination that minamizes this value is the solution
    
    for x in energy_balance:  #the section that iterates through one variable combination to find the silution
        T_film[x] = temp_low + (deltaT * x)
        
        
        Conv_ext = Nat_Conv_PanelExterior(A_cs, P_cs, T_film[x], T_air[T_cs_counter], RH[T_cs_counter], orientation, panel_height, panel_width, wind, h_ext_err, B_err, u_err, p_err, a_err, k_err_ext, n_err)
        Q1[x] = Conv_ext[0]
        Conv_ext_Ra[x] = Conv_ext[1]
        Pr_val [x]=Conv_ext[2]
        h_ext[x] = Conv_ext[3]
        Conv_ext_Re[x]=Conv_ext[4]
        K_ext_Re[x]=Conv_ext[5]
        
        Rad_abs = Radiant_Transfer_absorption (A_cs, T_cs[T_cs_counter], T_wall[T_cs_counter], trans, absorb, wave_len2, E_cs, reflect)
        Q2[x] = Rad_abs[0]
        #cooling_part1[x] =  Rad_abs[5]
        Q_radAbs_cs[x] = Rad_abs[8]
        Q_netroom1[x] = Rad_abs[9]
        Q_netroom_out1 [x] = Rad_abs[10]
        
        Conv_int = Nat_Conv_PanelInterior(A_cs, T_cs[T_cs_counter], T_film[x], S, orientation, panel_height, h_int_err, B_err, u_err, p_err, a_err, k_err_int)
        Q3[x] =  Conv_int[0]
        Conv_int_Ra[x] = Conv_int[1]
        h_int[x] = Conv_int[2]
        
        Rad_emi = Radiant_Transfer_emission(A_cs, T_film[x], trans, absorb, wave_len2, E_cs)
        Q4[x] = Rad_emi[0]
        film_emissivity [x] = Rad_emi[2]
        cooling_part2[x] =Rad_emi[3]
        Q_radEmi_cs[x] =Rad_emi[4]
        Q_netroom2[x] = Rad_emi[5]
        Q_netroom_out2 [x] = Rad_emi[6]
         
        
        energy_balance [x] = abs(Q1[x] + Q2[x] + Q3[x] + Q4[x])
       
       
        if energy_balance [x] < min_energy_balance:
            min_energy_balance = energy_balance [x]
            min_energy_balance_location = x
    
    All_ColdSurface_Qs [T_cs_counter] = round( Q_radAbs_cs[min_energy_balance_location] + Q_radEmi_cs[min_energy_balance_location] - Q3[min_energy_balance_location]       ,3)
    All_film_temps[T_cs_counter] = round(T_film[min_energy_balance_location],3)
    Q_netroom_rad = Q_netroom1[min_energy_balance_location] + Q_netroom2[min_energy_balance_location]
    ColdSurface_Q  =  Q_radAbs_cs[min_energy_balance_location] + Q_radEmi_cs[min_energy_balance_location] - Q3[min_energy_balance_location]
    Q_netroom_out = Q_netroom_out1[min_energy_balance_location] + Q_netroom_out2[min_energy_balance_location]
    Panel_temps [T_cs_counter] = MRT_Panel(Q_netroom_out, A_cs )
    
    All_QnetroomRadcooling [T_cs_counter] = round(Q_netroom_rad, 3)
    All_QnetroomRadother [T_cs_counter] = round(ColdSurface_Q - Q_netroom_rad+round(Q3[min_energy_balance_location], 3), 3)
    NaturalConvectionPanelinterior [T_cs_counter] = -1*round(Q3[min_energy_balance_location], 3)
    
    All_Conv_ext_h [T_cs_counter] = round(h_ext[min_energy_balance_location],3)
    All_Conv_int_h [T_cs_counter] = round(h_int[min_energy_balance_location], 3)    
    All_Trans [T_cs_counter] =  round(Rad_abs[7], 3)
    All_K_ext[T_cs_counter] =  round(K_ext_Re[min_energy_balance_location], 3) 

    
    Rear_Conduction [T_cs_counter] = U_value_ins*A_cs*abs(T_cs[T_cs_counter]-T_air[T_cs_counter])
    
    print("--------------------------------------------------------------------")
    
    print("Membrane Temperature:", round(T_film[min_energy_balance_location],3), "[K]",round(T_film[min_energy_balance_location]-273.15, 3), "[C]")
 
    #print("Cooling power:",  round((cooling_part1[min_energy_balance_location]+ cooling_part2[min_energy_balance_location])/1000,3), "[W]")
    print("Radiant Panel Temperature:",  Panel_temps[T_cs_counter], "[C]")


    print("")
    print("Chilled Surface Temperature:", round(T_cs[T_cs_counter],3), "[K]", round(T_cs[T_cs_counter]-273.15, 3), "[C]" )
    print("Surrounding Surface Temperature:", round(T_wall[T_cs_counter],3), "[K]", round(T_wall[T_cs_counter]-273.15, 3), "[C]")
    print("Air Temperature:", round(T_air[T_cs_counter],3), "[K]",round(T_air[T_cs_counter]-273.15, 3), "[C]")
    print("")
    print("Q1 (in) Natural Convection Panel Exterior:", round(Q1[min_energy_balance_location], 3), "W" )
    print("Q2 (in) Radiation absorbed:", round(Q2[min_energy_balance_location], 3), "W" )
    print("Q3 (out) Natural Convection Panel interior:", round(Q3[min_energy_balance_location], 3), "W" )
    print("Q4 (out) Radiation emitted:", round(Q4[min_energy_balance_location], 3), "W" )
    print("")
    print("Q netroom Rad-cooling:", round(Q_netroom_rad, 3), "W" )
    #print("Q netroom Rad-other:", round(ColdSurface_Q - Q_netroom_rad+round(Q3[min_energy_balance_location], 3), 3), "W" )
    print("Q netroom Conv-cooling:", round(Q1[min_energy_balance_location], 3), "W" )
    print("Q cold surface:", round(ColdSurface_Q, 3), "W" )
    print("Q %rad:", round((Q_netroom_rad/(Q_netroom_rad+Q1[min_energy_balance_location]))*100, 3), "W" )
    print("Q rear conduction:", round(Rear_Conduction [T_cs_counter], 3), "W" )
    
    print("")
    print("film emissivity:", round( film_emissivity [min_energy_balance_location], 3))
    print("film transmissivity:", round(Rad_abs[7], 3))
    #print("panel emissivity:", round(e_wall[min_energy_balance_location], 3))   
    print("")
    '%.2E' % Decimal('40800000000.00000000000000')
    print("ext conv Ra:",     '%.2E' % Decimal(Conv_ext_Ra[min_energy_balance_location])  ) 
    print("ext conv Re:",     '%.2E' % Decimal( Conv_ext_Re[min_energy_balance_location])  ) 
    print("ext conv h:",     round(h_ext[min_energy_balance_location],3)) 
    print("Pr value:", round(Pr_val[min_energy_balance_location], 3)) 
    print("")
    print("int conv Ra:",     '%.2E' % Decimal(Conv_int_Ra[min_energy_balance_location])  )
    print("int conv h:",     round(h_int[min_energy_balance_location], 3)  )
    #print(wall_e_film[min_energy_balance_location], wall_e_cs[min_energy_balance_location], wall_e_film_black[min_energy_balance_location], wall_e_cs_black[min_energy_balance_location])
      
    print("--------------------------------------------------------------------")
    print("")
    T_cs_counter +=1;

All_film_temps_C = [round(float(x - 273.15),3) for x in All_film_temps]
res_list = [] 
for i in range(0, len(All_film_temps)): 
        res_list_val = abs((All_film_temps[i]-273.15) - Real_Mem_Temp[i])
        res_list.append(res_list_val) 
Temp_diff=  np.mean(res_list)
print(All_film_temps_C)
print("Temp Error: ",round(Temp_diff,5))

workbook = xlsxwriter.Workbook('Heat_Transfer_Output.xlsx')
worksheet = workbook.add_worksheet() 
bold = workbook.add_format({'bold': 1})

headings = ['T_film', 'T_cs', 'net_Q',  'Rad-cooling', 'CS-Radgain-other', 'Q_NatConv_Interior', 'ext h', 'int h', 'Trans', 'T_ss', 'K ext']

worksheet.write_row('A1', headings, bold)
worksheet.write_column('A2', All_film_temps_C)
worksheet.write_column('B2', T_cs)
worksheet.write_column('C2', All_ColdSurface_Qs)

worksheet.write_column('D2', All_QnetroomRadcooling)
worksheet.write_column('E2', All_QnetroomRadother)
worksheet.write_column('F2', NaturalConvectionPanelinterior)

worksheet.write_column('G2', All_Conv_ext_h)
worksheet.write_column('H2', All_Conv_int_h)
worksheet.write_column('I2', All_Trans)
worksheet.write_column('J2', T_wall)
worksheet.write_column('K2', All_K_ext)
workbook.close() 