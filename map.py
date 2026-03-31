import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.title("🚍 Demand-Driven Bus Dispatch Simulation")

# -----------------------
# Real Coordinates (Replace with your exact Google Maps values)
# -----------------------

# Depots
iyyappanthangal = (13.037455471481548, 80.1345358364268)
thiruvanmiyur = (12.98704988577527, 80.25930075361671)
vadapalani = (13.050151522465278, 80.20686655963813)
broadway = (13.087323161660331, 80.28385016221362)

# Intermediate Stops (Example – Replace with real stops)
route_thiru_stops = [
    (13.0400, 80.1200),
    (13.0200, 80.1800),
    (12.9950, 80.2300)    
]

route_vada_stops = [
    (13.0480, 80.1400),
    (13.0490, 80.1700),
    (13.0495, 80.1950)
]

route_broadway_stops = [
    (13.0600, 80.1500),
    (13.0700, 80.2000),
    (13.0800, 80.2400)
]

# -----------------------
# Create Map
# -----------------------

m = folium.Map(location=iyyappanthangal, zoom_start=12)

# -----------------------
# Add Depot Markers
# -----------------------

folium.Marker(iyyappanthangal, popup="Iyyappanthangal Depot (Central Brain)", icon=folium.Icon(color="red")).add_to(m)
folium.Marker(thiruvanmiyur, popup="Thiruvanmiyur Terminal", icon=folium.Icon(color="blue")).add_to(m)
folium.Marker(vadapalani, popup="Vadapalani Terminal", icon=folium.Icon(color="green")).add_to(m)
folium.Marker(broadway, popup="Broadway Terminal", icon=folium.Icon(color="purple")).add_to(m)

# -----------------------
# Add Stops
# -----------------------

for stop in route_thiru_stops:
    folium.CircleMarker(stop, radius=5, color="blue", fill=True).add_to(m)

for stop in route_vada_stops:
    folium.CircleMarker(stop, radius=5, color="green", fill=True).add_to(m)

for stop in route_broadway_stops:
    folium.CircleMarker(stop, radius=5, color="purple", fill=True).add_to(m)

# -----------------------
# Draw Route Corridors
# -----------------------

folium.PolyLine([iyyappanthangal] + route_thiru_stops + [thiruvanmiyur],
                color="blue",
                weight=5,
                tooltip="Thiruvanmiyur Corridor").add_to(m)

folium.PolyLine([iyyappanthangal] + route_vada_stops + [vadapalani],
                color="green",
                weight=5,
                tooltip="Vadapalani Corridor").add_to(m)

folium.PolyLine([iyyappanthangal] + route_broadway_stops + [broadway],
                color="purple",
                weight=5,
                tooltip="Broadway Corridor").add_to(m)

# -----------------------
# Display Map
# -----------------------

st_folium(m, width=1200, height=700)
