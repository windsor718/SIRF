# Model directory  
We used [CaMa-Flood-v395b](http://hydro.iis.u-tokyo.ac.jp/~yamadai/cama-flood/) for our model.  

## Availability note  
As CaMa-Flood needs a registration to use, the source code is not published on GitHub. For internal use, the modified (implemented time-variant width) version of CaMa-Flood is placed in [the private repository](https://github.com/windsor718/SIRD_CaMa-Flood). Please contact me for this version of source code.  
  
## Setup your map  
After you created your map at your interested domain (via src_region/ code sets if you want to run regionally), run following commands:  
move to src_param directory:  
```bash  
cd ${your_CaMa_dir}/map/${your_map_dir}/src_param
```  
compile codesets:  
```bash  
make clean  
make all  
```  
create inpmat (interpolation matrix) for your input runoff and domain:  
```bash  
vi s02-generate_inpmat.sh  # edit for your domain and input runoff  
sh s02-generate_inpmat.sh  
```  
create rivwth and rivhgt, and other related files:  
```bash  
vi s01-channel_params.sh  # specify your diminfo.txt you just created via s02-generate_inpmat.sh  
sh s01-channel_params.sh  
```  
go back to the parent directory, and run following python code to get river-shape parameter file (You will need a class reference csv for width and shape parameter).:  
```bash  
cd ../
vi getParamViaClass.py  # edit for your domain  
python getParamViaClass.py  
```  
via the same code, you may get Manning's n by replacing the csv from river shape parameter to Manning's n as well.  
Finally get rivbta (parameters to get wetted-pelimeter) by running:  
```bash  
cd ./src_param/  
calc_rivbta ${path_to_your_diminfo}  
```  
