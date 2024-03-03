from datetime import datetime
import pandas as pd
from utils.globals import SI_MAX, SI_MIN, SP_MAX, SP_MIN

def kmh_to_knots(kmh):
    return kmh * 0.539957

def get_category(wind_speed_kn):
    """
    get a cyclone's current SAFFIR SIMPSON classified category based on its wind speed in knots
    """
    if wind_speed_kn < kmh_to_knots(125):
        return 1
    if wind_speed_kn < kmh_to_knots(164):
        return 2
    if wind_speed_kn < kmh_to_knots(224):
        return 3
    if wind_speed_kn < kmh_to_knots(279):
        return 4
    
    return 5


def lat_long_string_to_float(s):
    """
    use this to turn strings such as 118S to -11.8
    """
    num = s.rstrip('NWES')
    tail = s[len(num):]

    if tail == 'S' or tail == 'W':
        return -float(num)/10
    return float(num)/10

def time_to_season(dt: datetime):
    """
    convert python datetime object to a string denoting the current cyclone season
    with a season going from july to june
    e.g. {year: 1998, month: 7, day: 3} -> '1998-1999'
         {year: 1998, month: 6, day: 3} -> '1997-1998'
    """
    if dt.month <= 6:
        return f'{dt.year - 1}-{dt.year}'
    return f'{dt.year}-{dt.year + 1}'

def get_datetime(timestamp):
    return datetime.fromisoformat(timestamp)

def get_cyclone_data(basin=None, min_cat=None, one_per_id=False):
    """
    Perform some standard preprocessing on the Cyclone dataset, returning additional columns 
    with a cyclone's peak wind, category, and season
    """
    cyclones_df = pd.read_csv('../cyclone_data/with_ids_full.csv')
    cyclones_df['longitude'] = cyclones_df.loc[:,'Lon'].apply(lat_long_string_to_float)
    cyclones_df['longitude'] = cyclones_df.loc[:, 'longitude'].apply(lambda x: x if x > 0 else 360 + x)
    cyclones_df['latitude'] = cyclones_df.loc[:, 'Lat'].apply(lat_long_string_to_float)
    cyclones_df['peak_wind'] = cyclones_df.groupby('id')['Speed(knots)'].transform('max')
    cyclones_df['category'] = cyclones_df['peak_wind'].apply(get_category)
    cyclones_df.loc[:,'season'] = cyclones_df.loc[:, 'Time'].apply(lambda x: time_to_season((datetime.strptime(x, '%Y-%m-%d %X'))))
    cyclones_df.loc[:, 'basin'] = cyclones_df.loc[:, 'longitude'].apply(lambda x: 'SP' if (x > SP_MIN) else 'SI')

    relevant_df = cyclones_df.loc[:,["id", "Time", "latitude", "longitude", "basin", "Speed(knots)", "category", "peak_wind",  "season"]]

    if one_per_id:
        relevant_df = relevant_df.drop_duplicates(subset='id')


    if basin is not None:
        if basin == 'SI':
            relevant_df = relevant_df.loc[(relevant_df.loc[:, 'longitude'] > SI_MIN) & (relevant_df.loc[:, 'longitude'] < SI_MAX)]
        elif basin == 'SP':
            relevant_df = relevant_df.loc[(relevant_df.loc[:, 'longitude'] > SP_MIN) & (relevant_df.loc[:, 'longitude'] < SP_MAX)]
    
    if min_cat is not None:
        relevant_df = relevant_df.loc[relevant_df.loc[:, 'category'] >= min_cat]

    return relevant_df