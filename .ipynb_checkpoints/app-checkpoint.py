import streamlit as st
import pandas as pd
import numpy as np
from shapely.geometry import Polygon, Point
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="GeoStone AI",
    layout="wide"
)

st.title("🛰 GeoStone AI Land Measurement System")
st.subheader("Smart Survey | Boundary Alert | GPS Correction")

# Load data
df = pd.read_csv("geostone_land_dataset.csv")
df.columns = df.columns.str.strip()

# Sidebar
plot_id = st.sidebar.selectbox(
    "Select Plot",
    df["Plot_ID"].unique()
)

plot_data = df[df["Plot_ID"] == plot_id]

coords = list(zip(
    plot_data["Latitude"],
    plot_data["Longitude"]
))

# Polygon
polygon = Polygon(coords)

# Area
def convert_to_meters(lat, lon):
    x = lat * 111320
    y = lon * 111320
    return (x, y)

meter_coords = [convert_to_meters(lat, lon) for lat, lon in coords]
meter_polygon = Polygon(meter_coords)

calculated_area = meter_polygon.area / 4046.86
actual_area = plot_data["Actual_Area_Acre"].iloc[0]

# Display
col1, col2 = st.columns(2)

with col1:
    st.metric("Actual Area", round(actual_area, 2))
    st.metric("Calculated Area", round(calculated_area, 2))

with col2:
    st.metric("Shape Type", plot_data["Shape_Type"].iloc[0])
    st.metric(
        "Boundary Errors",
        int(plot_data["Boundary_Error"].sum())
    )

# Live GPS check
st.subheader("📍 Live Boundary Checker")

user_lat = st.number_input("Enter Latitude")
user_lon = st.number_input("Enter Longitude")

if st.button("Check Position"):
    point = Point(user_lat, user_lon)

    if polygon.contains(point):
        st.success("Inside Boundary ✅")
    else:
        st.error("Outside Boundary 🚨")

# Map
st.subheader("🗺 Plot Map")

m = folium.Map(
    location=[coords[0][0], coords[0][1]],
    zoom_start=18
)

folium.Polygon(
    locations=coords,
    color="blue",
    fill=True,
    fill_color="green",
    fill_opacity=0.4
).add_to(m)

for i, point in enumerate(coords):
    folium.Marker(
        location=point,
        popup=f"Point {i+1}"
    ).add_to(m)

st_folium(m, width=1000, height=500)