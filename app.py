# Import necessary libraries
import streamlit as st # A library for building interactive data applications
import pandas as pd # A library for data manipulation and analysis
import numpy as np # A library for numerical computing
import plotly.express as px # A library for data visualization
import pydeck as pdk # A library for 3D mapping

# Define the URL of the data file
# DATA_URL = "D:\\Python\\pythonProjects\\PythonStreamlitProject\\Motor_Vehicle_Collisions_-_Crashes.csv"
# Set the title and description of the app
st.title("Motor Vehicle🚗 Collisions💥 in New York 🗽")
st.markdown("This app analyzes the vehicle collision data")

# Define a function to load the data
@st.cache_data(persist=True) # Cache the data to improve performance
def load_data(nrows):
   # Load the data, parse the date/time column, drop rows with missing latitude/longitude,
   # convert column names to lowercase, and rename the date/time column
   data = pd.read_csv("Motor_Vehicle_Collisions.zip", nrows=nrows, parse_dates=['CRASH_DATE', 'CRASH_TIME'])
   data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
   def lowercase(x): return str(x).lower()
   data.rename(lowercase, axis='columns', inplace=True)
   data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
   return data

# Load the data and store the original data for later use
data = load_data(100000)
original_data = data

# Show the raw data if the user checks the box
if st.checkbox("Show Raw Data", False):
   st.subheader('Raw Data')
   st.write(data)

# Display the main data exploration section
st.header("# Data Exploration")
st.subheader('Where are the most injuries occuring in NYC?')

# Get the number of injured persons from the user
injuries = st.slider("No of persons injured in collisions", 0, 19)

# Display the map of collisions with at least the specified number of injured persons
st.map(data.query("injured_persons >= @injuries")[["latitude", "longitude"]].dropna(how="any"))

# Display the section for analyzing collisions at a specific time of day
st.subheader('How many collisions occured at a specific time of day?')

# Get the hour from the user
hour = st.slider("Hours to look at...", 0, 23)

# Filter the data to only include collisions that occurred during the specified hour
data = data[data['date/time'].dt.hour == hour]

# Display the number of collisions and the 3D map for the specified hour
st.markdown("Collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))

# Display the 3D map using pydeck
midpoint = (np.average(data['latitude']), np.average(data['longitude']))
st.write(pdk.Deck(
   map_style="mapbox://styles/mapbox/light-v9",
   initial_view_state={
       "latitude": midpoint[0],
       "longitude": midpoint[1],
       "zoom": 11,
       "pitch": 50,
   },
   layers=[
       pdk.Layer("HexagonLayer",
           data=data[['date/time', 'latitude', 'longitude']],
           get_position=['longitude', 'latitude'],
           radius=100,
           extruded=True,
           pickable=True,
           elevation_scale=4,
           elevation_range=[0, 1000],
       ),
   ],
))

# Display the chart of collisions by minute for the specified hour
filtered = data[(data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x='minute', y='crashes'
            ,hover_data=['minute', 'crashes'], height=400)
st.write(fig)
st.subheader("Breakdown by minute between %i:00 and %i:00" %
            (hour, (hour + 1) % 24))

# Display the top 5 dangerous streets by affected type
st.subheader("Top 5 dangerous streets by affected type")
select = st.selectbox('Affected type of people:', ['Pedestrians', 'Cyclists', 'Motorists'])

# Display the top 5 dangerous streets for the selected type of affected person
if select == 'Pedestrians':
   st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]]
            .sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any')[:5])

elif select == 'Cyclists':
   st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]]
            .sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any')[:5])

else:
   st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]]
            .sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:5])
