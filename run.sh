#!/usr/bin/env bash

year=2021

source env/bin/activate

python3 py-cal.py $year 1 -b "#60d168" -a "#30bc66" &
python3 py-cal.py $year 2 -b "#f28cdd" -a "#eb57dc" &
python3 py-cal.py $year 3 -b "#e8aa76" -a "#dc8374" &
python3 py-cal.py $year 4 -b "#beda5d" -a "#9dc95b" &
python3 py-cal.py $year 5 -b "#70cbf7" -a "#37b3f7" &
python3 py-cal.py $year 6 -b "#939aed" -a "#5d6bed" &
python3 py-cal.py $year 7 -b "#c9c9c9" -a "#a1a1a1" &
python3 py-cal.py $year 8 -b "#c6a4fa" -a "#a979fa" &
python3 py-cal.py $year 9 -b "#fcdd76" -a "#facc74" &
python3 py-cal.py $year 10 -b "#98e6db" -a "#58d8da" &
python3 py-cal.py $year 11 -b "#5eddaa" -a "#24caa8" &
python3 py-cal.py $year 12 -b "#e87e93" -a "#dc4491" &

wait

echo done.
