#!/bin/bash
source "$ASSISTANT_DIR"helpers.sh

## TRAP AND CLEANUP
cleanup() {
    echo 'cleaning up'
    # Now kill each services, which keep track of children themselves
    # each will kill itself and its children with SIGTERM signal
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
# looks into services dir. ommits modules starting with _
declare -a services
services=$(ls "$ASSISTANT_DIR"services | grep -v "^_" | sed 's/.py//')

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
    for s in ${services[@]}
    do
        ports[$s]=$((RANDOM%2048+4213)) # 4213 because vlc uses 4212. TODO: retry if already used port
    done
}

initialize() {
    ###########################################
    ## This is the first function called. Here,
    ## services scripts are run by instructing
    ## them to listen on the ports assigned. 
    ## Each pid is stored in 'pids' variable.
    ###########################################

    # to store data
    mkdir -p $HOME/.assistant/
    if [[ ! -f $HOME/.assistant/songs ]]; then
        echo songs file not found
        touch $HOME/.assistant/songs
    fi
    # store music here
    mkdir -p $HOME/Music/assistant/

    # first assign ports
    assign_ports

    # run all the processes/services, and store each pid
    for s in ${services[@]}
    do
        # make each service run and listen to the port specified
        # NOTE: the first argument will be the assigned port number to listen
        python3 "$ASSISTANT_DIR"services/$s.py ${ports[$s]} 2>/dev/null &

        pids[$s]=$! # storing corresponding pid

        # add to map/hashtable
        service_pid_map[$s]=${pids[$s]}
    done
}

execute_command() {
    case $1 in
        "pause")
            execute_command vlc $@
            #echo -e "test\npause\nquit" | nc localhost 4212
            ;;
        "play")
            execute_command vlc $@
            ;;
        "playlist")
            execute_command vlc $@
            ;;
        "next")
            execute_command vlc $@
            ;;
        "previous")
            execute_command vlc $@
            ;;
        "stop")
            msg="Stopped"
            ;;
        "vlc")
            exec 3<>/dev/tcp/localhost/${ports["vlc"]}

            ## send to socket
            shift
            echo $@ >&3

            ## read data from the socket
            read -r tmp <&3
            msg=$tmp
            ;;
        "bye")
            cleanup
            exit 0
            ;;
        "list")
            echo "LIST OF SONGS"
            cat $HOME/.assistant/songs
            echo $songs
            ;;
        "meaning")
            exec 3<>/dev/tcp/localhost/${ports["meaning"]}
            echo $@ >&3
            msg=$(cat<&3)
            ;;
        "download")
            exec 3<>/dev/tcp/localhost/${ports["song_download"]}
            echo $@ >&3
            msg=$(cat<&3)
            ;;
        "clear")
            clear >$(tty)
            msg=""
            ;;
        *)
            msg="Command not recognized"
            ;;
    esac
}

initialize

while true; do
    if [[ $msg != "" ]]; then
        echo -e $prompt"$msg"
    fi
    echo -n ">> "
    read -a command_args
    cmnd=${command_args[0]}
    args=${command_args[@]:1} # getting rest of the array
    execute_command $cmnd "$args"
done
