import numpy as np
import glob

files = glob.glob("./vic/*")
for fname in files:
    data = np.fromfile(fname, dtype=np.float32)
    masked_data = np.where(data==data.max(), 0, data)
    masked_data.flatten().astype(np.float32).tofile(fname)
