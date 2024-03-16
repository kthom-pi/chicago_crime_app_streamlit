import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import datetime
import plotly.express as px

# Constants
CRIME_DATA_PATH = "C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\Crimes_-_2001_to_Present.csv"
COMMUNITY_DATA_PATH = "C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\communities.csv"

# Function to clean robberies
@st.cache_data
def clean_robberies(crime_df, neighborhoods, crime_type, start_date, end_date):
    """Combines the crime, demographic and neighborhoods dataframe into one."""
    crime_df['Date'] = pd.to_datetime(crime_df['Date'])
    mask_1 = crime_df['Date'] >= start_date
    mask_2 = crime_df['Date'] < end_date
    crime_df = crime_df.loc[mask_1 & mask_2].sort_values(by='Date')
    crime_df['hour'] = crime_df['Date'].dt.hour
    crime_df['day'] = crime_df['Date'].dt.day
    crime_df['month'] = crime_df['Date'].dt.month
    crime_df['year'] = crime_df['Date'].dt.year

    conditions = [
        (crime_df['hour'] >= 0) & (crime_df['hour'] < 4),
        (crime_df['hour'] >= 4) & (crime_df['hour'] < 8),
        (crime_df['hour'] >= 8) & (crime_df['hour'] < 12),
        (crime_df['hour'] >= 12) & (crime_df['hour'] < 16),
        (crime_df['hour'] >= 16) & (crime_df['hour'] < 20),
        (crime_df['hour'] >= 20)
    ]

    values = ['12am to 4am', '4am to 8am', '8am to 12pm', '12pm to 4pm', '4pm to 8pm', '8pm to 12am']

    crime_df['Time of Day'] = np.select(conditions, values)
    crime_df = crime_df.loc[crime_df['Primary Type'] == crime_type]
    crime_df_1 = crime_df.merge(neighborhoods, how='left', on='Community Area')

    return crime_df_1

# Function to plot crime by time of day
@st.cache
def plot_community_time_day(df, community, begin_year, end_year):
    """Determines and plots the number of crimes in the community by the time of day."""
    mask_years = (df['Year'] >= begin_year) & (df['Year'] < end_year)
    mask_community = (df['Community'] == community)
    df = df.loc[mask_years & mask_community]

    order = ['12am to 4am', '4am to 8am', '8am to 12pm', '12pm to 4pm', '4pm to 8pm', '8pm to 12am']
    fig = px.histogram(df, x='Time of Day', category_orders={'Time of Day': order})

    return fig

# Load data
df_crime = pd.read_csv(CRIME_DATA_PATH)
df_communities = pd.read_csv(COMMUNITY_DATA_PATH)

# Sidebar
with st.sidebar:
    st.title('Neighborhood Input')
    begin_date = st.date_input('Begin Date', datetime.date(2018, 1, 1))
    ending_date = st.date_input('End Date', datetime.date(2024, 1, 10))

# Extract year
begin_year_int = begin_date.year
end_year_int = ending_date.year

# Data loading message
data_load_state = st.text('Loading data...')
new_df = clean_robberies(df_crime.loc[:1000, :], df_communities, "MOTOR VEHICLE THEFT", begin_date, ending_date)
data_load_state.text("Data loaded!")

# Display DataFrame
st.write(new_df)

# Plot crime by time of day
st.subheader('Crime by Time of Day')
time_of_day_plot = plot_community_time_day(new_df, "Rogers Park", begin_year_int, end_year_int)
st.plotly_chart(time_of_day_plot)

# Update years
update_button = st.button("Update Years")

if update_button:
    community = st.selectbox('Select Community', options=new_df['Community'].unique())
    begin_year_value = st.number_input('Begin Year', min_value=int(new_df['year'].min()), value=int(new_df['year'].min()), step=1)
    end_year_value = st.number_input('End Year', min_value=begin_year_value, value=int(new_df['year'].max()), step=1)

# Display selected or default values
st.write(f"Begin Year: {begin_year_value if begin_year_value else int(new_df['year'].min())}")
st.write(f"End Year: {end_year_value if end_year_value else int(new_df['year'].max())}")

# Plot based on user selection
if st.button('Plot'):
    fig = plot_community_time_day(new_df, community, begin_year_int, end_year_int)
    st.plotly_chart(fig)