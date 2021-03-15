import TRNSYSpy as TRNSYS
import math 
import csv
from pythermalcomfort.models import adaptive_ashrae
from pythermalcomfort.psychrometrics import t_o


#surface area of walls but not roof: 1000 + 2*150 + 2*60 = 1420
#surfae area of windows: 2*96 = 192

    

def PythonFunction():  

    #============These variables need to be set manually - Begin=================
        
    #model performance
    deltaT = 0.5
    orientation = 0 #0 for vertical panel, 1 for horizontal
    
    #Variables for multiple modes of heat transfer
    panel_height = 18  #[m]
    panel_width = 10   #[m]

    
    wind = 0.5 #air speed near panel m/s

    
    #Variables for convective heat transfer
    S = 0.2 #characteristic length (distance between cold panel and film [m])
    
    Cp = 4.184 #[KJ/Kg] #changer heat capacity if the fluid flowing through the panel is no water
    
    
    #These values are currently not incorperated into the model
    E_window = 0.02 #emissivity of windows, this value is currently not used
    insulation_thicknes = 0.15 #[m]   
    
    #============These variables need to be set manually - End=================
    
    T_air1 = TRNSYS.getInputValue(1) #air temperature surrounding the panel
    RH1 = TRNSYS.getInputValue(2) #relative humidity %
    DeHumid_Sched = TRNSYS.getInputValue(3) 
    T_dewpoint1 = TRNSYS.getInputValue(4)

    
    T_wallN = TRNSYS.getInputValue(5)
    T_wallS = TRNSYS.getInputValue(6)
    T_wallE = TRNSYS.getInputValue(7)
    T_wallW = TRNSYS.getInputValue(8)
    T_wallF = TRNSYS.getInputValue(9)
    T_wallR = TRNSYS.getInputValue(10)
    
    
    T_inlet1 = TRNSYS.getInputValue(11)    
    hot_side_flow_rate = TRNSYS.getInputValue(12) 
    mass_flow_rate = (hot_side_flow_rate/(3600)) #[Kg/sec]
    Day_of_year = int(TRNSYS.getInputValue(13) )     
    Occ_Schedual_input = TRNSYS.getInputValue(14) 
    Heatpump_temp_signal = TRNSYS.getInputValue(15)
    

   
    err_inc = 1.0
    h_int_err = err_inc*0.603
    h_ext_err = err_inc*1.499
    em_cs_err = err_inc
    Trans_error = err_inc*0.898
    #T_cs_err = err_inc
    T_ss_err = err_inc*1.019
    T_air_err = err_inc
    B_err = err_inc
    u_err = err_inc
    p_err = err_inc
    a_err = err_inc
    k_err_int = err_inc*0.993
    k_err_ext = err_inc*1.161
    #wind_err = err_inc
    
# =============================================================================
#     err_inc = 1.0
#     h_int_err = err_inc
#     h_ext_err = err_inc
#     em_cs_err = err_inc
#     Trans_error = err_inc
#     #T_cs_err = err_inc
#     T_ss_err = err_inc
#     T_air_err = err_inc
#     B_err = err_inc
#     u_err = err_inc
#     p_err = err_inc
#     a_err = err_inc
#     k_err_int = err_inc
#     k_err_ext = err_inc
#     #wind_err = err_inc
# =============================================================================
    
    A_cs = panel_height*panel_width #area of cold panel [m]
    P_cs = (panel_height*2)+(panel_width*2) #perimeter of cold panel [m]
    
    FTIR_out = FTIR()
    trans = FTIR_out[0]
    reflect = FTIR_out[1]
    wave_len2 = FTIR_out[2]
    
    trans = [(x*Trans_error) for x in trans]
    absorb = list(range(0, len(trans)))
    absorb = [(1 - trans[x] -  reflect[x]) for x in absorb]
    
    T_air = (T_air1*T_air_err)+273.15 #air temperature surrounding the panel
    E_cs = 0.95 * em_cs_err #emissivity of cold surface
    
    
    RH = RH1/100 #relative humidity to decimal
    
   


#=================Step 0: End ============================================    

    average_wall_temp = (T_wallN + T_wallS +T_wallE +T_wallW +T_wallF +T_wallR )/6
    
    path = r"C:\Users\denon\Google Drive\1_Masters_Backup\Python Code\Daily_Temps\Singapore_ave_daily_temp.csv"
    file = open(path, newline='')
    reader = csv.reader(file)
    Ave_Temp = []
    header = next(reader)
    for row in reader:
        temp = float(row[0])
        Ave_Temp.append(temp)
        
        
    Trm =(Ave_Temp[Day_of_year-2]+Ave_Temp[Day_of_year-3]+Ave_Temp[Day_of_year-4]+Ave_Temp[Day_of_year-5]+Ave_Temp[Day_of_year-6]+Ave_Temp[Day_of_year-7]+Ave_Temp[Day_of_year-8])/7 #running mean outdoor temp for adaptive model
    
    

    
    
    
    if Occ_Schedual_input ==1: 
        x = 1
        #=====================Step 3: Calculate View Factors between panels and human============================================
        P1_Panel_toHumans_F = [0.00088, 0.00088, 0.00088, 0.00088, 0.0027]
        total_Panel_toHumans_F = sum(P1_Panel_toHumans_F)*Occ_Schedual_input
        ave_panel_toHumans = (total_Panel_toHumans_F/len(P1_Panel_toHumans_F))*Occ_Schedual_input
        ave_human_toPanels_F = ((ave_panel_toHumans*A_cs)/1.551)
         
         #===========================Step 3: End ======================================================================
         
         
         
         
         
         #=================Step 1: Calculate MRT as seen by Panel ============================================
         
         #with people
        T_wall1 = Panel_MRT(T_wallF, T_wallN, T_wallS, T_wallE, T_wallW,  E_window, total_Panel_toHumans_F) #MRT in room
        P1_T_wall = (T_wall1*T_ss_err)+273.15 #MRT in room

         
         
         #without people
        T_wall1_no_H = Panel_MRT(T_wallF, T_wallN, T_wallS, T_wallE, T_wallW,  E_window, 0) #MRT in room
        P1_T_wall_no_H = (T_wall1_no_H*T_ss_err)+273.15 #MRT in room
 
         
         
        
        
        #=================Step 1: End ======================================================================
        
        #u_val = (3*(insulation_thicknes**2))-(1.82*insulation_thicknes)+0.34 #[W/m^2-k]
        
        Panel1_model1 = film_temp_and_Q(orientation, panel_height, panel_width, S, A_cs, P_cs, deltaT, 10+273.15, P1_T_wall, T_air, RH,  E_cs, wind, trans, reflect, absorb, wave_len2,  h_int_err, h_ext_err, B_err, u_err, p_err, a_err, k_err_ext, k_err_int)
        #Panel1_model1_Qdot_throughins = (u_val*A_cs*(T_wallR-15))/1000
        Panel1_model1_Q =   Panel1_model1[3]/1000
        t1_in = 10-(Panel1_model1_Q/(2*mass_flow_rate*Cp))   
        Panel1_model2 = film_temp_and_Q(orientation, panel_height, panel_width, S, A_cs, P_cs, deltaT, 5+273.15, P1_T_wall, T_air, RH,  E_cs, wind, trans, reflect, absorb, wave_len2,  h_int_err, h_ext_err, B_err, u_err, p_err, a_err, k_err_ext, k_err_int)
        #Panel1_model2_Qdot_throughins = (u_val*A_cs*(T_wallR-10))/1000
        Panel1_model2_Q =   Panel1_model2[3]/1000 
        t2_in = 5-(Panel1_model2_Q/(2*mass_flow_rate*Cp))  
        

                          
        P1_T_inlet_t_cs_equ = linear_regression(t1_in, 10, t2_in, 5)       
    
    
        
        #=================Step 2:Calculate Heat Transfer between Panel and Empty Room ============================================
         
        P1_T_cs1 = (P1_T_inlet_t_cs_equ[0]*T_inlet1)+P1_T_inlet_t_cs_equ[1]
        P1_T_cs = P1_T_cs1 + 273.15
        FTaQ_results = film_temp_and_Q(orientation, panel_height, panel_width, S, A_cs, P_cs, deltaT, P1_T_cs, P1_T_wall_no_H, T_air, RH,  E_cs, wind, trans, reflect, absorb, wave_len2,  h_int_err, h_ext_err, B_err, u_err, p_err, a_err, k_err_ext, k_err_int)    
        P1_Q_Panel_empty_room1 = FTaQ_results[0]
        P1_Q_film_room = FTaQ_results[4]
        
        P1_Q_room_gain = P1_Q_Panel_empty_room1*(1-total_Panel_toHumans_F)
        
    
    
        
        #=================Step 2: End ======================================================================
        
        
        
        
       
        
        
         #=================Step 4:Calculate Heat Transfer between Panel and Human ==================================
        
  

        P1_Q_PanelHuman_results = film_temp_and_Q(orientation, panel_height, panel_width, S, A_cs, P_cs, deltaT, P1_T_cs, P1_T_wall, T_air, RH,  E_cs, wind, trans, reflect, absorb, wave_len2,  h_int_err, h_ext_err, B_err, u_err, p_err, a_err, k_err_ext, k_err_int)    
        P1_Q_PanelOut = P1_Q_PanelHuman_results[2]
        P1_T_film1 = FTaQ_results[1]-273.15
    
    
        
        
       
    
        

    
        
        
        #=================Step 4: End ======================================================================    
         
         
        #=================Step 5 & 6: Calculate MRT as seen by human and pmv============================================
     
        H_MRT = list(range(5))  
        adapt_result_low = list(range(5)) 
        adapt_result_up = list(range(5)) 
        #adapt_result_temp = list(range(5)) 
        panel_MRT_temp = list(range(5))
        Q_human_panel = list(range(5))
        
        for x in H_MRT:
            H_MRT_results = MRT_Human(P1_Panel_toHumans_F[x],  P1_Q_PanelOut, T_wallN, T_wallS, T_wallE, T_wallW, T_wallF, T_wallR, A_cs,  E_window)
            H_MRT [x] = H_MRT_results[0]    
            panel_MRT_temp[x] = H_MRT_results[2]  
            adapt_resulttemp = adaptive_ashrae(T_air1, H_MRT[x], Trm, wind)
            adapt_result_low[x] = adapt_resulttemp['tmp_cmf_90_low']
            adapt_result_up[x] = adapt_resulttemp['tmp_cmf_90_up']
            #adapt_result_temp[x] = adapt_resulttemp['tmp_cmf']
            Q_human_panel [x] = H_MRT_results[3]*P1_Panel_toHumans_F[x]
    
        ADAPT_MIN = max(adapt_result_low)
        ADAPT_MAX = min(adapt_result_up)
        #ADAPT_temp_goal = sum(adapt_result_temp)/len(adapt_result_temp)

        AVE_HUMAN_MRT = sum(H_MRT)/len(H_MRT)
        Panel_MRT_Temp = sum(panel_MRT_temp)/len(panel_MRT_temp)
        
        
        AVE_Q_human_panel = sum(Q_human_panel)/len(Q_human_panel)
        
        operative_temp = t_o(T_air1, AVE_HUMAN_MRT, wind)

        #=================Step 5 & 6: End ====================================================================== 
        
        
        
        
        
        #=================Step 7:Update cold surface temperature============================================
         
        P1_T_outlet1 = P1_T_cs1 + (P1_T_cs1 - T_inlet1 )      
        T_outlet1_ave = P1_T_outlet1
        T_film1_low = P1_T_film1
        
        water_heat_gain_rate = 1000*mass_flow_rate*Cp*(P1_T_outlet1-T_inlet1)

        
        rad_control = 1
        heatpump_divert_control = 0.5
        
        
        panelflow_cont_var= (P1_T_outlet1 - (T_inlet1+0.5 ))*100
  

# =============================================================================
#         if  T_dewpoint1 <15:
#             T_dewpoint1 = 15
# =============================================================================
            
        T_cs_results = CS_temp(orientation, panel_height, panel_width, S, A_cs, P_cs, deltaT, T_dewpoint1+273.15, P1_T_wall, T_air, RH,  E_cs, wind, trans, reflect, absorb, wave_len2,  h_int_err, h_ext_err, B_err, u_err, p_err, a_err, k_err_ext, k_err_int)
        Panel_inlet_temp_set = (T_cs_results[1]+2)-273.15
        
    
   
            

            
        #=================Step 7:End============================================    
        

        
        
        ##Leave for Debugging
# =============================================================================
#         rad_control = 0 
#         operative_temp = 20
#         AVE_HUMAN_MRT = 30
#         P1_Q_room_gain = 0
#         panelflow_cont_var = 0
# =============================================================================
# =============================================================================
#         P1_Q_film_room = 0
# =============================================================================
# =============================================================================
#         ADAPT_MIN = 0
#         P1_T_outlet1 = T_inlet1
#         P2_T_outlet1 = T_inlet1 
#         T_outlet1_ave = T_inlet1
#         P1_T_cs1 = T_inlet1
#         T_film1_low = 0
# =============================================================================
# =============================================================================
#         ave_human_toPanels_F = 0
#         controlled_variable = 0
#         heatpump_divert_control = 0.5
#         Panel_MRT_Temp = 2532
#         Panel_inlet_temp_set = 25        
#         ADAPT_MAX = 1
#         PMV_MIN = 1
#         PMV_MAX = 1
# =============================================================================
    
            
    
    if  Occ_Schedual_input ==0:           

        ADAPT_MIN = 0
        ADAPT_MAX = 0
        AVE_HUMAN_MRT = 0
        rad_control = 0 
        P1_Q_room_gain = 0
        P1_Q_film_room = 0
        P1_T_outlet1 = T_inlet1       
        T_outlet1_ave = T_inlet1
        P1_T_cs1 = T_inlet1
        T_film1_low = 0
        ave_human_toPanels_F = 0
        panelflow_cont_var= (P1_T_outlet1 - (T_inlet1 +0.5))*100 
        heatpump_divert_control = 1
        Panel_inlet_temp_set = 20
        Panel_MRT_Temp = 0
        operative_temp = 0
        water_heat_gain_rate = 0
        AVE_Q_human_panel = 0
        
    ##########  
# =============================================================================
#     P1_Q_room_gain = 0
#     P1_Q_film_room = 0
# =============================================================================
    ##########
    

    ignore = 0
    
    
    TRNSYS.setOutputValue(1,P1_Q_room_gain)
    TRNSYS.setOutputValue(2,P1_T_outlet1)   
    TRNSYS.setOutputValue(3,rad_control)
    TRNSYS.setOutputValue(4,wind)
    TRNSYS.setOutputValue(5,T_inlet1)
    TRNSYS.setOutputValue(6,P1_T_cs1)
    TRNSYS.setOutputValue(7,operative_temp)
    TRNSYS.setOutputValue(8,T_film1_low) 
    TRNSYS.setOutputValue(9,T_dewpoint1) 
    TRNSYS.setOutputValue(10,P1_Q_film_room)   
    TRNSYS.setOutputValue(11,Trm)
    TRNSYS.setOutputValue(12,ave_human_toPanels_F)    
    TRNSYS.setOutputValue(13,panelflow_cont_var) 
    TRNSYS.setOutputValue(14,AVE_Q_human_panel) 
    TRNSYS.setOutputValue(15,ignore)
    TRNSYS.setOutputValue(16,ignore)
    TRNSYS.setOutputValue(17,ADAPT_MIN)
    TRNSYS.setOutputValue(18,ADAPT_MAX)
    TRNSYS.setOutputValue(19,average_wall_temp)  
    TRNSYS.setOutputValue(20, water_heat_gain_rate)    
    TRNSYS.setOutputValue(21, heatpump_divert_control) 
    TRNSYS.setOutputValue(22, Panel_MRT_Temp) 
    TRNSYS.setOutputValue(23, Panel_inlet_temp_set) 
    TRNSYS.setOutputValue(24, AVE_HUMAN_MRT) 
    
# =============================================================================
#     P1_Panel_toHumans_F = [0.00088, 0.00088, 0.00088, 0.00088, 0.0028]
#     total_Panel_toHumans_F = sum(P1_Panel_toHumans_F)*Occ_Schedual_input
#     ave_panel_toHumans = (total_Panel_toHumans_F/len(P1_Panel_toHumans_F))*Occ_Schedual_input
#     ave_human_toPanels_F = ((ave_panel_toHumans*A_cs)/1.551)
# 
# 
# 
# 
# 
#     if DeHumid_Sched == 1:
#          if RH1 >= 60:
#              AC_flow = 700
#          if 58 < RH1 < 60:
#              AC_flow = 400
#          if  RH1 <= 58:
#              AC_flow = 300
# 
#              
#      
#     elif DeHumid_Sched == 0:        
#              AC_flow = 50
# 
# 
# 
#     TRNSYS.setOutputValue(1,abs(0))
#     TRNSYS.setOutputValue(2,0)   
#     TRNSYS.setOutputValue(3,0)
#     TRNSYS.setOutputValue(4,0)
#     TRNSYS.setOutputValue(5,0)
#     TRNSYS.setOutputValue(6,0)
#     TRNSYS.setOutputValue(7,0)
#     TRNSYS.setOutputValue(8,0) 
#     TRNSYS.setOutputValue(9,0) 
#     TRNSYS.setOutputValue(10,abs(0))   
#     TRNSYS.setOutputValue(11,0)
#     TRNSYS.setOutputValue(12,ave_human_toPanels_F)    
#     TRNSYS.setOutputValue(13,0) 
#     TRNSYS.setOutputValue(14,0) 
#     TRNSYS.setOutputValue(15,0)
#     TRNSYS.setOutputValue(16,abs(0))
#     TRNSYS.setOutputValue(17,0)
#     TRNSYS.setOutputValue(18,0)
#     TRNSYS.setOutputValue(19,0)  
#     TRNSYS.setOutputValue(20, AC_flow)    
#     TRNSYS.setOutputValue(21, 0) 
#     TRNSYS.setOutputValue(22, 0) 
#     TRNSYS.setOutputValue(23, 0) 
#     TRNSYS.setOutputValue(24, 0)  
# =============================================================================
    return






def Panel_MRT(T_F, T_N, T_S, T_E, T_W,  E_window, total_Panel_toHumans_F): 
    
    P1_toWalls_F = [0.1088, 0.1088, 0.0416, 0.0416, .699 - total_Panel_toHumans_F , .062, .062] #Panel 1 to walls. North, South, East, West, Floor, window1, window2

    T_F = T_F + 273.15
    T_N = T_N + 273.15
    T_S = T_S + 273.15
    T_E = T_E + 273.15
    T_W = T_W + 273.15

    MRT_people = 32 + 273.15
        
    P1_mrt = ((((T_N**4)*P1_toWalls_F[0]) + ((T_S**4)*P1_toWalls_F[1]) + ((T_E**4)*P1_toWalls_F[2]) + ((T_W**4)*P1_toWalls_F[3]) + ((T_F**4)*P1_toWalls_F[4])+((MRT_people**4)*total_Panel_toHumans_F)    )**(1/4)) - 273.15 #calculates mrt 
    
    
    
    return P1_mrt


def film_temp_and_Q (orientation, panel_height, panel_width, S, A_cs, P_cs, deltaT, T_cs, T_wall, T_air, RH,  E_cs, wind, trans, reflect, absorb, wave_len2,  h_int_err, h_ext_err, B_err, u_err, p_err, a_err, k_err_ext, k_err_int):
          



    
    
    if T_wall > T_air: #deciding what range of potential film temperatures need to be iterated through
        temp_high = T_wall
    else:
        temp_high = T_air
    
    resolution = int((temp_high-T_cs)/deltaT) #higher number means more precise temperature but takes longer
    
    T_film = list(range(resolution)) #each of these lists are for storing data for one combination of variales, it gets reset after each combination has been iterated
    energy_balance = list(range(resolution))
    Q1 = list(range(resolution))
    Q2 = list(range(resolution))
    Q3 = list(range(resolution))
    Q4 = list(range(resolution))
    
    Q_netroom1 = list(range(resolution))
    Q_netroom2 = list(range(resolution))
    Q_netroom_out1 = list(range(resolution))
    Q_netroom_out2 = list(range(resolution))
    Q_radEmi_cs = list(range(resolution))
    Q_radAbs_cs = list(range(resolution))
    
    min_energy_balance = 10000 #just setting it to a large number, the combination that minamizes this value is the solution
    
    for x in energy_balance:  #the section that iterates through one variable combination to find the silution
        T_film[x] = T_cs + (deltaT * x)
        
        
        Conv_ext = Nat_Conv_PanelExterior(A_cs, P_cs, T_film[x], T_air, RH, orientation, panel_height, panel_width, wind, h_ext_err, B_err, u_err, p_err, a_err, k_err_ext)
        Q1[x] = Conv_ext[0]

        
        Rad_abs = Radiant_Transfer_absorption (A_cs, T_cs, T_wall, trans, absorb, wave_len2, E_cs, reflect)
        Q2[x] = Rad_abs[0]
        Q_netroom1[x] = Rad_abs[1]
        Q_netroom_out1 [x] = Rad_abs[2]
        Q_radAbs_cs[x] = Rad_abs[3]
        
        Conv_int = Nat_Conv_PanelInterior(A_cs, T_cs, T_film[x], S, orientation, panel_height, h_int_err, B_err, u_err, p_err, a_err, k_err_int)
        Q3[x] =  Conv_int[0]

        
        Rad_emi = Radiant_Transfer_emission(A_cs, T_film[x], trans, absorb, wave_len2, E_cs)
        Q4[x] = Rad_emi[0]
        Q_netroom2[x] = Rad_emi[2]
        Q_netroom_out2 [x] = Rad_emi[3]
        Q_radEmi_cs[x] =Rad_emi[4]
        
        energy_balance [x] = abs(Q1[x] + Q2[x] + Q3[x] + Q4[x])
       
       
        if energy_balance [x] < min_energy_balance:
            min_energy_balance = energy_balance [x]
            min_energy_balance_location = x
    
    T_film_result = T_film[min_energy_balance_location]            
    Q_netroom_rad = Q_netroom1[min_energy_balance_location] + Q_netroom2[min_energy_balance_location]
    Q_netroom_panel = Q_netroom_rad - Q3[min_energy_balance_location]
    Q_netroom_out = Q_netroom_out1[min_energy_balance_location] + Q_netroom_out2[min_energy_balance_location]
    ColdSurface_Q  =  Q_radAbs_cs[min_energy_balance_location] + Q_radEmi_cs[min_energy_balance_location] - Q3[min_energy_balance_location]        
    Q_film_room = Q1[min_energy_balance_location]
        


    return Q_netroom_rad, T_film_result, Q_netroom_out, ColdSurface_Q, Q_film_room, Q_netroom_panel



def CS_temp (orientation, panel_height, panel_width, S, A_cs, P_cs, deltaT, T_film, T_wall, T_air, RH,  E_cs, wind, trans, reflect, absorb, wave_len2,  h_int_err, h_ext_err, B_err, u_err, p_err, a_err, k_err_ext, k_err_int):
          



    
    
    resolution = int((T_film - 273.15 )/deltaT) #higher number means more precise temperature but takes longer
    
    T_cs = list(range(resolution)) #each of these lists are for storing data for one combination of variales, it gets reset after each combination has been iterated
    energy_balance = list(range(resolution))
    Q1 = list(range(resolution))
    Q2 = list(range(resolution))
    Q3 = list(range(resolution))
    Q4 = list(range(resolution))
    
    Q_netroom1 = list(range(resolution))
    Q_netroom2 = list(range(resolution))
    Q_netroom_out1 = list(range(resolution))
    Q_netroom_out2 = list(range(resolution))
    Q_radEmi_cs = list(range(resolution))
    Q_radAbs_cs = list(range(resolution))
    
    min_energy_balance = 10000 #just setting it to a large number, the combination that minamizes this value is the solution
    
    for x in energy_balance:  #the section that iterates through one variable combination to find the silution
        T_cs[x] = 273.15 + (deltaT * x)
        
        
        Conv_ext = Nat_Conv_PanelExterior(A_cs, P_cs, T_film, T_air, RH, orientation, panel_height, panel_width, wind, h_ext_err, B_err, u_err, p_err, a_err, k_err_ext)
        Q1[x] = Conv_ext[0]

        
        Rad_abs = Radiant_Transfer_absorption (A_cs, T_cs[x], T_wall, trans, absorb, wave_len2, E_cs, reflect)
        Q2[x] = Rad_abs[0]
        Q_netroom1[x] = Rad_abs[1]
        Q_netroom_out1 [x] = Rad_abs[2]
        Q_radAbs_cs[x] = Rad_abs[3]
        
        Conv_int = Nat_Conv_PanelInterior(A_cs, T_cs[x], T_film, S, orientation, panel_height, h_int_err, B_err, u_err, p_err, a_err, k_err_int)
        Q3[x] =  Conv_int[0]

        
        Rad_emi = Radiant_Transfer_emission(A_cs, T_film, trans, absorb, wave_len2, E_cs)
        Q4[x] = Rad_emi[0]
        Q_netroom2[x] = Rad_emi[2]
        Q_netroom_out2 [x] = Rad_emi[3]
        Q_radEmi_cs[x] =Rad_emi[4]
        
        energy_balance [x] = abs(Q1[x] + Q2[x] + Q3[x] + Q4[x])
       
       
        if energy_balance [x] < min_energy_balance:
            min_energy_balance = energy_balance [x]
            min_energy_balance_location = x
    
    T_cs_result = T_cs[min_energy_balance_location]            
    Q_netroom_rad = Q_netroom1[min_energy_balance_location] + Q_netroom2[min_energy_balance_location]
    Q_netroom_out = Q_netroom_out1[min_energy_balance_location] + Q_netroom_out2[min_energy_balance_location]
    ColdSurface_Q  =  Q_radAbs_cs[min_energy_balance_location] + Q_radEmi_cs[min_energy_balance_location] + Q3[min_energy_balance_location]        
    Q_film_room = Q1[min_energy_balance_location]
        


    return Q_netroom_rad, T_cs_result, Q_netroom_out, ColdSurface_Q, Q_film_room

# =============================================================================
# def Human_Panel_View_Factors (Panel1_toHuman_F, Panel2_toHuman_F, A_cs, panel_height, panel_width, R_z)  :
# 
#     Human_toPanel1_F = list(range(10))
#     Human_toPanel12_F = list(range(10))   
#     
#     for x in Human_toPanel1_F:
#         Human_toPanel1_F(x) = Panel1_toHuman_F(x)
# 
#     A_eff = 1.551 #affetcive radiative surface area of adult male
#     
#     F_ph = (F_hp*A_eff)/A_cs   #view factor panel to human
# 
#     return F_hp, F_ph
# =============================================================================

# =============================================================================
# def Human_Rec_View_Factor (a, b, c, A_cs, above)  :
# 
#     if above ==1:
#         par = [0.116, 1.39569, 0.13021, 0.986, 0.95093, 0.07967, 0.05458, 0.853]
#     else:
#         par = [0.118, 1.21590, 0.16890, 0.992, 0.71739, 0.08733, 0.05217, 0.927]
# 
#     
#     
#     F_sat = par[0]
#     tau = par[1]+(par[2]*(a/c))
#     y = par[4]+(par[5]*(b/c))+(par[6]*(a/c))
#         
#     F_hp = F_sat*(1-math.exp(-1*(a/c)/tau))*(1-math.exp(-1*(b/c)/y)) #view factor human to panel
# 
# 
#     return F_hp
# 
# 
# 
# 
# 
# def Human_Panel_Heat_exchange (Q_Panel_empty_room1, A_cs, F_ph)  :
#     #['F_max', 'A', 'B', 'R_r', 'C', 'D', 'E', 'R_R']
#     
#    
# 
#     
#     Q_room_gain = Q_Panel_empty_room1*(1-F_ph)
#     Q_PanelHuman = Q_Panel_empty_room1*F_ph  #assumption
#     
#     return Q_room_gain, Q_PanelHuman
# =============================================================================
    


def MRT_Human(P1_Panel_toHumans_F,  P1_Q_PanelOut, T_wallN, T_wallS, T_wallE, T_wallW, T_wallF, T_wallR, A_cs, E_window):
    
    F_hh = 15*0.00074 #average view fator from human to humans

    boltz = (5.670374*10**(-8))
    
    T_walls=((T_wallN + T_wallS + T_wallE + T_wallW + T_wallF + T_wallR)/6) +273.15
    

    T_human = 32 + 273.15


    T_panel1 = (P1_Q_PanelOut/(A_cs*boltz))**(1/4)
   


    

    
    A_eff = 1.551
    F_hp1 =  (P1_Panel_toHumans_F*A_cs)/A_eff
    
    Q_humanpanel_noView = boltz*A_cs*(((32+273.15)**4)-(T_panel1**4))
   
    
    T_MRT_human = (   (   ((T_panel1**4)*F_hp1)   +   ((T_human**4)*F_hh)   +   ((T_walls**4)* (1-F_hp1-F_hh)  ) )      **(1/4))-273.15
    

    
    return T_MRT_human,  T_walls-273.15, T_panel1-273.15, Q_humanpanel_noView
    
    
    



def FTIR():  
    thick_film_2 = 0.00076
    thick_film_data = 0.00076 # * Dont change unless data changes * thickness of film used for ftir data [m] 
    
    path = r"C:\Users\denon\Google Drive\1_Masters_Backup\Python Code\FTIR data\csv_files\Edit-coldtubeT.csv"
    file = open(path, newline='')
    reader = csv.reader(file)
    trans = []
    header = next(reader)
    for row in reader:
        Trans = float(row[1])
        if Trans!= 0:
            abs_cof_temp =  math.log(Trans)/thick_film_data #calculating absorption coefficient (Beer's Law)
            Trans = math.exp(abs_cof_temp*thick_film_2)  #Beer's law again (broken up for debugging)      
        else:
            Trans=0
        trans.append(Trans)
        
        
    
    path = r"C:\Users\denon\Google Drive\1_Masters_Backup\Python Code\FTIR data\csv_files\Edit-coldtubeR.csv"
    file = open(path, newline='')
    reader = csv.reader(file)
    reflect = []
    wave_len2 = []  
    header = next(reader)
    for row in reader:
        Wavelength = float(row[0])
        ref = float(row[1])
        reflect.append(ref)
        wave_len2.append(Wavelength)
    return trans, reflect, wave_len2    



#==============================================================================
def Nat_Conv_PanelInterior(A_cs, T_cs, T_film, S, orientation, panel_height, h_int_err, B_err, u_err, p_err, a_err, k_err):

   #T_cs = 273 #surface tmeperature
   #T_film = 300 #film temperature
         
    Interior_air_temp = float((T_cs + T_film)/2)
    
    vert_horiz_conversion = 1.9496*((abs(T_film-T_cs))**(0.0754))
    
    B = B_err*1.0473*Interior_air_temp**(-1.007)#B_err*PropsSI('isobaric_expansion_coefficient','P',101325,'T',Interior_air_temp,'air') #volumetric thermal expansion coefficient [1/k]
    u = u_err*(2.21436*10**(-7))*Interior_air_temp**0.7754  #Dynamic  viscosity [Pa*s]
    p = p_err*344.91*(Interior_air_temp**(-.996))#p_err*PropsSI('DMASS','P',101325,'T',Interior_air_temp,'air') #density [kg/m^3]
    v = u/p  #kinematic viscosity
    a = a_err*(((5.68172*(10.0**(-17.0)))* (Interior_air_temp**4.0))-((1.76304*(10.0**(-13.0)))*(Interior_air_temp**3.0))+((2.81311*(10.0**(-10.0)))*(Interior_air_temp**2.0))+((1.03147*(10.0**(-8.0)))*Interior_air_temp)-(1.47967*(10.0**(-6.0))))  #thermal diffusivity [m2/s]
    k= k_err*0.0002069*Interior_air_temp**0.84998#k_err*PropsSI('conductivity','P',101325,'T',Interior_air_temp,'air') #thermal conductivity [W/m k]
    g = 9.80665
    #S = 0.2 #characteristic length (distance between panels [m])
    
    
    Ra_S = abs((g*B*(T_film - T_cs)*(S**3))/(v*a))
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
        
    h_PanelInterior = vert_horiz_conversion*(Nu_L*k/S)*h_int_err
    Q3_NCIn =  h_PanelInterior*A_cs*(T_cs - T_film) #Q3_NCIn = total heat transfer (W) Natural Convection Interior
           
    return Q3_NCIn, Ra_S, h_PanelInterior




def Nat_Conv_PanelExterior(A_cs, P_cs, T_film, T_air, RH, orientation, panel_height, panel_width, wind, h_ext_err, B_err, u_err, p_err, a_err, k_err):
    
    vert_horiz_conversion = 2.032*((abs(T_film-T_air))**(-0.159))
    
    T_air = float(T_air)
    
    B = B_err*1.0473*T_air**(-1.007)#B_err*PropsSI('isobaric_expansion_coefficient','P',101325,'T',Interior_air_temp,'air') #volumetric thermal expansion coefficient [1/k]
    u = u_err*(2.21436*10**(-7))*T_air**0.7754#u_err*HAPropsSI('Visc','P',101325,'T',T_air,'R', RH) #Dynamic  viscosity [Pa*s]
    #u = PropsSI('viscosity','P',101325,'T',T_air,'air') #Dynamic  viscosity [Pa*s]
    p = p_err*344.91*(T_air**(-.996))#p_err*PropsSI('DMASS','P',101325,'T',T_air,'air') #density [kg/m^3]
    v = u/p  #kinematic viscosity
    a = a_err*(((5.68172*(10.0**(-17.0)))* (T_air**4.0))-((1.76304*(10.0**(-13.0)))*(T_air**3.0))+((2.81311*(10.0**(-10.0)))*(T_air**2.0))+((1.03147*(10.0**(-8.0)))*T_air)-(1.47967*(10.0**(-6.0))))  #thermal diffusivity [m2/s]
    #k = PropsSI('conductivity','P',101325,'T',T_air,'air') #thermal conductivity [W/m k]
    k = k_err*0.0002069*T_air**0.84998#k_err*HAPropsSI('K','P',101325,'T',T_air,'R', RH) #thermal conductivity [W/m/k]
    g = 9.80665
    




    if orientation ==0: #for verticle panels
        
        
        
        L = panel_height #characteristic length
        Gr_L = abs((g*B*(T_air - T_film)*(L**3))/(v**2))
        Pr = v/a
        Ra_L = Gr_L*Pr
        
        Re_L = (p*wind*panel_width)/u
        Nu_L_force=0.664*(Pr**(1/3))*(Re_L**(1/2))
        
        #UWT
        Nu_L_nat = (0.825+   ((0.387*(Ra_L**(1/6)))  /   ((1+ ((0.492/Pr)**(9/16))    )**(8/27))))**2
        Nu_L=((Nu_L_nat**0.7)+(Nu_L_force**0.7))**(1/0.7)
        
# =============================================================================
#         #UHF
#         Nu_L = 0.55 *  Ra_L**(1/5)
# =============================================================================


    else: #horiztonal panel
        L = A_cs / P_cs #characteristic length
        Gr_L = abs((g*B*(T_air - T_film)*(L**3))/(v**2))
        Pr = v/a
        Ra_L = Gr_L*Pr
      
        
        panel_width = (panel_width+panel_height)/2
        Re_L = (p*wind*panel_width)/u
        Nu_L_force=0.664*(Pr**(1/3))*(Re_L**(1/2))

        #UWT
        if Ra_L<10**7:
            Nu_L_nat = 0.54*Ra_L**0.25
        else:
            Nu_L_nat = 0.15*Ra_L**(1/3)
            
        Nu_L=((Nu_L_nat**3)+(Nu_L_force**3))**(1/3)
      
# =============================================================================
#         #UHF
#         if Ra_L>5*10**8:  
#             0.13*Ra_L**(1/3)
#         if Ra_L<5*10**8:
#             0.16*Ra_L**(1/3)
# =============================================================================

        
    h_PanelExterior = vert_horiz_conversion*(Nu_L*k/L)*h_ext_err
    Q1_NCEx =  h_PanelExterior*A_cs*(T_air - T_film) #Q1_NCEx = total heat transfer (W) Natural Convection Exterior
    return Q1_NCEx, Ra_L, Pr, h_PanelExterior, Re_L  
#==============================================================================
#==============================================================================
#==============================================================================
    


#==============================================================================
#==============================================================================
#==============================================================================
def Radiant_Transfer_absorption(A_cs, T_cs, T_wall, trans, absorb, wave_len2, E_cs, reflect):
    
        
    #==============================================================================
    ##constants
    #==============================================================================
        
    C1 = 3.741695*(10**8) #radiation contants for Planck's distribution
    C2 = 1.438866*(10**4)

    
   
    #===============================================================================  
    #===============================================================================    
    ##E1 (Emission cold panel)
    #===============================================================================
    #===============================================================================  

    E1 = list(range(0, len(trans)))  #emissive power of cold surface per wavelength 
    #Creating spectral emissive power from cold panel
    for x in E1:
        E1 [x] = (C1/((wave_len2[x]**5) * ((math.exp(C2/(wave_len2[x]*T_cs))) -1)))*E_cs # [W/m2-um] Emissive power/wavelength for blackbody
    E1_tot=integrate(E1, wave_len2)
    #==============================================================================
    ##Calculating transmission of E1  through film, ---> G2 (Irradiation on surfaces)
    #==============================================================================
       
  
    
    
    G2 = list(range(0, len(trans)))
    for x in G2:
        G2 [x] = E1 [x]*(trans[x])
    G2_tot=integrate(G2, wave_len2) #integrates across wavelengths to find total Irradiance on wall
    
    
    
    E1_film_reflect = list(range(0, len(trans)))
    for x in E1_film_reflect:
        E1_film_reflect [x] = E1 [x]*(reflect[x])
    E1_film_ref_tot=integrate(E1_film_reflect, wave_len2) #integrates across wavelengths to find total Irradiance on wall
    
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
    E2_tot=integrate(E2, wave_len2) #integrates across wavelengths to find total Emission from wall
    
    #==============================================================================
    ##Calculating transmission of E2  through film, ---> G1 (Irradiation on surfaces)
    #==============================================================================
   
    abs_E2 = list(range(0, len(trans)))
    for x in abs_E2:
        abs_E2 [x] = E2 [x]*(absorb[x])    
    abs_E2_tot=integrate(abs_E2, wave_len2) #integrates across wavelengths to find total Irradiance on cold surface
   
    
    G1 = list(range(0, len(trans)))
    for x in G1:
        G1 [x] = E2 [x]*(trans[x])    
    G1_tot=integrate(G1, wave_len2) #integrates across wavelengths to find total Irradiance on cold surface
    
    #==============================================================================
    ##Calculating reflected portion of G1  ---> pG1
    #==============================================================================
  
    pG1 = list(range(0, len(trans)))
    for x in pG1:
        pG1 [x] = G1 [x] * p_cs  
    pG1_tot=integrate(pG1, wave_len2) #integrates across wavelengths to find total energy reflected by cold panel


    pPanel = list(range(0, len(trans)))   #energy reflected off panel from outside
    for x in pPanel:
        pPanel [x] = (E2 [x] * reflect[x]) + (pG1 [x] * trans[x])
    pPanel_tot=integrate(pPanel, wave_len2) #integrates across wavelengths to find total energy reflected by cold panel    
    

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
        
    rad_abs_tot=integrate(rad_abs, wave_len2) #total energy flux absorbed (not accounting for surface area)
    Q2 = A_cs * rad_abs_tot
    film_transmissivity = G2_tot / E1_tot
    Q_netroom1 = A_cs*(E2_tot-pPanel_tot-G2_tot)#net heat transfer between panel and surrounding walls
    Q_netroom_out = A_cs*(G2_tot+pPanel_tot)
    #heat_transfer_on_cold_surface = A_cs*((E_cs*(G1_tot+E1_film_reflect_tot))-E1_tot)
    heat_transfer_on_cold_surface = A_cs*((E_cs*(G1_tot+(E1_tot*0.05)))-E1_tot)
    return Q2, Q_netroom1, Q_netroom_out, heat_transfer_on_cold_surface

 

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
    pG1_tot=integrate(pG1, wave_len2) #integrates across wavelengths to find total energy reflected by cold panel
    #==============================================================================
    
    
    film_ref_out = list(range(0, len(trans)))
    for x in film_ref_out:
        film_ref_out [x] = E_film [x] * p_cs * trans[x]  
    film_ref_out_tot=integrate(film_ref_out, wave_len2) #integrates across wavelengths to find total energy reflected by cold panel
    
    
    
    #=========================================================
    
        
        
    E_film_tot=integrate(E_film, wave_len2) #integrates across wavelengths to find total Emission from Cold Panel
    E_film_black_tot=integrate(E_film_black, wave_len2)
    film_emissivity = E_film_tot /  E_film_black_tot
   
    #Q4 = A_cs * ((2 * E_film_tot) - pG1_tot - pG2_tot)
    Q4 = -1*A_cs * ((2 * E_film_tot) - pG1_tot )
    
    pG1_for_cooling = list(range(0, len(trans)))
    pG1_for_cooling [x] = E_film [x] * p_cs * trans[x]
    Part2_Em_power_for_cooling = E_film_tot + integrate(pG1_for_cooling, wave_len2)
    
    Q_netroom2 = A_cs*(-E_film_tot-film_ref_out_tot)
    Q_netroom_out = A_cs*(E_film_tot+film_ref_out_tot)
    heat_transfer_on_cold_surface = A_cs*(E_film_tot*E_cs)
    
    return Q4, Part2_Em_power_for_cooling, Q_netroom2, Q_netroom_out, heat_transfer_on_cold_surface
    
#==============================================================================
#==============================================================================
#==============================================================================    
    
def integrate(y, x):
    area = 0
    i = 0
    while i < len(x)-1: 
        if y[i]<y[i+1]:
            height = y[i]
        else:
            height = y[i+1]
        area = area + (((x[i+1]-x[i])*height) + (((x[i+1]-x[i])*abs(y[i+1]-y[i]))/2))
        i=i+1
    return area

def linear_regression(x1, y1, x2, y2):
    m = (y1-y2)/(x1-x2)
    b = (-1*x1*m)+y1
       
    return m, b








