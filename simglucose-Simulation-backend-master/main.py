from datetime import datetime
import random
import pandas as pd
import time
from Patient import Patient
from SimulationClock import SimulationClock
import keyboard

import dearpygui.dearpygui as dpg

from shapes import Circle, Rectangle, Shape


def log_msg(message: str):
     currentLogs = dpg.get_value('log_text')
     dpg.set_value("log_text", currentLogs + message + "\n")

def secondsToDDHHMM(seconds):
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    return [days,hours, minutes]


simulationRunning = True

patientType = int(input('Enter Patient Type \n1)child \n2)adolescent \n3)Adult\n'))
patient = Patient(patientType)

simStartime = patient.getSimStartTime()
simClock = SimulationClock(simStartime)
simClock.setSimulationRate()

print(simStartime)

print(f"[WAWA] Glucose at sim start time (should be 145 ish) {patient.getGlucoseLevelAtTimestamp(simStartime)}") #Bug: First timestamp is +2hrs from start!


dpg.create_context()
dpg.create_viewport(title='Glucose Simulation', width=900, height=600)



with dpg.window(label="SIM GLUCOSE", height=dpg.get_viewport_max_height(), width=dpg.get_viewport_max_width(), no_collapse=True, no_move=True, no_close=True, no_title_bar=True, tag='root'):
    
    with dpg.child_window(label="Sim Info", pos=(20,20), tag='sim-info', border=True, width=1850, height=120):
        

        
        with dpg.table(header_row=False):
                dpg.add_table_column()
                dpg.add_table_column()
                with dpg.table_row():
                        
                        with dpg.group():
                            dpg.add_text(default_value=f"Simulation Controls: ", color=[255,255,255,255],tag='sim-ctrl-txt1')
                            dpg.add_text(default_value=f"simulation rate: 1x ", color=[255,255,255,255], tag='sim-rate-txt1')
                            with dpg.group(horizontal=True):
                                dpg.add_button(label='Normal Speed', callback=lambda:simClock.setSimulationRate(1))
                                dpg.add_button(label='3X Simulation Speed', callback=lambda:simClock.setSimulationRate(3))
                                dpg.add_button(label='6X Simulation Speed', callback=lambda:simClock.setSimulationRate(6))
                            dpg.add_text(default_value=f"Time of simulation: {0}",  tag='sim-time', color=[255,255,255,255])


                        with dpg.group():
                            dpg.add_text(default_value=f"Patient Info: ", color=[255,255,255,255], tag='sim-info-txt1')
                            dpg.add_text(default_value=f"Patient Type: {patient.getPatientType()}")
                            with dpg.group(horizontal=True):
                                
                                dpg.add_text(default_value=f"Current Glucose Level (mg/dL) {0}",  tag='sim-pt-glucose', color=[255,255,255,255])
                                dpg.add_text(default_value=f"",  tag='sim-pt-risk', color=[255,10,10,255])


    with dpg.child_window(label="Patient Glucose", tag="win", height=250, width=500, pos=(20,160), border=True, no_scrollbar=True):
    
        
        with dpg.plot(label="Blood Glucose Levels (ml/dl)", height=250, width=500,no_menus=True, no_box_select=True, no_mouse_pos=True, equal_aspects=False):
          
            dpg.add_plot_axis(dpg.mvXAxis, label="Time (seconds)", tag='x_axis')
            dpg.add_plot_axis(dpg.mvYAxis, label="Glucose ml/dl", tag="y_axis")

            # series belong to a y axis
            dpg.add_line_series([], [], label="Patient Glucose", parent="y_axis", tag="series_tag")

    with dpg.child_window(label="Insulin Delivered at timestamp", tag="insInj", height=250, width=500, pos=(20,400), border=True, no_scrollbar=True):
    
        
        with dpg.plot(label="Insulin Dosage injection", height=250, width=500,no_menus=True, no_box_select=True, no_mouse_pos=True, equal_aspects=False):
            # optionally create legend
            #dpg.add_plot_legend()

            dpg.add_plot_axis(dpg.mvXAxis, label="Time (seconds)", tag='ins-x_axis')
            dpg.add_plot_axis(dpg.mvYAxis, label="Insulin Injection units", tag="ins-y_axis")

            # series belong to a y axis
            dpg.add_line_series([], [], label="Patient Glucose", parent="ins-y_axis", tag="ins-series_tag" )

    with dpg.child_window(label='Patient Logs', tag='logs', width=500, height=250, pos=(20,670)):
         dpg.add_input_text(
        multiline=True,
        readonly=True,
        width=-1,
        height=-1,
        default_value="Simulation started...\n",
        tag="log_text"
        )
         

         
    with dpg.child_window(label='Simulation', height=760, width=1320, pos=(550,160)):
        with dpg.drawlist(height=500, width=720):
            #dpg.draw_circle((250,250),50,fill=(255,255,255,255), label="CGM")
            cgm = Circle((250,250), 50,fillColor=(255,255,255,255), textLabel="CGM")
            mcu = Rectangle((350,250), width=150, height=100, textLabel="MCU(ESP-32)", fillColor=(255,255,255,255))

            dpg.draw_arrow(((mcu.xpos + mcu.height)/2,mcu.ypos),(cgm.xpos+cgm.radius,cgm.ypos),color=(255,0,0,255))
        #dpg.add_text(default_value='CGM', pos=(250,250), color=(0,0,0,255))



dpg.show_viewport()
dpg.maximize_viewport()

dpg.setup_dearpygui()






simafter8hrs = simClock._simulationStartTime+28800
print(f"Sim start time + 8 hrs = {simafter8hrs}")
print(f"glucose after 8 hrs = {patient.getGlucoseLevelAtTimestamp(simafter8hrs)}")


simCycle = 0

while dpg.is_dearpygui_running() and simulationRunning:
    time.sleep(0.02)
    simClock.updateClock()
    simCycle = simCycle + 1
   
    if keyboard.is_pressed('q'):
        simulationRunning = False
        dpg.stop_dearpygui()

    timestamp = simClock.getSimulationTime()
    absolute_time = timestamp + simClock._simulationStartTime

    
    patient.updateGlucoseData(absoluteTimestamp=absolute_time)
    patient.updateInsulinInjectionData(absoluteTimestamp=absolute_time)
    patient.updateCarbIntakeData(absoluteTimestamp=absolute_time)
    
    bg = int(patient.getLatestGlucoseReading())
    








    dpg.set_value('series_tag', [simClock.getSimulationTimestampData(), patient.getGlucoseData()])
    dpg.fit_axis_data("x_axis")
    dpg.fit_axis_data("y_axis")

    dpg.set_value('ins-series_tag', [simClock.getSimulationTimestampData(), patient.getInsulinInjectionData()])
    dpg.fit_axis_data("ins-x_axis")
    dpg.fit_axis_data("ins-y_axis")


    simTimeDDHHMM = secondsToDDHHMM(timestamp)

    dpg.set_value('sim-time', f"Simulation Time: Day: {simTimeDDHHMM[0]}, Hour: {simTimeDDHHMM[1]}, Minutes: {simTimeDDHHMM[2]}")
    dpg.set_value('sim-pt-glucose', f"Current Glucose Level  {bg} mg/dL")

    dpg.set_value('sim-rate-txt1', f"simulation rate: {simClock.getSimulationRate()}x ")

    
    color = [255,0,0,255] if bg > 180 or bg < 70 else [0,255,0,255] 


    dpg.set_value('sim-pt-risk', f"Hyperglycemia" if  bg > 180 else "hypoglycemia " if bg < 70 else "Normal")
    dpg.configure_item('sim-pt-risk', color=color)

    patientState = patient.getPatientStatus()
    if patientState:
        logTime = secondsToDDHHMM(timestamp)
        logTimestamp = f"[D {logTime[0]}:H {logTime[1]}:M {logTime[2]}] : "
        log_msg( logTimestamp + patientState)
    
    dpg.render_dearpygui_frame()

dpg.destroy_context()
    


#problem then scope then related work then summarize the then brief overview then ident Gaps