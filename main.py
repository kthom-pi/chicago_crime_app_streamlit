
import os
import pandas as pd
import numpy as np

# Import the helper python files.
import robb_clean_fn

# Import the data files.
# Crime database
df_crime = pd.read_csv("C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\Crimes_-_2001_to_Present.csv")
# Demographics database
df_demographics = pd.read_csv("C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\Community_Data_Snapshots_2023_-7949553649742586148.csv")
# Communities database
df_communities = pd.read_csv("C:\\Users\\kthom\\Desktop\\Personal Projects\\Chicago Crime Streamlit\\data_files\\communities.csv")

crime = "ROBBERY"

new_df = robb_clean_fn(df_crime, df_demographics, df_communities, crime)



