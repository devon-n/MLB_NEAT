# Import libraries
import pandas as pd
from datetime import datetime
import pytz
import os

# Keras imports
import tensorflow as tf
# physical_devices = tf.config.list_physical_devices('GPU') 
# tf.config.experimental.set_memory_growth(physical_devices[0], True)
import numpy as np
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense

# Loading model
from keras.models import load_model

# Preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer
imputer = SimpleImputer()
MMS = MinMaxScaler()


# Path
dir_path = os.path.dirname(os.path.realpath(__file__))
model = load_model(dir_path + '/Model.h5')

# Today and yesterday date EST
tz = pytz.timezone('America/New_York')
today = datetime.now(tz)
year = today.year

def clean_games():
    # Get future games
    games = pd.read_csv(dir_path + '/auto_files/future_games.csv')

    # Read stats and only keep necessary columns
    stats = pd.read_csv(dir_path + '/MLB All Stats.csv')

    # Find a year's columns
    cols = stats.columns
    str_cols = [str(col) for col in cols]
    sum('2021' in s for s in str_cols)
    remove_dupes = [i[5:] for i in str_cols]
    one_year_cols = []
    [one_year_cols.append(x) for x in remove_dupes if x not in one_year_cols]
    one_year_cols.pop(0)
    final_cols = [str(year) + ' ' + i for i in one_year_cols]
    final_cols.insert(0, 'Tm')

    stats = pd.read_csv(dir_path + '/MLB All Stats.csv', usecols=final_cols)

    # Make home and away stat dfs
    home_stats = stats.add_prefix('H ')
    vis_stats = stats.add_prefix('V ')

    # Rename Team column
    home_stats.rename(columns={'H Tm': 'Home'}, inplace=True)
    vis_stats.rename(columns={'V Tm': 'Visitor'}, inplace=True)

    # Merge Stats and games
    merged = games.merge(home_stats, on='Home')
    merged = merged.merge(vis_stats, on='Visitor')
    x = merged.loc[:,'H 2021 #Bat':]
    return x, games



# Get previous data so we can fit_transform on it then transform on predictions x

# Split columns with hyphens
def fit_transform(x, y):
    
    x = x.astype(str)
    cols_to_delim = []
    for col in x.columns:
        result = x[col].str.contains(pat='\d-\d')
        if result.any():
            cols_to_delim.append(col)

    for col in cols_to_delim:
            x[[col + '1', col + '2']] = x[col].str.split('-', expand=True)
            del x[col]

    x = x.astype(float)
    
    # Scale and Normalise
    x = imputer.fit_transform(x, y)
    x = MMS.fit_transform(x)
    return x


# Transform predictive columns
def transform(x):
    
    x = x.astype(str)
    cols_to_delim = []
    for col in x.columns:
        result = x[col].str.contains(pat='\d-\d')
        if result.any():
            cols_to_delim.append(col)

    for col in cols_to_delim:
            x[[col + '1', col + '2']] = x[col].str.split('-', expand=True)
            del x[col]

    x = x.astype(float)
    
    # Scale and Normalise
    x = imputer.transform(x)
    x = MMS.transform(x)
    return x


def transform_all_data(x):
    data_current = pd.read_csv(dir_path + '/Current Stats and Games.csv', parse_dates=['Date'])
    y = data_current['Home Win']
    x_current = data_current.loc[:,'H  #Bat':]
    x_current = fit_transform(x_current, y)
    x_trans = transform(x)
    return x_trans


def predict_and_save(x, games):
    preds = model.predict(x)
    games['Predictions'] = preds
    NE_input = games[['Time', 'Date', 'Home', 'Visitor', 'Home Odds', 'Vis Odds', 'Predictions']]
    NE_input.to_csv(dir_path + '/auto_files/ne_input.csv', index=False)




#### RUN FUNCTIONS
# x, games = clean_games()
# x = transform_all_data(x)
# predict_and_save(x, games)
