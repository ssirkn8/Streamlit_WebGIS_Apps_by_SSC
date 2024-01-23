import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")

# st.sidebar.info(
#     """
#     - Web App URL: <https://streamlit.geemap.org>
#     - GitHub repository: <https://github.com/giswqs/streamlit-geospatial>
#     """
# )

# ssc_logo = "https://drive.google.com/uc?export=download&id=18zo1EP0x3VHWDFz9doNokYXqAs627DBI"
# st.sidebar.image(ssc_logo)

# st.sidebar.title("Contact")
# st.sidebar.info(
#     """
#     Qiusheng Wu: <https://wetlands.io>
#     [GitHub](https://github.com/giswqs) | [Twitter](https://twitter.com/giswqs) | [YouTube](https://www.youtube.com/c/QiushengWu) | [LinkedIn](https://www.linkedin.com/in/qiushengwu)
#     """
# )

# ssc_logo = "https://drive.google.com/file/d/18zo1EP0x3VHWDFz9doNokYXqAs627DBI/view?usp=drive_link"
# st.image(ssc_logo)

st.title("WebGIS Applications by Smart System Center (SSC)")

st.markdown(
    """

    This multi-page web app demonstrates various interactive WebGIS apps derived from GIS analysis created using [streamlit](https://streamlit.io) and open-source mapping libraries, 
    mainly [leafmap](https://leafmap.org) and [geemap](https://geemap.org).

    (Adopted from: [streamlit-multipage-template](https://github.com/giswqs/streamlit-multipage-template) by [Dr. Qiusheng Wu](https://github.com/giswqs))

    """
)

st.info("Click on the left sidebar menu to navigate to the different apps.")

st.subheader("Timelapse of Satellite Imagery")
st.markdown(
"""
    The following timelapse animations were created using the Timelapse web app. Click `Timelapse` on the left sidebar menu to create your own timelapse for any location around the globe.
"""
)

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.image("https://github.com/giswqs/data/raw/main/timelapse/spain.gif")
    st.image("https://github.com/giswqs/data/raw/main/timelapse/las_vegas.gif")

with row1_col2:
    st.image("https://github.com/giswqs/data/raw/main/timelapse/goes.gif")
    st.image("https://github.com/giswqs/data/raw/main/timelapse/fire.gif")
