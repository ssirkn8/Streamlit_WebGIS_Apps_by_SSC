import ee
import streamlit as st
import geemap.foliumap as geemap
from datetime import datetime

geemap.ee_initialize()

# st.sidebar.title("About")
# logo = "https://drive.google.com/uc?export=download&id=1MyUtL-XdUQtiGwUaAwr6GCmH0nqiEATb"
# st.sidebar.image(logo)

def getSentinel2(start_date, end_date, admin_boundary):
    # Get administrative boundaries (level 1).
    admin_boundaries = ee.FeatureCollection("FAO/GAUL/2015/level0")

    # Filter the selected administrative boundary.
    selected_admin_boundary = admin_boundaries.filter(ee.Filter.eq("ADM0_NAME", admin_boundary))
    
    # Import the Harmonized Sentinel-2 Surface Reflectance collection.
    dataset = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")

    # Filter the collection by date range.
    sentinel2 = dataset.filterDate(start_date, end_date)

    # Take the median value for each pixel in the date range.
    sentinel2 = sentinel2.median().clip(selected_admin_boundary)

    return sentinel2

# Set up Streamlit application
st.header("NDVI Explorer (Based on Sentinel-2 Harmonized Dataset)")
st.text("Dataset Availability: 2017-03-28 – Today")
st.text("Resolution: 10 meters")

# Create a layout containing four columns: one for the map, two for date input, and one for admin boundary input.
col1, col2 = st.columns([8, 2])

# Initialize an interactive map
Map = geemap.Map()

# Set default starting and ending dates.
default_start_date = datetime(2022, 12, 1)
default_end_date = datetime(2022, 12, 31)

# Fetch the list of province names in Indonesia (level 0).
nation_names = ee.FeatureCollection("FAO/GAUL/2015/level0").aggregate_array("ADM0_NAME").distinct().getInfo()

# Sort the province names alphabetically.
nation_names.sort()

# Set default administrative boundary.
default_admin_boundary = "Indonesia"

# Add start and end date input widgets to the second column with default values and a dropdown for choosing an administrative boundary.
with col2:
    start_date = str(st.date_input("Start Date", key="start_date", value=default_start_date))
    end_date = str(st.date_input("End Date", key="end_date", value=default_end_date))
    admin_boundary = st.selectbox("Select Country", nation_names, index=nation_names.index(default_admin_boundary))

# Add the selected Sentinel-2 image and NDVI layer to the map based on the selected date range and admin boundary.
if start_date and end_date:
    roi = ee.Feature(ee.FeatureCollection("FAO/GAUL/2015/level0").filter(ee.Filter.eq("ADM0_NAME", admin_boundary)).first())
    variable_center = roi.simplify(maxError = 1).geometry()
    Map.centerObject(variable_center)
    Map.add_basemap(basemap = "HYBRID", show = True)
    Map.add_basemap(basemap = "ROADMAP", show = True)

    sentinel2 = getSentinel2(start_date, end_date, admin_boundary)
    
    # Calculate NDVI.
    ndvi = sentinel2.normalizedDifference(['B8', 'B4']).clamp(0, 1).rename('NDVI')
    
    sentinel2 = sentinel2.addBands(ndvi)

    Map.addLayer(sentinel2.select('NDVI'), {
        'palette': ['white', 'darkgreen'],
        'min': 0,
        'max': 1
    }, f"NDVI @{admin_boundary} ({start_date} to {end_date})")

    # Add colorbar as legend
    vis_params = {
        'min': 0,
        'max': 1,
        'palette': ['white', 'darkgreen'],
    }
    
    Map.add_colorbar(
        vis_params=vis_params, # The visualization parameters of the layer
        label='NDVI', # The label of the colorbar
    )

    # sample = sentinel2_with_ndvi.sample(
    #     region = roi,
    #     scale = 1000,
    # )

    # table = sample.

    with col1:
        Map.to_streamlit(height=600)

else:
    with col1:
        Map.to_streamlit(height=600)

# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
