import pandas as pd

def get_NWP_data(one_per_id = False):
     cyclones_df = pd.read_csv('../cyclone_data/jtwc/cleaned/nwp.csv')

     nwp_df = cyclones_df.loc[cyclones_df.loc[:,'BASIN'] == 'WP']

     if one_per_id:
        nwp_df = nwp_df.drop_duplicates(subset='Storm ID')

     return nwp_df

def get_saffir_simpson_category(wind_kn):
    # NOTE: observations are rounded to nearest 5 so is this being a bit cheeky??
    if wind_kn <= 82:
        return 1
    if wind_kn <= 95:
        return 2
    if wind_kn <= 112:
        return 3
    if wind_kn <= 136:
        return 4
    return 5

def get_southern_hem_data(one_per_id = False):
     cyclones_df = pd.read_csv('../cyclone_data/jtwc/cleaned/southern_hemisphere.csv')

     if one_per_id:
        cyclones_df = cyclones_df.drop_duplicates(subset='Storm ID')

     return cyclones_df

def get_all_cyclones(one_per_id = False):
    south_df = get_southern_hem_data(one_per_id)
    nwp_df = get_NWP_data(one_per_id)
    return pd.concat([south_df, nwp_df], ignore_index=True).sort_values(by=['Season', 'SEASON TC NUMBER', 'BASIN'])