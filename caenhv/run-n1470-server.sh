#!/bin/sh

name=caenhv-n1470-server
server="python $HOME/software/slow-monitor/caenhv/$name.py"
session=`tmux ls | grep $name`

if [ -z "$session" ]; then
    echo "create new session $name"
    tmux new-session -d -s $name "while true; do $server; sleep 10; done"
else
    echo "reattach session $name"
    tmux a -t $name
fi
