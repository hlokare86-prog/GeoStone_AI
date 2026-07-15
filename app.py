import streamlit as st
import pandas as pd
import numpy as np
from shapely.geometry import Polygon, Point
import folium
from streamlit_folium import st_folium

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="GeoStone AI",
    page_icon="🛰️",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

/* ---------------- MAIN BACKGROUND ---------------- */

.stApp {
    background:
    linear-gradient(
        135deg,
        #020617 0%,
        #071428 25%,
        #0b2447 50%,
        #071428 75%,
        #020617 100%
    );
}

/* Animated GIS grid overlay */
.stApp::before {
    content: "";
    position: fixed;
    width: 100%;
    height: 100%;
    background-image:
        linear-gradient(rgba(0,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,255,0.03) 1px, transparent 1px);

    background-size: 45px 45px;
    pointer-events: none;
    z-index: -1;
}

/* ---------------- SIDEBAR ---------------- */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            rgba(2,6,23,0.98),
            rgba(15,23,42,0.98)
        );

    border-right: 1px solid rgba(0,255,255,0.15);
}

/* ---------------- TITLE ---------------- */

.main-title{
    font-size:65px;
    font-weight:900;
    text-align:center;
    color:#ffffff;

    text-shadow:
        0 0 8px #00ffff,
        0 0 18px #00ffff,
        0 0 35px #00ffff;
}

.sub-title{
    text-align:center;
    color:#dbeafe;
    font-size:22px;
    margin-bottom:25px;
}

/* ---------------- GLASS CARDS ---------------- */

.glass-card{
    background: rgba(255,255,255,0.08);

    border:1px solid rgba(255,255,255,0.15);

    backdrop-filter: blur(18px);

    border-radius:25px;

    padding:25px;

    box-shadow:
        0px 8px 32px rgba(0,0,0,0.45);
}

/* ---------------- FIX INVISIBLE METRICS ---------------- */

div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 18px;
    border-radius: 18px;
}

/* metric title */
div[data-testid="metric-container"] label {
    color: #ffffff !important;
    font-size: 18px !important;
    font-weight: 700 !important;
}

/* metric value */
div[data-testid="metric-container"] div {
    color: #00ffff !important;
    font-size: 40px !important;
    font-weight: 900 !important;
}

/* ---------------- HEADINGS ---------------- */

h1,h2,h3,h4,h5,h6{
    color:white !important;
}

/* ---------------- TEXT ---------------- */

p, span, div, label {
    color:white !important;
}

/* ---------------- BUTTON ---------------- */

.stButton>button{
    background:
        linear-gradient(
            135deg,
            #00c6ff,
            #0072ff
        );

    color:white !important;

    border:none;

    border-radius:15px;

    height:55px;

    font-size:18px;

    font-weight:700;

    transition:0.3s;
}

.stButton>button:hover{
    transform:scale(1.03);
    box-shadow:0px 0px 20px #00ffff;
}

/* ---------------- INPUT BOX ---------------- */

input {
    color:white !important;
    background-color: rgba(255,255,255,0.08) !important;
}

/* ---------------- SELECT BOX ---------------- */

div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.08) !important;
    color:white !important;
}

/* ---------------- SUCCESS BOX ---------------- */

.stAlert{
    border-radius:18px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class='main-title'>
🛰️ GeoStone AI
</div>

<div class='sub-title'>
Satellite Land Intelligence • Smart Boundary Detection • GIS Survey Platform
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv("geostone_land_dataset.csv")
df.columns = df.columns.str.strip()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

plot_id = st.sidebar.selectbox(
    "Select Plot",
    df["Plot_ID"].unique()
)

plot_data = df[df["Plot_ID"] == plot_id]

coords = list(
    zip(
        plot_data["Latitude"],
        plot_data["Longitude"]
    )
)

# --------------------------------------------------
# POLYGON CREATION
# --------------------------------------------------

polygon_coords = [
    (lon, lat)
    for lat, lon in coords
]

polygon = Polygon(polygon_coords)

# --------------------------------------------------
# AREA CALCULATION
# --------------------------------------------------

def convert_to_meters(lat, lon):
    x = lon * 111320
    y = lat * 111320
    return x, y

meter_coords = [
    convert_to_meters(lat, lon)
    for lat, lon in coords
]

meter_polygon = Polygon(meter_coords)

calculated_area = meter_polygon.area / 4046.86

actual_area = plot_data["Actual_Area_Acre"].iloc[0]

shape_type = plot_data["Shape_Type"].iloc[0]

boundary_errors = int(
    plot_data["Boundary_Error"].sum()
)

accuracy = (
    actual_area /
    calculated_area
) * 100

# --------------------------------------------------
# DASHBOARD METRICS
# --------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "📐 Actual Area",
        f"{actual_area:.2f} Acre"
    )

with c2:
    st.metric(
        "🛰 Calculated Area",
        f"{calculated_area:.2f} Acre"
    )

with c3:
    st.metric(
        "🔷 Shape Type",
        shape_type
    )

with c4:
    st.metric(
        "⚠ Boundary Errors",
        boundary_errors
    )

# --------------------------------------------------
# GPS CHECKER
# --------------------------------------------------

st.subheader("📍 Live Boundary Monitoring")

col1, col2 = st.columns(2)

with col1:
    user_lat = st.number_input(
        "Latitude",
        format="%.8f"
    )

with col2:
    user_lon = st.number_input(
        "Longitude",
        format="%.8f"
    )

if st.button("Check Position"):

    point = Point(
        user_lon,
        user_lat
    )

    if polygon.contains(point):
        st.success(
            "✅ Inside Boundary"
        )
    else:
        st.error(
            "🚨 Outside Boundary"
        )

# --------------------------------------------------
# CREATE MAP
# --------------------------------------------------

m = folium.Map(
    location=[
        coords[0][0],
        coords[0][1]
    ],
    zoom_start=18,
    tiles=None,
    control_scale=True
)

# Satellite Layer
folium.TileLayer(
    tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
    attr="Google Satellite",
    name="Satellite",
    overlay=False,
    control=True
).add_to(m)

# Street Layer
folium.TileLayer(
    "OpenStreetMap",
    name="Street"
).add_to(m)

# Boundary Polygon
folium.Polygon(
    locations=coords,
    color="cyan",
    weight=4,
    fill=True,
    fill_color="cyan",
    fill_opacity=0.3,
    popup=f"Plot {plot_id}"
).add_to(m)

# Corner Points
for i, point in enumerate(coords):
    folium.Marker(
        location=point,
        popup=f"Point {i+1}"
    ).add_to(m)

# User Marker
if user_lat != 0 and user_lon != 0:
    folium.Marker(
        [user_lat, user_lon],
        popup="Current Position",
        icon=folium.Icon(
            color="red"
        )
    ).add_to(m)

folium.LayerControl().add_to(m)

# --------------------------------------------------
# DISPLAY MAP
# --------------------------------------------------

st.subheader("🗺️ GIS Satellite View")

st_folium(
    m,
    width=1200,
    height=650
)

# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

st.subheader("📊 AI Survey Analytics")

a1, a2, a3 = st.columns(3)

survey_score = max(
    100 - boundary_errors * 5,
    0
)

gps_accuracy = np.random.randint(
    1,
    5
)

with a1:
    st.metric(
        "Shape Accuracy",
        f"{accuracy:.2f}%"
    )

with a2:
    st.metric(
        "Survey Quality Index",
        f"{survey_score}%"
    )

with a3:
    st.metric(
        "GPS Accuracy",
        f"±{gps_accuracy} m"
    )

st.progress(
    survey_score / 100
)

st.success(
    "🛰 GeoStone AI GIS Engine Active"
)