
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import datetime
import plotly.express as px


# Import the community data files.
df_communities = pd.read_csv("C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\communities.csv")


# API access
# Website: https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2/data_preview

@st.cache_data
def mod_df():
    """Imports the dataframe and keeps only the desired columns."""

    # Crime database
    df_crime = pd.read_csv(
        "C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\crime_df_mod.csv")

    # Filter for the crimes of interest.
    keep_crimes = ['THEFT', 'ASSAULT', 'SEX OFFENSE', 'BURGLARY', 'CRIM SEXUAL ASSAULT',
                   'MOTOR VEHICLE THEFT', 'OFFENSE INVOLVING CHILDREN', 'CRIMINAL TRESPASS',
                   'ROBBERY', 'CRIMINAL SEXUAL ASSAULT', 'STALKING', 'HOMICIDE', 'KIDNAPPING',
                   'DOMESTIC VIOLENCE']

    df_crime_input = df_crime[df_crime['Primary Type'].isin(keep_crimes)]

    return df_crime_input

@st.cache_data
def clean_robberies(crime_df, neighborhoods, community, crime, start_date= "2018-01-01", end_date="2024-01-01"):
    """Combines the crime, demographic and neightborhoods dataframe into one."""

    # Convert 'Date' column to date time
    crime_df['Date'] = pd.to_datetime(crime_df['Date'], format='mixed')

    # Apply filter to dataframe
    mask_1 = crime_df['Date'] >= start_date
    mask_2 = crime_df['Date'] < end_date

    crime_df = crime_df.loc[mask_1 & mask_2].sort_values(by='Date')

    # Create columns with hour, day, month, year
    crime_df['hour'] = crime_df['Date'].dt.hour
    crime_df['day'] = crime_df['Date'].dt.day
    crime_df['month'] = crime_df['Date'].dt.month
    crime_df['year'] = crime_df['Date'].dt.year

    # Create a feature based on time of day
    conditions = [
        (crime_df['hour'] >= 0) & (crime_df['hour'] < 4),
        (crime_df['hour'] >= 4) & (crime_df['hour'] < 8),
        (crime_df['hour'] >= 8) & (crime_df['hour'] < 12),
        (crime_df['hour'] >= 12) & (crime_df['hour'] < 16),
        (crime_df['hour'] >= 16) & (crime_df['hour'] < 20),
        (crime_df['hour'] >= 20)
    ]

    values = ['12am to 4am', '4am to 8am', '8am to 12pm', '12pm to 4pm', '4pm to 8pm',
              '8pm to 12am']

    crime_df['Time of Day'] = np.select(conditions, values)

    # Filter for only the robberies
    crime_df = crime_df.loc[crime_df['Primary Type'] == crime]

    # Add the communities to the dataframe.
    crime_df_1 = crime_df.merge(neighborhoods, how='left', on='Community Area')

    # Filter for the community
    crime_df_2 = crime_df_1.loc[crime_df_1["Community"] == community]

    return crime_df_2


def plot_community_time_day(df):
    """Determines and plots the number of crimes in the community by the time of day."""

    # Order for the x_axis
    order = ['12am to 4am', '4am to 8am', '8am to 12pm', '12pm to 4pm', '4pm to 8pm', '8pm to 12am']

    # Plot the crimes by time of day
    fig = px.histogram(df, x='Time of Day', category_orders={'Time of Day': order})
    # Set the pie chart size.
    fig.update_layout(width=500, height=400)

    return fig

def location_description(df):
    """Plots a histogram of the location of most likely occurrence."""

    value_counts = df['Location Description'].value_counts()

    # Does a breakdown of occurrence for each crime.
    fig = px.pie(df, values=value_counts.values, names=value_counts.index)
    fig.update_layout(width=500, height=400)
    # Removes the labels
    fig.update_traces(textposition='inside', textinfo='none')

    return fig

def crime_map(df):
    """Plots a map of the different crime locations"""

    latitude = df['Latitude']
    longitude = df['Longitude']
    coordinates_data = {'latitude': latitude, 'longitude': longitude}
    df_coordinates = pd.DataFrame(coordinates_data)

    st.map(df_coordinates, color='#4dffff', size=20)

    return



st.set_page_config(
    page_title="Neighborhood Watch Statistics",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")

start_init = "2023-10-01"
end_init = "2024-01-01"

start_init_1 = pd.to_datetime(start_init)
end_init_1 = pd.to_datetime(end_init)


# Obtain the dataset with the desired columns
df_crime_1 = mod_df()


# Add a sidebar
with st.sidebar:
#with sidebar_column:
    st.title('Neighborhodd Input')
    begin_date = st.date_input('Begin Date', start_init_1)
    ending_date = st.date_input('End Date', end_init_1)
    st.text("")
    community_chosen = st.selectbox('Community', options=df_communities['Community'].unique())
    crime_type = st.selectbox('Crime Type', options=df_crime_1['Primary Type'].unique())
    st.text("")
    data_button = st.button("Update Data")

# Convert the datetime back to a string
begin_date_1 = begin_date.strftime('%Y-%m-%d')
ending_date_1 = ending_date.strftime('%Y-%m-%d')

# Content on the main colunn.
st.subheader('Table of Data')
# Placeholder for dataframe table
data_placeholder = st.empty()
new_df = clean_robberies(df_crime_1, df_communities, community_chosen, crime_type, begin_date_1, ending_date_1)
if 'new_df_key_1' not in st.session_state:
    st.session_state['new_df_key_1'] = new_df
    data_placeholder = st.empty()

st.text("")
st.text("")

# Row to hold the pie and bar charts.
col1, col2 = st.columns(2)
with col1:
    # Box Plot
    st.subheader('Time of Day')
    boxplot_placeholder = st.empty()

    #Pie chart
with col2:
    st.subheader('Location Description')
    piechart_placeholder = st.empty()

st.text("")

    # Location Map
c1 = st.container()
c1.subheader("Crime Location Map")
c1.map_placeholder = st.empty()


# Load the data and update the placeholders when "Update Data" is clicked.
if data_button:
    new_df = clean_robberies(df_crime_1, df_communities, community_chosen, crime_type, begin_date_1, ending_date_1)
    st.session_state['new_df_key_1'] = new_df
    data_placeholder.dataframe(new_df)

    # Boxplot implementation
    fig = plot_community_time_day(st.session_state['new_df_key_1'])
    boxplot_placeholder.plotly_chart(fig)

    # Piechart implementation
    fig2 = location_description(st.session_state['new_df_key_1'])
    piechart_placeholder.plotly_chart(fig2)

    # Map implementation
    fig3 = crime_map(st.session_state['new_df_key_1'])
    c1.map_placeholder = fig3








