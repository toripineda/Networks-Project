#!/bin/bash

python src/peerProcess.py 1001 &
python src/peerProcess.py 1002 &
python src/peerProcess.py 1003 &
python src/peerProcess.py 1004 &
python src/peerProcess.py 1005 &

# automatically starts peers