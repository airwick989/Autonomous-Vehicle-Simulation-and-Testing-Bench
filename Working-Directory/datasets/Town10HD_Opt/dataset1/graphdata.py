from turtle import title
import pandas as pd
import plotly.express as px

vehicle_telemetry = pd.read_csv('vehicle_telemetry.csv')
speed_plot = px.line(vehicle_telemetry, x = 'Rec_time', y = 'Speed', title = 'Vehicle Speed')
speed_plot.show()