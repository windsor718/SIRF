import assim_cama
import datetime

sdate = datetime.datetime(1984,5,8)
edate = datetime.datetime(1985,1,10)

handler = assim_cama.AssimCama()
handler.register("./config.json", initialize=True, use_cached_lp=True)
handler.start(sdate, edate, spinup=False)
#handler.const_statevector(3)
