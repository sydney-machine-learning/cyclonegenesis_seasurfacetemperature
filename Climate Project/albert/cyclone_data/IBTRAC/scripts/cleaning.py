import pandas as pd
import numpy as np

vec_int = np.vectorize(lambda x: int(x))

def get_essential_columns(df):
    cutoff_df = df.loc[2:,:]
    well_defined_df = cutoff_df.loc[(cutoff_df.loc[:, 'TRACK_TYPE'] == 'main') & (cutoff_df.loc[:, 'WMO_WIND'] != ' ') & (cutoff_df.loc[:, 'WMO_WIND'] >= '35') & (vec_int(cutoff_df.loc[:, 'SEASON']) >= 1981)]
    relevant_df = well_defined_df.loc[:, ['SID', 'SEASON', 'NUMBER', 'BASIN', 'NAME', 'ISO_TIME', 'LAT', 'LON', 'WMO_WIND', 'DIST2LAND']]
    return relevant_df

if __name__ == '__main__':
    input_filepath = input('relative file path from execution directory: ')
    desired_path = input('desired file path from execution directory: ')
    df = pd.read_csv(input_filepath)
    cleaned_df = get_essential_columns(df) 

    cleaned_df.to_csv(desired_path, index=False)

