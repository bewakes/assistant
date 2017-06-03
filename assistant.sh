#!/bin/sh

#initial pid of player is nothing
curr_player_pid=-1

prompt=">>> "
msg="Welcome!!"

# hash table for commands -> services
declare -A command_service_map=( ['play']='youtube')
declare -A service_pid_map

services=("youtube")
# ports where the processes listen for command
ports=
pids=

initialize_ports() {
    local i=0
    for s in $services
    do
        ports[$i]=$((RANDOM%2048+1025))
        i=$(($i+1)) # increment
    done
}

initialize() {
    # first initialize ports
    initialize_ports

    # run all the processes/services, like youtube/player
    local i=0
    for s in $services
    do
        # make each service run and listen to the port specified
        python services/$s.py ${ports[$i]} &

        pids[$i]=$!

        # add to map/hashtable
        service_pid_map[$s]=${pids[$i]}

        i=$(($i+1)) # increment
    done
    echo ${pids[0]}
}

execute_command() {
    case $1 in
        "play")
            #kill $curr_player_pid
            echo $2
            python services/youtube.py $2 >/dev/null 2>/dev/null
            curr_player_pid=$!
            echo $curr_player_pid
            #echo curr pid $curr_player_pid
            msg="Playing.."
            ;;
        "stop")
            echo stop
            echo curr pid $curr_player_pid ..
            kill $curr_player_pid
            msg="Stopped"
            ;;
        *)
            msg="Command not recognized"
            ;;
    esac
}

#initialize

while true; do
    echo $prompt$msg
    echo -n ">> "
    read -a command_args
    cmnd=${command_args[0]}
    args=${command_args[@]:1} # getting rest of the array
    execute_command $cmnd "$args"
done
