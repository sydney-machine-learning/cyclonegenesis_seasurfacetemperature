import pandas as pd
from datetime import datetime

def add_cyclone_ids(df: pd.DataFrame):
    """
    Currently, data has unique ids ONLY WITHIN THE YEAR,
    which repeat year-over-year
    """

    # inefficient to use a loop...
    curr_id = 1
    year_num_to_id_map = {}

    new_df = df.copy()

    for index, row in new_df.iterrows():
        num_in_year = row['No. of Cycl']
        year = datetime.strptime(row['Time'], '%Y-%m-%d %X').year
        if (num_in_year, year) in year_num_to_id_map:
            new_df.loc[index, 'id'] = year_num_to_id_map[(num_in_year, year)]
        else:
            year_num_to_id_map[(num_in_year, year)] = curr_id
            new_df.loc[index, 'id'] = year_num_to_id_map[(num_in_year, year)]
            curr_id += 1

    return new_df
    
        

csv_path = input("Enter relative CSV Path from current directory: ")

df = pd.read_csv(csv_path, index_col=0)
df.insert(0,'id',0)

df_sorted = df.sort_values(by=['Time', 'No. of Cycl'])
new_df = add_cyclone_ids(df_sorted)
new_df.to_csv(csv_path+'_with_ids.csv', index=False)


