for i in `seq 0 19`; do
    if [ $i -lt 10 ]; then
        i=0$i
    fi
    cp ../../model/CaMa-Flood_v395b_20191030/out/MS-RiDiA-promptShort/${i}/restart1984051100.bin ../../model/CaMa-Flood_v395b_20191030/out/MS-RiDiA-promptShort/${i}/restart.bin
done
