#!/bin/bash

source ~/.bashrc
cd $LSB_JOB_CWD
conda activate ridia
python -u /home/yi79a/yuta/RiDiA/srcda/MS-RiDiA/go_long.py
