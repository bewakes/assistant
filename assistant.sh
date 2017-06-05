#!/bin/sh
PROJECT_DIR=/home/bibek/projects/assistant/

## TRAP AND CLEANUP
cleanup() {
    echo 'cleaning up'
    for id in ${pids[@]}
    do
        kill $id
    done
    echo cleaned up
    exit 0
}

# to kill all the spawned service processes upon receiving Ctrl-C
trap 'cleanup' SIGINT
## TRAP AND CLEANUP

#############################
 ## A SHORT INTRO TO THIS ##
#############################
################################################################################
# This is the main file. This is what takes in the user commands. Each command 
#  is associated with one of the services inside services/folder. During the 
#  initialization, this will create processes for each of the services and later
#  all the communication takes place with the use of sockets
################################################################################

############################
 ## INITIALIZE VARIABLES ##
############################
prompt=">>> " # prompt for user
msg="Hi there!!" # Initial message to be displayed by the assistant

# hash table for commands -> services
declare -A service_pid_map

# list of available services
declare -a services
services=("youtube" "vlc")

# ports where the processes listen for command
declare -A ports

# process ids of the services spawned
declare -A pids

################################
## END INITIALIZING VARIABLES ##
################################


assign_ports() {
    ##########################################
    ## Assign random ports to services.
    ## Ports are stored by 'ports' variable
    ##########################################
    #local i=0
    for s in ${services[@]}
    do
        ports[$s]=$((RANDOM%2048+1025))
        #i=$(($i+1)) # increment
    done
}

initialize() {
    ###########################################
    ## This is the first function called. Here,
    ## services scripts are run by instructing
    ## them to listen on the ports assigned. 
    ## Each pid is stored in 'pids' variable.
    ###########################################

    # first assign ports
    assign_ports

    # run all the processes/services, and store each pid
    #local i=0
    for s in ${services[@]}
    do
        # make each service run and listen to the port specified
        # NOTE: the first argument will be the assigned port number to listen
        python "$PROJECT_DIR"services/$s.py ${ports[$s]} 2>/dev/null &

        pids[$s]=$! # storing corresponding pid

        # add to map/hashtable
        service_pid_map[$s]=${pids[$s]}

        #i=$(($i+1)) # increment counter
    done
}

execute_command() {
    case $1 in
        "play")
            url=''
            execute_command youtube song_url "$2"
            if [[ -n $url ]];then
                msg="Playing song '$2'"
                execute_command vlc_play audio $url & #url will be updated in youtube command
            else
                msg="NO song found"
            fi
            ;;
        "playlist")
            url=''
            execute_command youtube playlist_url "$2"
            msg="Playing Playlist.. '$2'"
            ;;
        "stop")
            msg="Stopped"
            ;;
        "youtube")
            ## get url of the song from youtube service

            ## first get processid and port number for service(youtube)
            exec 3<>/dev/tcp/localhost/${ports["youtube"]}

            ## send to socket
            echo ${@:2} >&3

            ## read data from the socket
            read -r url <&3
            ;;
        "vlc_play")
            exec 3<>/dev/tcp/localhost/${ports["vlc"]}

            ## send to socket
            echo ${@:2} >&3

            ## read data from the socket
            read -r tmp <&3
            msg="Playing"
            ;;
        "bye")
            cleanup
            exit 0
            ;;
        *)
            msg="Command not recognized"
            ;;
    esac
}

initialize

while true; do
    echo $prompt$msg
    echo -n ">> "
    read -a command_args
    cmnd=${command_args[0]}
    args=${command_args[@]:1} # getting rest of the array
    execute_command $cmnd "$args"
done
