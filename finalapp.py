import streamlit as st
import folium
import json
import math
from streamlit_folium import st_folium

# ---------------- CONFIG ----------------

CORRIDORS = ["Vadapalani", "Broadway", "Thiruvanmiyur"]
BUS_CAPACITY = 40
AVAILABLE_BUSES = 3  # only for display (not simulation limit)

FIXED_DEMAND = {
    "Vadapalani": 100,
    "Broadway": 80,
    "Thiruvanmiyur": 40
}

IYYAPPANTHANGAL = (13.037455471481548, 80.1345358364268)

STOPS = {
    "Porur": (13.036249887328198, 80.15330188330523),
    "Valasaravakkam": (13.041018584890555, 80.17295100513537),
    "Iyyappanthangal": (13.037729409724287, 80.13684511959497),
    "Ramapuram": (13.025125453836557, 80.1768439794521)
}

# ---------------- SESSION STATE ----------------

if "simulation_step" not in st.session_state:
    st.session_state.simulation_step = -1

# ---------------- PAGE ----------------

st.set_page_config(layout="wide")
st.title("🚍 Demand-Driven Bus Dispatch Simulation")

# ---------------- DEMAND DISPLAY ----------------

st.subheader("📊 Corridor Demand")
col1, col2, col3 = st.columns(3)

col1.metric("Vadapalani", FIXED_DEMAND["Vadapalani"])
col2.metric("Broadway", FIXED_DEMAND["Broadway"])
col3.metric("Thiruvanmiyur", FIXED_DEMAND["Thiruvanmiyur"])

# ---------------- REQUIRED BUSES ----------------

required = {
    c: math.ceil(FIXED_DEMAND[c] / BUS_CAPACITY)
    for c in CORRIDORS
}

st.subheader("🧮 Required Buses")
st.write(
    f"Vadapalani: {required['Vadapalani']} | "
    f"Broadway: {required['Broadway']} | "
    f"Thiruvanmiyur: {required['Thiruvanmiyur']}"
)

# ---------------- DISPATCH ORDER (FULL QUEUE) ----------------

remaining = required.copy()
queue = []

# Greedy priority logic
while sum(remaining.values()) > 0:
    selected = max(remaining, key=lambda x: remaining[x])
    if remaining[selected] > 0:
        queue.append(selected)
        remaining[selected] -= 1

st.subheader("📋 Dispatch Order (Full Simulation)")
st.info(" → ".join(queue))

# ---------------- AVAILABLE BUS DISPLAY (Only Info) ----------------

dispatched = queue[:AVAILABLE_BUSES]

st.subheader("🚌 Buses Dispatched (Available Limit Info Only)")
st.success(" → ".join(dispatched))

# ---------------- SIMULATION CONTROLS ----------------

colA, colB, colC = st.columns(3)

if colA.button("▶ Start Simulation"):
    st.session_state.simulation_step = 0

if colB.button("⏭ Next Bus"):
    if st.session_state.simulation_step < len(queue) - 1:
        st.session_state.simulation_step += 1

if colC.button("🔄 Reset"):
    st.session_state.simulation_step = -1

# ---------------- MAP CREATION ----------------

m = folium.Map(location=IYYAPPANTHANGAL, zoom_start=12)

# Central Depot
folium.Marker(
    IYYAPPANTHANGAL,
    popup="Iyyappanthangal Depot (Central Brain)",
    icon=folium.Icon(color="red", icon="building", prefix='fa')
).add_to(m)

# Stop Markers
for stop_name, coordinates in STOPS.items():
    folium.Marker(
        location=coordinates,
        popup=stop_name,
        icon=folium.Icon(color="orange", icon="info-sign")
    ).add_to(m)

# ---------------- LOAD ROUTES ----------------

with open("routes_index.json", "r") as f:
    route_files = json.load(f)

# Determine Highlight Route FROM FULL QUEUE
highlight_route = None
if 0 <= st.session_state.simulation_step < len(queue):
    highlight_route = queue[st.session_state.simulation_step]

# ---------------- DRAW ROUTES ----------------

for route_name, filename in route_files.items():

    with open(filename, "r") as rf:
        route_data = json.load(rf)

    coords = route_data["coordinates"]
    base_color = route_data.get("color", "blue")

    # Highlight logic
    if highlight_route and route_name.lower().startswith(highlight_route.lower()):
        color = "yellow"
        weight = 10
    else:
        color = base_color
        weight = 6

    # Draw route line
    folium.PolyLine(
        locations=coords,
        color=color,
        weight=weight,
        opacity=0.9,
        tooltip=route_name
    ).add_to(m)

    # Terminal marker
    folium.Marker(
        coords[-1],
        popup=f"{route_name} Terminal",
        icon=folium.Icon(color=base_color)
    ).add_to(m)

# ---------------- DISPLAY MAP ----------------

st_folium(m, width=1200, height=700)