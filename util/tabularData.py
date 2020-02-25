import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker


m3_to_acrefeet = 0.000810714
dtSeconds = 3600

def returnQmodOnly(dbcon, **kwargs):
    # only use this when there is just one iteration 
    mod_cmd = "SELECT * FROM MODOUT"
    mod = pd.read_sql(sql = mod_cmd, con="sqlite:///{}".format(dbcon))
    mod['time'] = pd.to_datetime(mod['time']) 
    mod['type'] = 'WRF_Hydro V5'
    return mod 

def returnObsOnly(dbcon, **kwargs):
    obs = pd.read_sql(sql="SELECT * FROM OBSERVATIONS", con="sqlite:///{}".format(dbcon))
    obs.rename(columns={"site_name_long":"site"}, inplace=True)
    obs['time'] = pd.to_datetime(obs['time'])
    obs.set_index('time', inplace=True) 
    idx = pd.date_range(obs.index[0], obs.index[-1])
    
    # check if there are missing times from the observations ...
    if len(idx) != len(obs.index):
        missing_list = [str(i) for i in idx if i not in obs.index]
        message = 'observations are missing the following dates: {}'.format(missing_list)    
        print(message)
    
    # reindex and interpolate
    obs = obs.reindex(idx)
    obs_interpolate = obs.interpolate()
    obs_interpolate['time'] = idx
    # remove the very last entry 
    return obs_interpolate[:-1]


def returnQmodCalib(dbcon, **kwargs):
    mod_cmd = "SELECT * FROM MODOUT"
    mod = pd.read_sql(sql = mod_cmd, con="sqlite:///{}".format(dbcon))
    # 
    calib_cmd = "SELECT * FROM CALIBRATION"
    calib = pd.read_sql(sql = calib_cmd, con="sqlite:///{}".format(dbcon))
    #
    obs = pd.read_sql(sql="SELECT * FROM OBSERVATIONS", con="sqlite:///{}".format(dbcon))
    obs['time'] = pd.to_datetime(obs['time'])
    obs.drop(columns=['site_no'], inplace=True)

    #df.drop(columns=["Directory", "Iterations"], inplace=True)
    mod['time'] = pd.to_datetime(mod['time'])
    df_cd = pd.merge(calib, mod, how='outer', left_on = 'Iteration', right_on = 'Iterations')
    df_cd['time'] = pd.to_datetime(df_cd['time'])
    return df_cd 


def integrateQ(array):
    #return np.mean(array)*3600*24*365*m3_to_acrefeet
    AcreFeet = array*3600*24*m3_to_acrefeet
    return np.cumsum(AcreFeet).values



#df_cd = returnQmodCalib("CALIBRATION.db")
obs = returnObsOnly("BASELINE_WY2014.db")
preduce = returnQmodOnly("PREDUCE_WY2014.db")
baseline = returnQmodOnly("BASELINE_WY2014.db")


df = pd.DataFrame(data = {'WRF-HydroV5:PREDUCE':integrateQ(preduce['qMod']),
                          'WRF-HydroV5:Baseline':integrateQ(baseline['qMod']), 
                         'USGS SiteNo 13185000':integrateQ(obs['qObs'])
                         }
                 )

df = df.set_index(obs.index)

#df.to_csv('MF_BoiseTwinSprings_13185000-WY2014.csv')
#df['stat'] = 'total_runoff_acrefeet'
#df.set_index('stat', inplace=True)

