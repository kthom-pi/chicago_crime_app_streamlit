
import pandas as pd
import numpy as np
import plotly.express as px

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
    crime_df_1 = crime_df.merge(neighborhoods, how='right', on='Community Area')

    # Change the column name for the demographics from GEOG to 'Community'.
    demographics = demographics.rename(columns={'GEOG':'Community'})

    # Add the demographics dataframe
    crime_df_2 = crime_df_1.merge(demographics, how='left', on='Community')

    return crime_df_2


def plot_community_time_day(df_crimetype, community, begin_year, end_year):
    """Determines and plots the number of crimes in the community by the time of day."""

    # filter for the number of years
    mask_years = (df_crimetype['Year'] >= begin_year) & (df_crimetype['Year'] < end_year)

    # filter for the community
    mask_community = (df_crimetype['Community'] == community)

    # Apply the years and community masks to the the dataframe
    df_crimetype = df_crimetype.loc[mask_years & mask_community]

    # Order for the x_axis
    order = ['12am to 4am', '4am to 8am', '8am to 12pm', '12pm to 4pm', '4pm to 8pm', '8pm to 12am']

    # Plot the crimes by time of day
    fig = px.histogram(df_crimetype, x='Time of Day', category_orders={'Time of Day': order})
    fig.show()

    return




# Import the data files.
# Crime database
df_crime = pd.read_csv("C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\Crimes_-_2001_to_Present.csv")
# Demographics database
df_demographics = pd.read_csv("C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\Community_Data_Snapshots_2023_-7949553649742586148.csv")
# Communities database
df_communities = pd.read_csv("C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\communities.csv")

crime = "ROBBERY"

new_df = clean_robberies(df_crime, df_demographics, df_communities, crime)

starting_year = 2023
ending_year = 2024
chicago_community = 'The Loop'

community_df = plot_community_time_day(new_df, chicago_community, starting_year, ending_year)