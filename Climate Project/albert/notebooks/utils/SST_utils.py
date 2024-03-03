import xarray as xr
import numpy as np
from datetime import datetime

from netCDF4 import Dataset
# get cyclone dataset
from utils.globals import SP_MAX, SP_MIN, SI_MAX, SI_MIN

def get_historical_ssts(basin=None):
    monthly_avg_ssts = xr.open_dataset('../SST_data/Historical/sst.mon.mean.nc', engine='netcdf4')
    if basin == 'SP':
        return monthly_avg_ssts.sel(lon=slice(SP_MIN, SP_MAX))
    elif basin == 'SI':
        return monthly_avg_ssts.sel(lon=slice(SI_MIN, SI_MAX))
    return monthly_avg_ssts

def get_cmip_prediction(forcing_num):
      monthly_avg_ssts = xr.open_dataset(f'../SST_data/CMIP/CMIP_ssp{forcing_num}_Omon_tos-mean.nc', engine='netcdf4')
      return monthly_avg_ssts['tos_mean_mean'].rename({'latitude': 'lat', 'longitude': 'lon'})

def get_cmip_historical():
    monthly_avg_ssts = xr.open_dataset('../SST_data/CMIP/CMIP_historical_Omon_tos-mean.nc', engine='netcdf4')
    return monthly_avg_ssts['tos_mean_mean'].rename({'latitude': 'lat', 'longitude': 'lon'})

def get_tropical_avg(sst_xarray):
     """ Takes a whole xarray dataset """
     return sst_xarray.sel(lat=slice(-20,20)).mean(dim=['lon', 'lat'])

def sel_mm_yyyyy(sst_xarray, mm, yyyy):
    """ Takes a single_variable x-array, returns boolean array that you can use in .sel()"""
    return ((sst_xarray.time.dt.year == yyyy) & (sst_xarray.time.dt.month == mm))

# def get_local_smooth_month_avg(sst_xarray, lat, lon, month, grid_size = 10):
#     res = sst_xarray.sel(
#         lat=slice(lat - grid_size/2, lat + grid_size/2), 
#         lon=slice(lon - grid_size/2, lon + grid_size/2),
#         time=(sst_xarray.time.dt.month == month) ## for efficiency, this is equivalent???
#         ).mean().values

#     return res

def get_local_mean(sst_xarray, lat, lon, time, grid_size = 5):
    """ Takes a single-variable xarray """
    dt_obj = datetime.strptime(time, '%Y-%m-%d %X')
    month = dt_obj.month

    match = sst_xarray.sel(
        lat=slice(lat - grid_size/2, lat + grid_size/2), 
        lon=slice(lon - grid_size/2, lon + grid_size/2),
        time=sst_xarray.time.dt.month == month)

    try:
        return match.mean() 
    except Exception:
        return np.nan




def get_local_smooth_at_time(sst_xarray, lat, lon, time, grid_size = 5):
    """ Takes a single-variable xarray """
    dt_obj = datetime.strptime(time, '%Y-%m-%d %X')
    month = dt_obj.month
    year = dt_obj.year
    res = sst_xarray.sel(
        lat=slice(lat - grid_size/2, lat + grid_size/2), 
        lon=slice(lon - grid_size/2, lon + grid_size/2),
        time = sel_mm_yyyyy(sst_xarray, month, year)).mean(dim=['lon', 'lat']).values
    
    if (len(res) > 0):
        return res[0]
    return np.nan


## COMPUTE ANOMALY AS VECTOR
# def get_local_anomaly_at_time(sst_xarray, lat, lon, time, grid_size = 5):
#     dt_obj = datetime.strptime(time, '%Y-%m-%d %X')
#     month = dt_obj.month
#     year = dt_obj.year
#     # av = sst_xarray.sel(
#     # lat=slice(lat - grid_size/2, lat + grid_size/2), 
#     # lon=slice(lon - grid_size/2, lon + grid_size/2)).mean(dim=['lon', 'lat', 'time']).values 
    
#     res = sst_xarray.sel(
#     lat=slice(lat - grid_size/2, lat + grid_size/2), 
#     lon=slice(lon - grid_size/2, lon + grid_size/2),
#     time = sel_mm_yyyyy(sst_xarray, month, year)).mean(dim=['lon', 'lat']).values
    
#     if (len(res) > 0):
#         return res[0]
#     return np.nan

def get_yearly_avg(sst_xarray):
    """ Takes a single-variable xarray """
    return sst_xarray.rolling(time=12).mean().dropna(dim='time')


