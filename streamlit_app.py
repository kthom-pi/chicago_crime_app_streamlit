
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import datetime
import plotly.express as px


# Import the data files.
# Crime database

df_crime = pd.read_csv("C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\Crimes_-_2001_to_Present.csv")

# Communities database
df_communities = pd.read_csv("C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\communities.csv")

# Create a smaller df for testing purposes
df_crime_1 = df_crime.loc[:1000, :]

crime = "MOTOR VEHICLE THEFT"
#community = "Rogers Park"

start_init = "2018-01-01"
end_init = "2024-01-01"


def clean_robberies(crime_df, neighborhoods, crime_type, start_date=start_init, end_date=end_init):
    """Combines the crime, demographic and neightborhoods dataframe into one."""

    # Convert 'Date' column to date time
    crime_df['Date'] = pd.to_datetime(crime_df['Date'])

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
    crime_df = crime_df.loc[crime_df['Primary Type'] == crime_type]

    # Add the communities to the dataframe.
    crime_df_1 = crime_df.merge(neighborhoods, how='left', on='Community Area')

    return crime_df_1



def plot_community_time_day(df, community, begin_year, end_year):
    """Determines and plots the number of crimes in the community by the time of day."""

    # filter for the number of years
    mask_years = (df['Year'] >= begin_year) & (df['Year'] < end_year)

    # filter for the community
    mask_community = (df['Community'] == community)

    # Apply the years and community masks to the the dataframe
    df = df.loc[mask_years & mask_community]

    # Order for the x_axis
    order = ['12am to 4am', '4am to 8am', '8am to 12pm', '12pm to 4pm', '4pm to 8pm', '8pm to 12am']

    # Plot the crimes by time of day
    fig = px.histogram(df, x='Time of Day', category_orders={'Time of Day': order})

    return fig



st.set_page_config(
    page_title="Neighborhood Watch Statistics",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")

start_init_1 = pd.to_datetime(start_init)
end_init_1 = pd.to_datetime(end_init)


# Add a sidebar
with st.sidebar:
    st.title('Neighborhodd Input')
    begin_date = st.date_input('Begin Date', start_init_1)
    ending_date = st.date_input('End Date', end_init_1)
    community = st.selectbox('Select Community', options=df_communities['Community'].unique())



# Convert the datetime back to a string
begin_date_1 = begin_date.strftime('%Y-%m-%d')
ending_date_1 = ending_date.strftime('%Y-%m-%d')

data_load_state = st.text('Loading data...')
new_df = clean_robberies(df_crime_1, df_communities, crime, begin_date_1, ending_date_1)
data_load_state.text("Data loaded!")

st.write(new_df)
st.subheader('Crime by Time of Day')


# Extract the year
begin_year_int = begin_date.year
end_year_int = ending_date.year

time_of_day_plot = plot_community_time_day(new_df, community, begin_year_int, end_year_int)

# Initialize variables to hold selected begin and end years
#begin_year_value = None
#end_year_value = None
# Button to trigger the update
#update_button = st.button("Update Years")


#if update_button:
#community = st.selectbox('Select Community', options=new_df['Community'].unique())
#begin_year_value = st.number_input('Begin Year', min_value=int(new_df['year'].min()), value=int(new_df['year'].min()), step=1)
#end_year_value = st.number_input('End Year', min_value=begin_year_value, value=int(new_df['year'].max()), step=1)

# Display selected or default values
st.write(f"Begin Year: {begin_year_int if begin_year_int else int(new_df['year'].min())}")
st.write(f"End Year: {end_year_int if end_year_int else int(new_df['year'].max())}")

if st.button('Plot'):

    fig = plot_community_time_day(new_df, community, begin_year_int, end_year_int)
    st.plotly_chart(fig)




