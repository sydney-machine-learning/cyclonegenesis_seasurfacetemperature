import pandas as pd
import numpy as np
from datetime import datetime

from common import SI_MIN, SI_MAX, SP_MIN, SP_MAX

## DATA CLEANING TODO LIST:
# - best tracks only
# - filter out weak storms
# - only take quality controlled data
# - convert tenths of a degree to numeric degrees?
# - generate unique id's (can only do this per basin, sometimes cross basins so don't want to double-count)
# - return relevant columns only:
# - BASIN, ID, TIME (to iso?), lat, lon, vmax, name

int_vec = np.vectorize(int)

def shift_array(arr, num, fill_value=np.nan):
    if num >= 0:
        return np.concatenate((np.full(num, fill_value), arr[:-num]))
    else:
        return np.concatenate((arr[-num:], np.full(-num, fill_value)))
    
def get_max_24h_intensification(col: pd.Series):
    ## ONLY GET INTENSIFICATION VALUES HERE AND LET USER DETERMINE RI THRESHOLD
    WINDOW_SIZE = 4 ## 4 observations in 24 hours
    curr_max = None
    for shift_num in range(1, min(WINDOW_SIZE, len(col))):
        shifted = shift_array(col, shift_num)
        diff = (col - shifted).dropna()
        curr_max = max(diff)
    return curr_max


def max_timegap(col : pd.Series):
    # shift and check difference in hours
    shifted = shift_array(col, 1, fill_value=pd.NaT)
    diff = (col - shifted).dropna()

    if len(diff) > 0:
        to_seconds = np.vectorize(lambda x: pd.Timedelta(x).total_seconds())
        diff_seconds = to_seconds(diff)
        return max(diff_seconds)/(60*60)
    
    return 0


def get_lat_lon_float(coordinate_str: str):
    if not isinstance(coordinate_str, str):
        return 'NOT A STRING??'
    num = float(coordinate_str[:-1])/10
    letter = coordinate_str[-1]
    if letter == 'S':
        return -num
    if letter == 'W':
        return 360 - num
    return num
    

def clean_df(input_path, output_path, is_southern_hemisphere=False):
    df = pd.read_csv(input_path)

    df = df.dropna(subset=['VMAX (kt)'])
    # get post-satellite data. some cyclones also have junk numbers in their VMAX observations
    df = df.loc[(df.loc[:,'Season'] >= 1982) & (df.loc[:, 'VMAX (kt)'] >= 10) & (df.loc[:, 'VMAX (kt)'] <= 200)]
    df = df.loc[:, ['BASIN', 'Season', 'SEASON TC NUMBER', 'TIME (YYYYMMMDDHH)', 'LAT (1/10 degrees)', 'LON (1/10 degrees)', 'VMAX (kt)', 'MSLP (MB)', 'TY' , 'TECH']]
    df['SEASON TC NUMBER'] = df['SEASON TC NUMBER'].apply(int)
    # convert degrees
    df['Latitude (degrees)'] = df['LAT (1/10 degrees)'].apply(lambda x: get_lat_lon_float(x))
    df['Longitude (degrees)'] = df['LON (1/10 degrees)'].apply(lambda x: get_lat_lon_float(x))

    # more specific southern hemisphere basin
    if is_southern_hemisphere:
        df.loc[(df.loc[:,'Longitude (degrees)'] >= SI_MIN) & (df.loc[:,'Longitude (degrees)'] < SI_MAX), 'BASIN'] ='SI'
        # df.loc[(df.loc[:,'Longitude (degrees)'] >= AUS_MIN) & (df.loc[:,'Longitude (degrees)'] < AUS_MAX), 'BASIN'] ='AUS'
        df.loc[(df.loc[:,'Longitude (degrees)'] >= SP_MIN) & (df.loc[:,'Longitude (degrees)'] < SP_MAX), 'BASIN'] = 'SP'

    # DATA CONTAINS SOME 3HOUR OBSERVATIONS, only take 00:00, 06:00, 12:00, 18:00
    df['Hour'] = df['TIME (YYYYMMMDDHH)'].apply(lambda x: datetime.strptime(str(x), "%Y%m%d%H").hour)
    df = df.loc[np.remainder(df.loc[:, 'Hour'], 6) == 0]

    df['Longitude (degrees)'] = df['LON (1/10 degrees)'].apply(lambda x: get_lat_lon_float(x))
    df['Time'] = df['TIME (YYYYMMMDDHH)'].apply(lambda x: datetime.strftime(datetime.strptime(str(x),"%Y%m%d%H"), '%Y-%m-%d %X'))
    df['timestamp'] = pd.to_datetime(df['Time'])
    
    if is_southern_hemisphere:
        set_str = 'S'
    else:
        set_str = 'N'

    # get unique ID's
    df['Storm ID'] = df.apply(lambda row: str(row['Season']) + '-' + set_str + '-' + str(row['SEASON TC NUMBER']), axis=1)

    ## DROP DUPLICATE OBSERVATIONS (TIME AND STORM)
    df = df.drop_duplicates(subset=['Storm ID', 'Time'])


    # Northern Hemisphere 1985 storm 16 is pathological.... WHY IS THE DATA SO BAD????
    df = df.loc[df.loc[:, 'Storm ID'] != '1983-N-16']


    ## INTERPOLATE DATA FOR MISSING HOURS...
    df = df.set_index('timestamp').groupby('Storm ID').resample('6H').interpolate().fillna(method='ffill').drop('Storm ID', axis=1).reset_index()

    # print(f'number of TCs with gaps in observations: {with_gaps.shape[0]}')
    # df = df.loc[df.loc[:, 'max_timegap'] == 6]
    
    # print(with_gaps.drop_duplicates(subset=['Storm ID']).shape[0])
    # get a storm's peak wind

    df['Peak VMAX (kt)'] = df.groupby('Storm ID')['VMAX (kt)'].transform('max')

    grouped_ssq = df.groupby(by="Storm ID")['VMAX (kt)'].agg(lambda x: sum(x**2)/100000)
    df = df.join(grouped_ssq, on='Storm ID', rsuffix="_ssq") 
    df = df.rename(columns={'VMAX (kt)_ssq': 'ACE'})

    df['Maximum 24h Intensification'] = df.groupby(by='Storm ID')['VMAX (kt)'].transform(get_max_24h_intensification) 
    # one_per_id_with_ri = all_cyclone_datapoints.drop_duplicates(subset='Storm ID')
    df = df.loc[df.loc[:,'Peak VMAX (kt)'] >= 40]
    df = df.sort_values(by=['Season', 'SEASON TC NUMBER', 'timestamp'])
    df = df.loc[:, ['timestamp', 'Storm ID', 'BASIN', 'Season', 'SEASON TC NUMBER', 'Latitude (degrees)', 'Longitude (degrees)', 'VMAX (kt)', 'Peak VMAX (kt)', 'ACE', 'Maximum 24h Intensification']]
    
    print('time:')
    print(f'min: {df["timestamp"].min()}')
    print(f'max: {df["timestamp"].max()}')

    print('latitude:')
    print(f'min: {df["Latitude (degrees)"].min()}')
    print(f'max: {df["Latitude (degrees)"].max()}')

    print('longitude')
    print(f'min: {df["Longitude (degrees)"].min()}')
    print(f'max: {df["Longitude (degrees)"].max()}')

    print('vmax:')
    print(f'min: {df["VMAX (kt)"].min()}')
    print(f'max: {df["VMAX (kt)"].max()}')

  

    df.to_csv(output_path, index=False)


    
if __name__ == '__main__':
    # e.g. NWP_PATH = 'cyclone_data/jtwc/NWP'
    input_path = input('Enter path of concatenated cluttered file relative to ./albert/ folder: ')
    output_path = input('Enter path where you would like output .csv to be placed (including filename): ')
    is_southern_str = input('Is southern hemisphere? T/F: ')
    is_southern = is_southern_str == 'T'

    clean_df(input_path, output_path, is_southern)