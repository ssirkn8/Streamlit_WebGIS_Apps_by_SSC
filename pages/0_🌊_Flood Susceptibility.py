import ee
import geemap
import pandas as pd
import streamlit as st
import geemap.foliumap as geemap

geemap.ee_initialize()

# st.sidebar.title("About")
# logo = "https://drive.google.com/uc?export=download&id=1MyUtL-XdUQtiGwUaAwr6GCmH0nqiEATb"
# st.sidebar.image(logo)

gsw = ee.Image("JRC/GSW1_4/GlobalSurfaceWater")
srtm = ee.Image("USGS/SRTMGL1_003")
l8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")

# Function to cloudmask landsat 8
def cloudMask(image):
    qa = image.select('QA_PIXEL')
    dilated = 1 << 1
    cirrus = 1 << 2
    cloud = 1 << 3
    shadow = 1 << 4
    mask = qa.bitwiseAnd(dilated).eq(0) \
    .And(qa.bitwiseAnd(cirrus).eq(0)) \
    .And(qa.bitwiseAnd(cloud).eq(0)) \
    .And(qa.bitwiseAnd(shadow).eq(0))
    return image.select(['SR_B.*'], ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7']).multiply(0.0000275).add(-0.2).updateMask(mask)

# Set up Streamlit application
st.header("Flood Susceptibility Monitoring (Based on Landsat 8, EC JRC/Google, and SRTM)")
st.text("Some layers might take some time to load...")
# st.text("Dataset Availability: 2017-03-28 – Today")
# st.text("Resolution: 10 meters")

# Create a layout containing four columns: one for the map, two for date input, and one for admin boundary input.
col1, col2 = st.columns([8, 2])

# Initialize an interactive map
Map = geemap.Map()

# # Set default starting and ending dates.
# default_start_date = datetime(2022, 12, 1)
# default_end_date = datetime(2022, 12, 31)

# Fetch the list of province names in Indonesia (level 0).
city_names = ee.FeatureCollection("FAO/GAUL/2015/level2").aggregate_array("ADM2_NAME").distinct().getInfo()

# Sort the province names alphabetically.
city_names.sort()

# Set default administrative boundary.
default_admin_boundary = "Kutai Kartanegara"

# Add start and end date input widgets to the second column with default values and a dropdown for choosing an administrative boundary.
with col2:
    # start_date = str(st.date_input("Start Date", key="start_date", value=default_start_date))
    # end_date = str(st.date_input("End Date", key="end_date", value=default_end_date))
    admin_boundary = st.selectbox("Select City", city_names, index=city_names.index(default_admin_boundary))

# Add the selected Sentinel-2 image and NDVI layer to the map based on the selected date range and admin boundary.
if admin_boundary:
    adm = ee.Feature(ee.FeatureCollection("FAO/GAUL/2015/level2").filter(ee.Filter.eq('ADM2_NAME', admin_boundary)).first())
    roi = adm.geometry() 
    variable_center = adm.simplify(maxError = 1).geometry()
    Map.centerObject(variable_center)
    Map.add_basemap(basemap = "HYBRID", show = True)
    Map.add_basemap(basemap = "ROADMAP", show = True)

    # Get water data
    water = gsw.select('occurrence').clip(roi)
    # Map.addLayer(water, { 'min': 0, 'max': 100, 'palette': ['white', 'cyan', 'blue' ]}, 'Water', False)

    # Permanent water
    permanent = water.gt(80)
    Map.addLayer(permanent.selfMask(), { 'palette': 'blue' }, 'Permanent Water')

    # Rainbow palette
    rainbow = ['blue', 'cyan', 'green', 'yellow', 'red']

    # Distance from water
    distance = permanent.fastDistanceTransform().divide(30).clip(roi).reproject('EPSG:4326', None, 30)
    # Map.addLayer(distance, { 'max': 0, 'min': 5000, 'palette': rainbow}, 'Distance', False)

    # Only the distance without permanent water
    onlyDistance = distance.updateMask(distance.neq(0).And(srtm.mask()))
    Map.addLayer(onlyDistance, { 'min': 0, 'max': 5000, 'palette': rainbow}, 'Distance from permanent water')

    # Distance
    distanceScore = onlyDistance.where(onlyDistance.gt(4000), 1) \
    .where(onlyDistance.gt(3000).And(onlyDistance.lte(4000)), 2) \
    .where(onlyDistance.gt(2000).And(onlyDistance.lte(3000)), 3) \
    .where(onlyDistance.gt(1000).And(onlyDistance.lte(2000)), 4) \
    .where(onlyDistance.lte(1000), 5)
    # Map.addLayer(distanceScore, { 'min': 1, 'max': 5, 'palette': rainbow }, 'Distance hazard score', False)

    # Elevation data
    elevation = srtm.clip(roi)
    Map.addLayer(elevation, { 'min': 0, 'max': 100, 'palette': ['green', 'yellow', 'red', 'white'] }, 'DEM')

    # Elevation score
    elevScore = elevation.updateMask(distance.neq(0)).where(elevation.gt(20), 1) \
    .where(elevation.gt(15).And(elevation.lte(20)), 2) \
    .where(elevation.gt(10).And(elevation.lte(15)), 3) \
    .where(elevation.gt(5).And(elevation.lte(10)), 4) \
    .where(elevation.lte(5), 5)
    # Map.addLayer(elevScore, { 'min': 1, 'max': 5, 'palette': rainbow }, 'Elevation hazard score', False)

    # Create topographic position index
    tpi = elevation.subtract(elevation.focalMean(5).reproject('EPSG:4326', None, 30)).rename('TPI')
    Map.addLayer(tpi, { 'min': -5, 'max': 5, 'palette': ['blue', 'yellow', 'red'] }, 'TPI')

    # Topo score
    topoScore = tpi.updateMask(distance.neq(0)).where(tpi.gt(0), 1) \
    .where(tpi.gt(-2).And(tpi.lte(0)), 2) \
    .where(tpi.gt(-4).And(tpi.lte(-2)), 3) \
    .where(tpi.gt(-6).And(tpi.lte(-4)), 4) \
    .where(tpi.lte(-8), 5)
    # Map.addLayer(topoScore, { 'min': 1, 'max': 5, 'palette': rainbow }, 'Topographic hazard score', False)

    # Landsat 8
    landsat8 = l8.filterBounds(roi).filterDate('2022-01-01', '2022-12-31').map(cloudMask).median().clip(roi)
    # Map.addLayer(landsat8, { 'bands': ['B4', 'B3', 'B2']}, 'Landsat 8', False)

    # Band map
    bandMap = {
    'RED': landsat8.select('B4'),
    'NIR': landsat8.select('B5'),
    'GREEN': landsat8.select('B3'),
    }

    # NDVI
    ndvi = landsat8.expression('(NIR - RED) / (NIR + RED)', bandMap).rename('NDVI')
    Map.addLayer(ndvi, { 'min': -1, 'max': 1, 'palette': ['blue', 'white', 'green']}, 'NDVI')

    # Vegetation score
    vegScore = ndvi.updateMask(distance.neq(0)).where(ndvi.gt(0.8), 1) \
    .where(ndvi.gt(0.6).And(ndvi.lte(0.8)), 2) \
    .where(ndvi.gt(0.4).And(ndvi.lte(0.6)), 3) \
    .where(ndvi.gt(0.2).And(ndvi.lte(0.4)), 4) \
    .where(ndvi.lte(0.2), 5)
    # Map.addLayer(vegScore, { 'min': 1, 'max': 5, 'palette': rainbow }, 'Vegetation hazard score', False)

    # NDWI
    ndwi = landsat8.expression('(GREEN - NIR) / (GREEN + NIR)', bandMap).rename('NDWI')
    Map.addLayer(ndwi, { 'min': -1, 'max': 1, 'palette': ['red', 'white', 'blue']}, 'NDWI')

    # Wetness score
    wetScore = ndwi.updateMask(distance.neq(0)).where(ndwi.gt(0.6), 5) \
    .where(ndwi.gt(0.2).And(ndwi.lte(0.6)), 4) \
    .where(ndwi.gt(-0.2).And(ndwi.lte(0.2)), 3) \
    .where(ndwi.gt(-0.6).And(ndwi.lte(-0.2)), 2) \
    .where(ndwi.lte(-0.6), 1)
    # Map.addLayer(wetScore, { 'min': 1, 'max': 5, 'palette': rainbow }, 'Wetness hazard score', False)

    # Flood hazard
    floodHazard = distanceScore.add(topoScore).add(vegScore).add(wetScore).add(elevScore).rename('Flood_hazard')
    # Map.addLayer(floodHazard, { 'min': 1, 'max': 20, 'palette': rainbow }, 'Flood hazard', False)

    # Flood hazard scored
    floodHazardScore = floodHazard.where(floodHazard.gt(15), 5) \
    .where(floodHazard.gt(10).And(floodHazard.lte(15)), 4) \
    .where(floodHazard.gt(5).And(floodHazard.lte(10)), 3) \
    .where(floodHazard.gt(0).And(floodHazard.lte(5)), 2) \
    .where(floodHazard.lte(0), 1)
    Map.addLayer(floodHazardScore, { 'min': 1, 'max': 5, 'palette': ["blue", "green", "yellow", "orange", "red"] }, 'Flood Susceptibility')

    # Add colorbar as legend
    vis_params = {
        'Very low': 'blue',
        'Low': 'green',
        'Moderate': 'yellow',
        'High': 'orange',
        'Very high': 'red'
    }
    
    Map.add_legend(
        title='Flood Susceptibility',
        legend_dict=vis_params
    )

    # Map.add_colorbar(
    #     vis_params=vis_params, # The visualization parameters of the layer
    #     label='NDVI', # The label of the colorbar
    # )

    # my_sample = floodHazardScore.sample(region=roi, numPixels=5000)
    # df = geemap.ee_to_pandas(my_sample).Flood_hazard
    # df = pd.DataFrame(df)
    # flood_dict = {1: "Very Low", 2: "Low", 3: "Moderate", 4: "High", 5: "Very High"}
    # dflood = df.iloc[:, 0].copy().map(flood_dict)
    # ax = dflood.value_counts().plot(kind='barh', figsize=(10, 5))
    # ax.set_ylabel("Flood Susceptibility")
    # ax.set_xlabel("Pixel Count")
    # for container in ax.containers:
    #     ax.bar_label(container, padding=2, fontsize=7)

    with col1:
        Map.to_streamlit(height=600)
        # st.pyplot(ax)

else:
    with col1:
        Map.to_streamlit(height=600)
        # st.pyplot(ax)

# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
