
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import datetime


# Import the data files.
# Crime database
df_crime = pd.read_csv("C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\Crimes_-_2001_to_Present.csv")
# Demographics database
df_demographics = pd.read_csv("C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\Community_Data_Snapshots_2023_-7949553649742586148.csv")
# Communities database
df_communities = pd.read_csv("C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\communities.csv")

# Create a smaller df for testing purposes
df_crime_1 = df_crime.loc[:1000, :]

crime = "MOTOR VEHICLE THEFT"

start_date = datetime.date(2018, 1, 1)
end_date = datetime.date(2024, 1, 10)


@st.cache_data
def clean_robberies(crime_df, demographics, neighborhoods, crime_type):
    """Combines the crime, demographic and neightborhoods dataframe into one."""

    # Convert 'Date' column to date time
    crime_df['Date'] = pd.to_datetime(crime_df['Date'])

    # Filter for dates after 2018
    begin_date = '2018-01-01'

    # Apply filter to dataframe
    mask_1 = crime_df['Date'] >= begin_date
    crime_df = crime_df.loc[mask_1].sort_values(by='Date')

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

    # Change the column name for the demographics from GEOG to 'Community'.
    demographics = demographics.rename(columns={'GEOG':'Community'})

    # Add the demographics dataframe
    crime_df_2 = crime_df_1.merge(demographics, how='left', on='Community')

    return crime_df_2


st.set_page_config(
    page_title="Neighborhood Watch Statistics",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")


# Add a sidebar
with st.sidebar:
    st.title('Neighborhodd Input')
    begin_date = st.date_input('Begin Date', start_date)
    end_date = st.date_input('End Date', end_date)

data_load_state = st.text('Loading data...')
new_df = clean_robberies(df_crime_1, df_demographics, df_communities, crime)


st.write(new_df)





st.subheader('Crime by Time of Day')





