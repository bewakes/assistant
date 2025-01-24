#!/bin/bash
source "$ASSISTANT_DIR"/helpers.sh

TMP_DIR=/tmp/assistant
SERVICES_DIR=$TMP_DIR/services
LOCK_FILE=$TMP_DIR/assistant.lock
ASSISTANT_HOME=$HOME/.assistant

## TRAP AND CLEANUP
# TODO: This is probably not needed
cleanup() {
    echo -n 'Cleaning up...'
    # Now kill each services, which keep track of children themselves
    # each will kill itself and its children with SIGTERM signal
    for id in ${pids[@]}
    do
        kill $id 2> /dev/null
    done
    echo DONE
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

# list of enabled services
# looks into $ASSISTANT_HOME/enabled_services.list.
services=$(cat $ASSISTANT_HOME/enabled_services.list)

# ports where the processes listen for command
# declare -A ports

# process ids of the services spawned
# declare -A pids

################################
## END INITIALIZING VARIABLES ##
################################


assign_ports() {
    ##########################################
    ## Assign random ports to services.
    ## Ports are stored by 'ports' variable
    ##########################################
    # To store services and ports to file which can be used by services to communicate with each other
    for s in ${services[@]}
    do
        port=$((RANDOM%2048+4213)) # 4213 because vlc uses 4212. TODO: retry if already used port
        ports[$s]=$port
        echo $port > $SERVICES_DIR/$s
    done
}

initialize() {
    ###########################################
    ## This is the first function called. Here,
    ## services scripts are run by instructing
    ## them to listen on the ports assigned. 
    ## Each pid is stored in 'pids' variable.
    ###########################################

    # Make tmp services dir
    mkdir -p $SERVICES_DIR

    lock_content=$(head -n 1 $LOCK_FILE 2>/dev/null || echo "")
    if [ "$lock_content" = "initializing" ]; then
        echo Assistant instance is already initializing. Aborting.
        exit 1;
    elif [ "$lock_content" = "initialized" ]; then
        echo Assistant instance is already initialized. Aborting.
        exit 1;
    else
        echo initializing assistant
    fi
    echo -n "initializing" > $LOCK_FILE

    source ${ASSISTANT_DIR}/venv/bin/activate

    # to store data
    mkdir -p $ASSISTANT_HOME
    if [[ ! -f $ASSISTANT_HOME/songs ]]; then
        echo songs file not found
        touch $ASSISTANT_HOME/songs
    fi
    # store music here
    mkdir -p $ASSISTANT_HOME/Music/

    # first assign ports
    assign_ports

    # run all the processes/services, and store each pid
    for s in ${services[@]}
    do
        echo starting service $s
        # make each service run and listen to the port specified
        # NOTE: the first argument will be the assigned port number to listen
        python3 "$ASSISTANT_DIR"/services/$s.py ${ports[$s]} &

        pid=$! # storing corresponding pid
        echo $s $pid

        # add to map/hashtable
        echo $pid >> $SERVICES_DIR/$s
    done

    echo "initialized" > $LOCK_FILE
    echo "$1" >> $LOCK_FILE
    echo initialized. Now you can use 'assistant <cmd>'
}

while true; do
    sleep 100000;
done &

initialize $!
