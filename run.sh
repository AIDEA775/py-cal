#!/bin/bash

year=2019
ics=u100000354650822.ics

source env/bin/activate
python3 py-cal2.py $year 1 -c $ics -b 0ead69
python3 py-cal2.py $year 2 -c $ics -b ff206e
python3 py-cal2.py $year 3 -c $ics -b 774936
python3 py-cal2.py $year 4 -c $ics -b ff8966
python3 py-cal2.py $year 5 -c $ics -b 75AADB
python3 py-cal2.py $year 6 -c $ics -b 0a3f7a
python3 py-cal2.py $year 7 -c $ics -b 757575
python3 py-cal2.py $year 8 -c $ics -b 8338ec
python3 py-cal2.py $year 9 -c $ics -b ffbe0b
python3 py-cal2.py $year 10 -c $ics -b f6511d
python3 py-cal2.py $year 11 -c $ics -b 9bc53d
python3 py-cal2.py $year 12 -c $ics -b d62828

echo done.