from turtle import title
import pandas as pd
import plotly.graph_objects as go

vehicle_telemetry = pd.read_csv('vehicle_telemetry.csv')




# ==============================================================================
# -- Speed ---------------------------------------------------------------------
# ==============================================================================

vehicle_telemetry_manual = vehicle_telemetry[vehicle_telemetry.Autopilot == False]
vehicle_telemetry_manual = vehicle_telemetry_manual.reset_index(drop=True)

vehicle_telemetry_auto = vehicle_telemetry[vehicle_telemetry.Autopilot == True]
vehicle_telemetry_auto = vehicle_telemetry_auto.reset_index(drop=True)

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
throttle = vehicle_telemetry['Throttle'].to_list()

#Need to clean the data, percentage signs
for i in range(0, len(throttle)):
    cleaned = throttle[i].strip()
    cleaned = cleaned[:-1]
    cleaned = int(cleaned)
    throttle[i] = cleaned

throttle_plot = throttle_plot.add_trace(go.Scatter(
    x = vehicle_telemetry['Rec_time'],
    y = throttle,
))
throttle_plot.update_layout(
    title = 'Throttle Application',
    xaxis_title = 'Rec_time (seconds)',
    yaxis_title = 'Throttle Position (Percentage)',
    hovermode = 'x unified'
)




speed_plot.show()
frame_plot.show()
throttle_plot.show()