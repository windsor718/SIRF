# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd
import numpy as np
import datetime
import geopandas as gpd


# %%
effective_rivers = pd.read_csv("./good_rivers.csv")
effective_rivers


# %%
cs_all = gpd.read_file("./missouri_joined_gt120m_v01.shp")
reaches_all = cs_all["segmentInd"]
reaches_all.drop_duplicates()
cs_all

# %%
test = gpd.read_file("./intersected_validation.shp")
reaches = test["segmentInd"]
gauges = test["Gauge_no"]
reaches

# %% 
gauges


# %%
width_all = pd.read_csv("./missouri_widths_v01.csv", index_col=[0])
width_all

# %%
dates = width_all.columns.tolist()
dates = [datetime.datetime.utcfromtimestamp(float(d)/1000) for d in dates]
width_all.columns = dates
width_all

# %%
data = width_all.loc["1_91"]
data = data.replace(0, np.nan)
data.describe()
