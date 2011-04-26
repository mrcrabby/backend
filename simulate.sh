#! /usr/bin/env sh

for i in 1 2 3 4 5 6 7 8 9  
    do
    python worker.py &
    done

for i in 1 2 3 4 5
    do 
    python tracker.py &
    done
