import pandas as pd

# Set default start date for graph
START_DATE_DEFAULT = pd.to_datetime('08/01/2024')

# Read community data from Google Cloud Storage
community_df = pd.read_csv('gs://home_values/stt_values.csv', parse_dates=['date'])

#TODO: Convert to Zillow API call
# Read in dummy data
zillow_df = pd.read_csv('gs://home_values/dummyData.csv', parse_dates=['date'])

# Combine community and zillow data
combined_df = pd.merge(community_df, zillow_df, on='date', how='left')

# Index all columns except 'date' to their value on 8/1/2021 (vectorized)
base_date = pd.to_datetime('08/01/2021')
cols_to_index = [col for col in combined_df.columns if col != 'date']

# Get the base values as a Series (index is column names)
base_values = combined_df.loc[combined_df['date'] == base_date, cols_to_index].iloc[0]

# Perform vectorized calculation and assign new columns
combined_df[[f"{col}_indexed" for col in cols_to_index]] = (
    (combined_df[cols_to_index] / base_values) * 100
).round(1)