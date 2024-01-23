import ee
import streamlit as st
import geemap.foliumap as geemap
from datetime import datetime

geemap.ee_initialize()

# st.sidebar.title("About")
# logo = "https://drive.google.com/uc?export=download&id=1MyUtL-XdUQtiGwUaAwr6GCmH0nqiEATb"
# st.sidebar.image(logo)

# def getSentinel2(start_date, end_date, admin_boundary):
#     # Get administrative boundaries (level 1).
#     admin_boundaries = ee.FeatureCollection("FAO/GAUL/2015/level0")

#     # Filter the selected administrative boundary.
#     selected_admin_boundary = admin_boundaries.filter(ee.Filter.eq("ADM0_NAME", admin_boundary))
    
#     # Import the Harmonized Sentinel-2 Surface Reflectance collection.
#     dataset = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")

#     # Filter the collection by date range.
#     sentinel2 = dataset.filterDate(start_date, end_date)

#     # Take the median value for each pixel in the date range.
#     sentinel2 = sentinel2.median().clip(selected_admin_boundary)

#     return sentinel2

def get_no2(start_date, end_date, admin_boundary):
    # Get administrative boundaries (level 1).
    admin_boundaries = ee.FeatureCollection("FAO/GAUL/2015/level1")

    # Filter the selected administrative boundary.
    selected_admin_boundary = admin_boundaries.filter(ee.Filter.eq("ADM1_NAME", admin_boundary))
    
    # Import the Harmonized Sentinel-2 Surface Reflectance collection.
    dataset = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_NO2').select('tropospheric_NO2_column_number_density')

    # Filter the collection by date range.
    no2 = dataset.filterDate(start_date, end_date)

    # Take the median value for each pixel in the date range.
    no2 = no2.mean().clip(selected_admin_boundary)

    return no2

def get_so2(start_date, end_date, admin_boundary):
    # Get administrative boundaries (level 1).
    admin_boundaries = ee.FeatureCollection("FAO/GAUL/2015/level1")

    # Filter the selected administrative boundary.
    selected_admin_boundary = admin_boundaries.filter(ee.Filter.eq("ADM1_NAME", admin_boundary))
    
    # Import the Harmonized Sentinel-2 Surface Reflectance collection.
    dataset = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_SO2").select("SO2_column_number_density")

    # Filter the collection by date range.
    so2 = dataset.filterDate(start_date, end_date)

    # Take the median value for each pixel in the date range.
    so2 = so2.mean().clip(selected_admin_boundary)

    return so2

def get_o3(start_date, end_date, admin_boundary):
    # Get administrative boundaries (level 1).
    admin_boundaries = ee.FeatureCollection("FAO/GAUL/2015/level1")

    # Filter the selected administrative boundary.
    selected_admin_boundary = admin_boundaries.filter(ee.Filter.eq("ADM1_NAME", admin_boundary))
    
    # Import the Harmonized Sentinel-2 Surface Reflectance collection.
    dataset = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_O3").select("O3_column_number_density")

    # Filter the collection by date range.
    o3 = dataset.filterDate(start_date, end_date)

    # Take the median value for each pixel in the date range.
    o3 = o3.mean().clip(selected_admin_boundary)

    return o3

def get_co(start_date, end_date, admin_boundary):
    # Get administrative boundaries (level 1).
    admin_boundaries = ee.FeatureCollection("FAO/GAUL/2015/level1")

    # Filter the selected administrative boundary.
    selected_admin_boundary = admin_boundaries.filter(ee.Filter.eq("ADM1_NAME", admin_boundary))
    
    # Import the Harmonized Sentinel-2 Surface Reflectance collection.
    dataset = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_CO").select("CO_column_number_density")

    # Filter the collection by date range.
    co = dataset.filterDate(start_date, end_date)

    # Take the median value for each pixel in the date range.
    co = co.mean().clip(selected_admin_boundary)

    return co

def get_h2o(start_date, end_date, admin_boundary):
    # Get administrative boundaries (level 1).
    admin_boundaries = ee.FeatureCollection("FAO/GAUL/2015/level1")

    # Filter the selected administrative boundary.
    selected_admin_boundary = admin_boundaries.filter(ee.Filter.eq("ADM1_NAME", admin_boundary))
    
    # Import the Harmonized Sentinel-2 Surface Reflectance collection.
    dataset = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_CO").select("H2O_column_number_density")

    # Filter the collection by date range.
    h2o = dataset.filterDate(start_date, end_date)

    # Take the median value for each pixel in the date range.
    h2o = h2o.mean().clip(selected_admin_boundary)

    return h2o

def get_ch4(start_date, end_date, admin_boundary):
    # Get administrative boundaries (level 1).
    admin_boundaries = ee.FeatureCollection("FAO/GAUL/2015/level1")

    # Filter the selected administrative boundary.
    selected_admin_boundary = admin_boundaries.filter(ee.Filter.eq("ADM1_NAME", admin_boundary))
    
    # Import the Harmonized Sentinel-2 Surface Reflectance collection.
    dataset = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_CH4").select("H2O_column_number_density")

    # Filter the collection by date range.
    ch4 = dataset.filterDate(start_date, end_date)

    # Take the median value for each pixel in the date range.
    ch4 = ch4.mean().clip(selected_admin_boundary)

    return ch4

# Set up Streamlit application
st.header("NO2 Concentration Explorer (Based on TROPOMI instrument on Sentinel-5 Precursor)")
st.text("Dataset Availability: 2018-06-28 – Today")
st.text("Resolution: 1113.2 meters")
st.text("Some layers might take some time to load...")

# Create a layout containing four columns: one for the map, two for date input, and one for admin boundary input.
col1, col2 = st.columns([8, 2])

# Initialize an interactive map
Map = geemap.Map()

# Set default starting and ending dates.
default_start_date = datetime(2022, 11, 1)
default_end_date = datetime(2022, 12, 1)

# Fetch the list of province names in Indonesia (level 0).
province_names = ee.FeatureCollection("FAO/GAUL/2015/level1").aggregate_array("ADM1_NAME").distinct().getInfo()

# Sort the province names alphabetically.
province_names.sort()

# Set default administrative boundary.
default_admin_boundary = "Dki Jakarta"

# Add start and end date input widgets to the second column with default values and a dropdown for choosing an administrative boundary.
with col2:
    start_date = str(st.date_input("Start Date", key="start_date", value=default_start_date))
    end_date = str(st.date_input("End Date", key="end_date", value=default_end_date))
    admin_boundary = st.selectbox("Select City", province_names, index=province_names.index(default_admin_boundary))

# Add the selected Sentinel-2 image and NDVI layer to the map based on the selected date range and admin boundary.
if start_date and end_date:
    roi = ee.Feature(ee.FeatureCollection("FAO/GAUL/2015/level1").filter(ee.Filter.eq("ADM1_NAME", admin_boundary)).first())
    variable_center = roi.simplify(maxError = 1).geometry()
    Map.centerObject(variable_center)
    Map.add_basemap(basemap = "HYBRID", show = True)
    Map.add_basemap(basemap = "ROADMAP", show = True)

    no2 = get_no2(start_date, end_date, admin_boundary)
    so2 = get_so2(start_date, end_date, admin_boundary)
    o3 = get_o3(start_date, end_date, admin_boundary)
    co = get_co(start_date, end_date, admin_boundary)
    ch4 = get_ch4(start_date, end_date, admin_boundary)

    Map.addLayer(no2, {
        'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red'],
        'min': 0,
        'max': 0.0002
    }, f"NO2 @{admin_boundary} ({start_date} to {end_date})")

    # Add colorbar as legend
    vis_params = {
        'min': 0,
        'max': 0.0002,
        'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red'],
    }
    
    Map.add_colorbar(
        vis_params=vis_params, # The visualization parameters of the layer
        label='mol/m^2', # The label of the colorbar
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
