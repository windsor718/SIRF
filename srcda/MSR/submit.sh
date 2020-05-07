rm logerr.e
rm logstd.o
bsub -W 128:00 -n 20 -q long -R span[hosts=1] -R rusage[mem=6146] -e logerr.e -o logstd.o -J cada -cwd "/project/uma_colin_gleason/yuta/RiDiA/srcda/MS-RiDiA" /project/uma_colin_gleason/yuta/RiDiA/srcda/MS-RiDiA/batch.sh
