import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

vehicle_telemetry = pd.read_csv('vehicle_telemetry.csv')
vehicle_telemetry_manual = pd.read_csv('vehicle_telemetry.csv')
vehicle_telemetry_auto = pd.read_csv('vehicle_telemetry.csv')




# ==============================================================================
# -- Speed ---------------------------------------------------------------------
# ==============================================================================
vehicle_telemetry_manual['Speed'] = np.where(vehicle_telemetry_manual.Autopilot == True, 0, vehicle_telemetry_manual['Speed'])
vehicle_telemetry_auto['Speed'] = np.where(vehicle_telemetry_auto.Autopilot == False, 0, vehicle_telemetry_auto['Speed'])

speed_plot = go.Figure()
speed_plot = speed_plot.add_trace(go.Scatter(
    x=vehicle_telemetry_manual['Rec_time'],
    y=vehicle_telemetry_manual['Speed'],
    name='Manual Control'
    ))
speed_plot = speed_plot.add_trace(go.Scatter(
    x=vehicle_telemetry_auto['Rec_time'],
    y=vehicle_telemetry_auto['Speed'],
    name='Autopilot'
    ))
speed_plot.update_layout(
    title = 'Speed vs Time',
    xaxis_title = 'Rec_time (seconds)',
    yaxis_title = 'Speed (kph)',
    hovermode = 'x unified'
)




# ==============================================================================
# -- Performance (Frames) ------------------------------------------------------
# ==============================================================================
frame_plot = go.Figure()
frame_plot = frame_plot.add_trace(go.Scatter(
    x = vehicle_telemetry['Rec_time'],
    y = vehicle_telemetry['Server_fps'],
    name='Server'
))
frame_plot = frame_plot.add_trace(go.Scatter(
    x = vehicle_telemetry['Rec_time'],
    y = vehicle_telemetry['Client_fps'],
    name='Client'
))
frame_plot.update_layout(
    title = 'Server & Client Performance',
    xaxis_title = 'Rec_time (seconds)',
    yaxis_title = 'Performance (Frames per Second)',
    hovermode = 'x unified'
)




# ==============================================================================
# -- Throttle ------------------------------------------------------------------
# ==============================================================================
throttle_plot = go.Figure()
vehicle_telemetry_manual['Throttle'] = np.where(vehicle_telemetry_manual.Autopilot == True, '0%', vehicle_telemetry_manual['Throttle'])
vehicle_telemetry_auto['Throttle'] = np.where(vehicle_telemetry_auto.Autopilot == False, '0%', vehicle_telemetry_auto['Throttle'])

throttle_manual = vehicle_telemetry_manual['Throttle'].to_list()
throttle_auto = vehicle_telemetry_auto['Throttle'].to_list()

#Need to clean the data, percentage signs
for i in range(0, len(throttle_manual)):
    cleaned = throttle_manual[i].strip()
    cleaned = cleaned[:-1]
    cleaned = int(cleaned)
    throttle_manual[i] = cleaned

throttle_plot = throttle_plot.add_trace(go.Scatter(
    x = vehicle_telemetry['Rec_time'],
    y = throttle_manual,
    name='Manual Control'
))

#Need to clean the data, percentage signs
for i in range(0, len(throttle_auto)):
    cleaned = throttle_auto[i].strip()
    cleaned = cleaned[:-1]
    cleaned = int(cleaned)
    throttle_auto[i] = cleaned

throttle_plot = throttle_plot.add_trace(go.Scatter(
    x = vehicle_telemetry['Rec_time'],
    y = throttle_auto,
    name='Autopilot'
))

throttle_plot.update_layout(
    title = 'Throttle Application',
    xaxis_title = 'Rec_time (seconds)',
    yaxis_title = 'Throttle Position (Percentage)',
    hovermode = 'x unified'
)




# ==============================================================================
# -- Brake ---------------------------------------------------------------------
# ==============================================================================
brake_plot = go.Figure()
vehicle_telemetry_manual['Brake'] = np.where(vehicle_telemetry_manual.Autopilot == True, '0%', vehicle_telemetry_manual['Brake'])
vehicle_telemetry_auto['Brake'] = np.where(vehicle_telemetry_auto.Autopilot == False, '0%', vehicle_telemetry_auto['Brake'])

brake_manual = vehicle_telemetry_manual['Brake'].to_list()
brake_auto = vehicle_telemetry_auto['Brake'].to_list()

#Need to clean the data, percentage signs
for i in range(0, len(brake_manual)):
    cleaned = brake_manual[i].strip()
    cleaned = cleaned[:-1]
    cleaned = int(cleaned)
    brake_manual[i] = cleaned

brake_plot = brake_plot.add_trace(go.Scatter(
    x = vehicle_telemetry['Rec_time'],
    y = brake_manual,
    name='Manual Control'
))

#Need to clean the data, percentage signs
for i in range(0, len(brake_auto)):
    cleaned = brake_auto[i].strip()
    cleaned = cleaned[:-1]
    cleaned = int(cleaned)
    brake_auto[i] = cleaned

brake_plot = brake_plot.add_trace(go.Scatter(
    x = vehicle_telemetry['Rec_time'],
    y = brake_auto,
    name='Autopilot'
))

brake_plot.update_layout(
    title = 'Brake Application',
    xaxis_title = 'Rec_time (seconds)',
    yaxis_title = 'Brake Position (Percentage)',
    hovermode = 'x unified'
)




# ==============================================================================
# -- Steering ------------------------------------------------------------------
# ==============================================================================
steering_plot = go.Figure()
vehicle_telemetry_manual['Steering'] = np.where(vehicle_telemetry_manual.Autopilot == True, 0, vehicle_telemetry_manual['Steering'])
vehicle_telemetry_auto['Steering'] = np.where(vehicle_telemetry_auto.Autopilot == False, 0, vehicle_telemetry_auto['Steering'])

steering_plot = steering_plot.add_trace(go.Scatter(
    x = vehicle_telemetry_manual['Rec_time'],
    y = vehicle_telemetry_manual['Steering'],
    name='Manual Control'
))

steering_plot = steering_plot.add_trace(go.Scatter(
    x = vehicle_telemetry_auto['Rec_time'],
    y = vehicle_telemetry_auto['Steering'],
    name='Autopilot'
))

steering_plot.update_layout(
    title = 'Steering Input',
    xaxis_title = 'Rec_time (seconds)',
    yaxis_title = 'Steering Position (-1 to 1 = Left lock to Right lock)',
    hovermode = 'x unified'
)




# ==============================================================================
# -- Height --------------------------------------------------------------------
# ==============================================================================
height_plot = go.Figure()
vehicle_telemetry_manual['Height'] = np.where(vehicle_telemetry_manual.Autopilot == True, 0, vehicle_telemetry_manual['Height'])
vehicle_telemetry_auto['Height'] = np.where(vehicle_telemetry_auto.Autopilot == False, 0, vehicle_telemetry_auto['Height'])

height_manual = vehicle_telemetry_manual['Height'].to_list()
height_auto = vehicle_telemetry_auto['Height'].to_list()

# #Need to clean the data, m
# for i in range(0, len(height_manual)):
#     cleaned = height_manual[i].strip()
#     cleaned = cleaned[:-2]
#     cleaned = int(cleaned)
#     height_manual[i] = cleaned

height_plot = height_plot.add_trace(go.Scatter(
    x = vehicle_telemetry['Rec_time'],
    y = height_manual,
    name='Manual Control'
))

# #Need to clean the data, m
# for i in range(0, len(height_auto)):
#     cleaned = height_auto[i].strip()
#     cleaned = cleaned[:-2]
#     cleaned = int(cleaned)
#     height_auto[i] = cleaned

height_plot = height_plot.add_trace(go.Scatter(
    x = vehicle_telemetry['Rec_time'],
    y = height_auto,
    name='Autopilot'
))

height_plot.update_layout(
    title = 'Height vs Time',
    xaxis_title = 'Rec_time (seconds)',
    yaxis_title = 'Height Above Ground Level (meters)',
    hovermode = 'x unified'
)




# ==============================================================================
# -- Collisions ----------------------------------------------------------------
# ==============================================================================
collision_data = pd.read_csv('collision_data.csv')
collision_data = collision_data.sort_values(by ='Intensity' , ascending=True)
collision_data = collision_data.drop_duplicates(subset=['Rec_time'], keep='last')

coll_plot = px.bar(
    collision_data, 
    x='Rec_time', y='Intensity',
    hover_data=['Event'], color='Intensity',
    labels={'Rec_time':'Rec_time (seconds)', 'Intensity': 'Collision Intensity'}, 
)








speed_plot.show()
frame_plot.show()
throttle_plot.show()
brake_plot.show()
steering_plot.show()
height_plot.show()
coll_plot.show()