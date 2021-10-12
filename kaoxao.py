### Streamlit Geodatasci 

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
import seaborn as sns
import urllib.request
from PIL import Image
import datetime

# SETTING PAGE CONFIG TO WIDE MODE
st.set_page_config(layout="wide")

# LOADING DATA
DATE_TIME = "date/time"
DATA_URL = (
    "https://github.com/kaoxao/heraku/raw/main/data_stlit.pq"
)

### Cache
@st.cache(persist=True)
def load_data_origin():
    datastart = pd.read_parquet(DATA_URL)
    datastart = datastart[['timestart','latstartl','lonstartl']].copy()
    datastart = datastart.rename(columns = {'timestart': 'Date/Time', 'latstartl': 'Lat', 'lonstartl': 'Lon'}, inplace = False)
    lowercase = lambda x: str(x).lower()
    datastart.rename(lowercase, axis="columns", inplace=True)
    datastart[DATE_TIME] = pd.to_datetime(datastart[DATE_TIME],format= '%d/%m/%Y %H:%M')
    return datastart.sample(100_000)
    
@st.cache(persist=True)
def load_data_destination():
    datastop = pd.read_parquet(DATA_URL)
    datastop = datastop[['timestop','latstop','lonstop']].copy()
    datastop = datastop.rename(columns = {'timestop': 'Date/Time', 'latstop': 'Lat', 'lonstop': 'Lon'}, inplace = False)
    lowercase = lambda x: str(x).lower()
    datastop.rename(lowercase, axis="columns", inplace=True)
    datastop[DATE_TIME] = pd.to_datetime(datastop[DATE_TIME],format= '%d/%m/%Y %H:%M')
    return datastop.sample(100_000)


data1 = load_data_origin()
data2 = load_data_destination()

# create Map
def map(data, lat, lon, zoom):
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": lat,
            "longitude": lon,
            "zoom": zoom,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=data,
                get_position=["lon", "lat"],
                radius=100,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ]
    ))

data1 = load_data_origin()
data2 = load_data_destination()

c1, c2 = st.columns((3,2))
# Set title name
with c1:
    st.title(' Recording transportation in Bangkok 1 Jan 2019 to 5 Jan 2019 \
                ') 
    st.markdown(""" Visualization of transportation, showing the destination with \
                    hexagon on map and histogram show in the range of minutes """)

with c2:
    st.markdown(' ')
    st.markdown(' ')
    st.markdown(' Name : Kanokphon Sitth')
    st.markdown(' ID : 6130801021 ')
    st.markdown(' Deploy : Heruko ')

st.write('''
***
''')

# start - stop data
start = datetime.date(2019,1,1)
stop = datetime.date(2019,1,5)

# sidebar
st.sidebar.header(' Choosing day ')
select_day = st.sidebar.slider('Day', start, stop)
select_hour = st.sidebar.selectbox("Hour", [ str(x) for x in range(0,24)])
select_hour = int(select_hour)
data1 = data1[(data1[DATE_TIME].dt.date == select_day) & (data1[DATE_TIME].dt.hour == select_hour)]
data2 = data2[(data2[DATE_TIME].dt.date == select_day) & (data2[DATE_TIME].dt.hour == select_hour)]

st.header( select_day )

## Seperate side
row1_1, row1_2 = st.columns(2)

## Called Map
zoom_level = 11
midpoint = [13.75, 100.525]


with row1_1:
    st.subheader("Start destination")
    st.warning("Time : %i:00 - %i:00" % (select_hour, (select_hour + 1) % 24 ))
    map(data1, midpoint[0], midpoint[1], zoom_level)
    
with row1_2:
    st.subheader("End destination")
    st.warning("Time : %i:00 - %i:00" % (select_hour, (select_hour + 1) % 24))
    map(data2, midpoint[0], midpoint[1], zoom_level)

# Hist 1 
r31, r32 = st.columns(2)
filtered1 = data1[(data1[DATE_TIME].dt.hour >= select_hour) & (data1[DATE_TIME].dt.hour < (select_hour + 1))]
hist1 = np.histogram(filtered1[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data1 = pd.DataFrame({"minute": range(60), "Start Origin": hist1})
with r31:
    st.altair_chart(alt.Chart(chart_data1)
        .mark_area(
            interpolate='step-after',
        ).encode(
            x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
            y=alt.Y("Start Origin:Q"),
            tooltip=['minute', 'Start Origin']
        ).configure_mark(
            opacity=0.5,
            color='orange'
        ), use_container_width=True)


## Hist 2
filtered2 = data2[(data2[DATE_TIME].dt.hour >= select_hour) & (data2[DATE_TIME].dt.hour < (select_hour + 1))]
hist2 = np.histogram(filtered2[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data2 = pd.DataFrame({"minute": range(60), "Destination Origin": hist2})
with r32:
    st.altair_chart(alt.Chart(chart_data2)
        .mark_area(
            interpolate='step-after',
        ).encode(
            x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
            y=alt.Y("Destination Origin:Q"),
            tooltip=['minute', 'Destination Origin']
        ).configure_mark(
            opacity=0.5,
            color='red'
        ), use_container_width=True)
        
st.write('''
***
''')