# %%
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

data = np.fromfile("../missouri_03min/uparea.bin", dtype=np.float32).reshape(276, 466)
lonlat = np.fromfile("../missouri_03min/lonlat.bin", dtype=np.float32).reshape(2, 276, 466)
mask = np.fromfile("../missouri_03min/basin.bin", dtype=np.int32).reshape(276, 466)
p80 = np.percentile(data, 80)
p60 = np.percentile(data, 60)
p40 = np.percentile(data, 40)
# %%
plt.close()
lonlat[0][mask!=1] = np.nan
lonlat[1][mask!=1] = np.nan
plt.figure(figsize=(12, 8))
nr = data/data.max()
sr = nr*12*8/3
sr[sr<0.5] = 0.5
plt.scatter(lonlat[0][data>p40], lonlat[1][data>p40], s=sr[data>p40], color="k")
satellites_lonlat = np.fromfile("./camapoints.bin", np.float32).reshape(3, -1)
slon_g = satellites_lonlat[0][satellites_lonlat[2]<1].tolist()
slat_g = satellites_lonlat[1][satellites_lonlat[2]<1].tolist()
slon_d = [lonlat[0, int(slat_g[i]), int(slon_g[i])] for i in range(len(slon_g))]
slat_d = [lonlat[1, int(slat_g[i]), int(slon_g[i])] for i in range(len(slon_g))]
plt.scatter(slon_d, slat_d, s=10, color="orange")
