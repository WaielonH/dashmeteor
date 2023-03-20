# Import necessary libraries
import pandas as pd
import os
    
# Read data
data = pd.read_csv('../data/raw/meteorite-landings.csv')

# Filter data to be between year 860 and 2016
clean = data[data['year'] >= 860]
clean = clean[clean['year'] <= 2016]

# Filter data to remove 0 value latitudes and longtitudes
clean = clean[clean['reclat'] != 0]
clean = clean[clean['reclong'] != 0]

# Convert year to integers
clean['year'] = clean['year'].astype(int)

# Drop NA values
clean = clean.dropna()

# Save processed dataset
try:
    clean.to_csv('../data/clean/clean_meteorite_landings.csv', index=False)
except:
    os.makedirs(os.path.dirname('../data/clean/'))
    clean.to_csv('../data/clean/clean_meteorite_landings.csv', index=False)