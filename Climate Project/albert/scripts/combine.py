import pandas as pd
from datetime import datetime

def get_cyclone_season_as_string(dt: datetime):
    """
    couple weird outliers here where a cyclone 'overflows' into the next season
    """
    if (dt.month <= 6):
        print(f'{dt.year - 1}-{dt.year}')
        return f'{dt.year - 1}-{dt.year}'
    else:
        print(f'{dt.year}-{dt.year+1}')
        return f'{dt.year}-{dt.year+1}'

def are_in_same_season(dt1: datetime, dt2: datetime):
    return get_cyclone_season_as_string(dt1) == get_cyclone_season_as_string(dt2)


def assign_ids_intermediate(df: pd.DataFrame):
    # inefficient to use a loop...

    curr_id = 1
    time1 = None
    time2 = None
    prev_num_in_season = None

    new_df = df.copy(deep=True)

    # THE ALGORITHM -- go through our cyclones sequentially
    for index, row in df.iterrows():
        print(curr_id)
        
        num_in_season = row['No. of Cycl']
        
        
        # HOW DO WE KNOW THAT WE HAVE A NEW SEASON? 
        time2 = datetime.strptime(row["Time"], '%Y-%m-%d %X')
        if not time1 or not prev_num_in_season:
            new_df.loc[index, "id"] = curr_id
        elif prev_num_in_season == num_in_season and are_in_same_season(time1, time2):
            new_df.loc[index, "id"] = curr_id
        else: 
            curr_id += 1
            new_df.loc[index, "id"] = curr_id
        
        prev_num_in_season = num_in_season
        time1 = time2
    
    return new_df
        
# No. of cyclone column seems to line up so I can safely merge the dogs
si_df = pd.read_csv('./SI_with_ids.csv', index_col=False)
sp_df = pd.read_csv('./SP_with_ids.csv', index_col=False)
full_df = pd.concat([si_df, sp_df])


df_sorted = full_df.sort_values(by=["No. of Cycl", "Time"]).reset_index(drop=True)


combined = assign_ids_intermediate(df_sorted)
# combined_by_id = combined.sort_values(by=["id"])
combined_sorted = combined.sort_values(by=["Time"]).reset_index(drop=True)

def rearrange_ids(df: pd.DataFrame):
    # inefficient to use a loop...

    curr_id = 0
    old_to_new_id_map = {}
    new_df = df.copy(deep=True)

    # THE ALGORITHM -- go through our cyclones sequentially
    for index, row in df.iterrows():
        old_id = row['id']
        
        if (old_id in old_to_new_id_map):
            new_df.loc[index, "id"] = old_to_new_id_map[old_id]
        else:
            curr_id += 1
            old_to_new_id_map[old_id] = curr_id
            new_df.loc[index, "id"] = old_to_new_id_map[old_id]
            

    return new_df

rearranged = rearrange_ids(combined_sorted)

rearranged.to_csv('with_ids_full.csv', index=False)