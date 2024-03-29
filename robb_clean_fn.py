

import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date, datetime
from sodapy import Socrata

# API access
#https://dev.socrata.com/foundry/data.cityofchicago.org/ijzp-q8t2

# Use for reference:
#https://dev.socrata.com/foundry/data.cityofchicago.org/ijzp-q8t2


current_date = date.today()
# Query the date
starting_date = "2023-01-01T00:00:00.000"
ending_date = datetime.now()
end_date = ending_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
end_date_2 = f"{end_date}"
crime_type = "MOTOR VEHICLE THEFT"

client = Socrata("data.cityofchicago.org", None)
results = client.get("ijzp-q8t2",
                     select="id, case_number, block, primary_type, description, location_description, date, community_area, fbi_code,"
                            "year, latitude, longitude",
                     where=f"date > '{starting_date}' AND date < '{end_date_2}' AND primary_type = '{crime_type}'",
                     limit=250000,
                     order="date DESC")

results_df = pd.DataFrame.from_records(results)



def clean_robberies(crime_df, neighborhoods, crime_type):
    """Combines the crime, demographic and neightborhoods dataframe into one."""

    # Convert 'Date' column to date time
    crime_df['date'] = pd.to_datetime(crime_df['date'])

    # Filter for dates after 2018
    #begin_date = '2018-01-01'

    # Apply filter to dataframe
    #mask_1 = crime_df['Date'] >= begin_date
    #crime_df = crime_df.loc[mask_1].sort_values(by='Date')

    # Create columns with hour, day, month, year
    crime_df['hour'] = crime_df['date'].dt.hour
    crime_df['day'] = crime_df['date'].dt.day
    crime_df['month'] = crime_df['date'].dt.month
    crime_df['year'] = crime_df['date'].dt.year

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
    crime_df = crime_df.loc[crime_df['primary_type'] == crime_type]

    # Rename the column Community in the Commnities dataframe
    neighborhoods = neighborhoods.rename(columns={"Community Area": "community_area"})

    # Make the community_area a string in neightborhoods.
    neighborhoods['community_area'] = neighborhoods['community_area'].astype(str)

    # Add the communities to the dataframe.
    crime_df_1 = pd.merge(crime_df, neighborhoods, on='community_area', how='outer')


    # Filter for the crimes of interest.
    keep_crimes = ['THEFT', 'ASSAULT', 'SEX OFFENSE', 'BURGLARY', 'CRIM SEXUAL ASSAULT',
                   'MOTOR VEHICLE THEFT', 'OFFENSE INVOLVING CHILDREN', 'CRIMINAL TRESPASS',
                   'ROBBERY', 'CRIMINAL SEXUAL ASSAULT', 'STALKING', 'HOMICIDE', 'KIDNAPPING',
                   'DOMESTIC VIOLENCE']

    crime_df_1 = crime_df_1[crime_df_1['primary_type'].isin(keep_crimes)]

    return crime_df_1


def plot_community_time_day(df_crimetype, community, begin_year, end_year):
    """Determines and plots the number of crimes in the community by the time of day."""

    # filter for the number of years
    mask_years = (df_crimetype['year'] >= begin_year) & (df_crimetype['year'] < end_year)

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


def location_description(df_crimetype, community, begin_year, end_year):
    """Plots a pie chart of the different locations"""

    # filter for the number of years
    mask_years = (df_crimetype['year'] >= begin_year) & (df_crimetype['year'] < end_year)

    # filter for the community
    mask_community = (df_crimetype['Community'] == community)

    # Apply the years and community masks to the the dataframe
    df_crimetype = df_crimetype.loc[mask_years & mask_community]

    value_counts = df_crimetype['location_description'].value_counts()

    # Plot the crimes by time of day
    fig = px.pie(df_crimetype, values=value_counts.values, names=value_counts.index)
    fig.show()

    return


# Import the data files.
# Crime database
#df_crime = pd.read_csv("C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\Crimes_-_2001_to_Present.csv")
# Demographics database
#df_demographics = pd.read_csv("C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\Community_Data_Snapshots_2023_-7949553649742586148.csv")
# Communities database
df_communities = pd.read_csv("C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\communities.csv")


new_df = clean_robberies(results_df, df_communities, crime_type)

starting_year = 2023
ending_year = 2024
chicago_community = 'The Loop'

community_df = plot_community_time_day(new_df, chicago_community, starting_year, ending_year)

location_df = location_description(new_df, chicago_community, starting_year, ending_year)
